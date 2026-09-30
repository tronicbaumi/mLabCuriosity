"""mLabCuriosity Scope GUI — real-time plot of ADC channels via X2CScope/LNet."""

import sys
import time
import collections
from pathlib import Path

import numpy as np
import pyqtgraph as pg
import serial.tools.list_ports
from PyQt5.QtCore import Qt, QThread, QTimer, pyqtSignal
from PyQt5.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from pyx2cscope.x2cscope import X2CScope

# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------
DEFAULT_ELF = str(
    Path(r"C:\_data\github\mLabCuriosity\fw\mLabCuriosity\out\mLabCuriosity\default.elf")
)
DEFAULT_BAUD = "115200"
PLOT_BUFFER = 500          # samples kept in the rolling window
POLL_INTERVAL_MS = 50      # UI timer period (20 Hz)
AUTOCONNECT_INTERVAL_MS = 2000

ADC_CHANNELS = ["mLabCuriosity.adc1", "mLabCuriosity.adc2",
                 "mLabCuriosity.adc3", "mLabCuriosity.adc4"]
COLORS = ["#e74c3c", "#2ecc71", "#3498db", "#f39c12"]


# ---------------------------------------------------------------------------
# Background worker — keeps serial I/O off the GUI thread
# ---------------------------------------------------------------------------
class ScopeWorker(QThread):
    values_ready = pyqtSignal(list)   # [v1, v2, v3, v4]
    error = pyqtSignal(str)

    def __init__(self, x2c: X2CScope):
        super().__init__()
        self._x2c = x2c
        self._vars = []
        self._running = False

    def setup_variables(self):
        self._vars = [self._x2c.get_variable(ch) for ch in ADC_CHANNELS]

    def run(self):
        self._running = True
        while self._running:
            try:
                vals = [int(v.get_value()) for v in self._vars]
                self.values_ready.emit(vals)
            except Exception as exc:
                self.error.emit(str(exc))
                self._running = False
                break
            time.sleep(POLL_INTERVAL_MS / 1000.0)

    def stop(self):
        self._running = False
        self.wait(2000)


# ---------------------------------------------------------------------------
# Main window
# ---------------------------------------------------------------------------
class MLAbScopeWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("mLabCuriosity Scope")
        self.resize(1100, 700)

        self._x2c: X2CScope | None = None
        self._worker: ScopeWorker | None = None
        self._connected = False
        self._buffers = [collections.deque([0.0] * PLOT_BUFFER, maxlen=PLOT_BUFFER)
                         for _ in ADC_CHANNELS]

        self._autoconnect_timer = QTimer(self)
        self._autoconnect_timer.timeout.connect(self._try_autoconnect)

        self._build_ui()
        self._build_plot()
        self._refresh_ports()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------
    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setSpacing(6)

        # ---- config group ----
        cfg_box = QGroupBox("Connection")
        cfg_layout = QHBoxLayout(cfg_box)

        cfg_layout.addWidget(QLabel("Port:"))
        self._port_combo = QComboBox()
        self._port_combo.setMinimumWidth(100)
        cfg_layout.addWidget(self._port_combo)

        refresh_btn = QPushButton("⟳")
        refresh_btn.setFixedWidth(28)
        refresh_btn.setToolTip("Refresh port list")
        refresh_btn.clicked.connect(self._refresh_ports)
        cfg_layout.addWidget(refresh_btn)

        cfg_layout.addWidget(QLabel("Baud:"))
        self._baud_combo = QComboBox()
        for b in ["9600", "19200", "38400", "57600", "115200", "230400"]:
            self._baud_combo.addItem(b)
        self._baud_combo.setCurrentText(DEFAULT_BAUD)
        self._baud_combo.setMinimumWidth(90)
        cfg_layout.addWidget(self._baud_combo)

        cfg_layout.addWidget(QLabel("ELF:"))
        self._elf_edit = QLineEdit(DEFAULT_ELF)
        self._elf_edit.setMinimumWidth(320)
        cfg_layout.addWidget(self._elf_edit)

        elf_browse = QPushButton("...")
        elf_browse.setFixedWidth(28)
        elf_browse.clicked.connect(self._browse_elf)
        cfg_layout.addWidget(elf_browse)

        cfg_layout.addSpacing(12)
        self._autoconnect_cb = QCheckBox("Auto-connect")
        self._autoconnect_cb.setChecked(True)
        self._autoconnect_cb.stateChanged.connect(self._on_autoconnect_toggle)
        cfg_layout.addWidget(self._autoconnect_cb)

        cfg_layout.addSpacing(12)
        self._connect_btn = QPushButton("Connect")
        self._connect_btn.setMinimumWidth(90)
        self._connect_btn.clicked.connect(self._on_connect_clicked)
        cfg_layout.addWidget(self._connect_btn)

        cfg_layout.addStretch()
        root.addWidget(cfg_box)

        # ---- plot placeholder (filled in _build_plot) ----
        self._plot_placeholder = QVBoxLayout()
        root.addLayout(self._plot_placeholder, stretch=1)

        # ---- status bar ----
        self._status = QStatusBar()
        self.setStatusBar(self._status)
        self._set_status("Ready — not connected", ok=None)

        # start autoconnect if checked
        if self._autoconnect_cb.isChecked():
            self._autoconnect_timer.start(AUTOCONNECT_INTERVAL_MS)

    def _build_plot(self):
        pg.setConfigOptions(antialias=True, background="#1e1e2e", foreground="#cdd6f4")
        self._plot_widget = pg.GraphicsLayoutWidget()
        self._plot_placeholder.addWidget(self._plot_widget)

        self._plot = self._plot_widget.addPlot(title="ADC Channels")
        self._plot.showGrid(x=True, y=True, alpha=0.3)
        self._plot.setLabel("left", "ADC value (12-bit)")
        self._plot.setLabel("bottom", "Sample")
        self._plot.setYRange(0, 4095, padding=0.02)
        self._plot.addLegend(offset=(10, 10))

        self._curves = []
        for i, ch in enumerate(ADC_CHANNELS):
            short = ch.split(".")[-1]
            pen = pg.mkPen(color=COLORS[i], width=2)
            curve = self._plot.plot(pen=pen, name=short)
            self._curves.append(curve)

        self._x_data = np.arange(PLOT_BUFFER)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _refresh_ports(self):
        current = self._port_combo.currentText()
        self._port_combo.blockSignals(True)
        self._port_combo.clear()
        ports = [p.device for p in serial.tools.list_ports.comports()]
        for p in ports:
            self._port_combo.addItem(p)
        if current in ports:
            self._port_combo.setCurrentText(current)
        self._port_combo.blockSignals(False)

    def _browse_elf(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select ELF file", str(Path(self._elf_edit.text()).parent),
            "ELF files (*.elf);;All files (*)"
        )
        if path:
            self._elf_edit.setText(path)

    def _set_status(self, msg: str, ok=True):
        self._status.showMessage(msg)
        color = {"True": "#2ecc71", "False": "#e74c3c", "None": "#cdd6f4"}[str(ok)]
        self._status.setStyleSheet(f"color: {color};")

    # ------------------------------------------------------------------
    # Connection logic
    # ------------------------------------------------------------------
    def _on_connect_clicked(self):
        if self._connected:
            self._disconnect()
        else:
            self._connect(self._port_combo.currentText())

    def _connect(self, port: str):
        if not port:
            self._set_status("No COM port selected", ok=False)
            return
        elf = self._elf_edit.text().strip()
        baud = int(self._baud_combo.currentText())
        try:
            self._x2c = X2CScope(port=port, baud_rate=baud,
                                  elf_file=elf if elf else None)
            self._x2c.connect()
        except Exception as exc:
            self._set_status(f"Connection failed: {exc}", ok=False)
            self._x2c = None
            return

        try:
            self._worker = ScopeWorker(self._x2c)
            self._worker.setup_variables()
            self._worker.values_ready.connect(self._on_values)
            self._worker.error.connect(self._on_worker_error)
            self._worker.start()
        except Exception as exc:
            self._set_status(f"Variable setup failed: {exc}", ok=False)
            try:
                self._x2c.disconnect()
            except Exception:
                pass
            self._x2c = None
            return

        self._connected = True
        self._connect_btn.setText("Disconnect")
        self._port_combo.setEnabled(False)
        self._baud_combo.setEnabled(False)
        self._elf_edit.setEnabled(False)
        self._set_status(f"Connected — {port} @ {baud}", ok=True)

    def _disconnect(self):
        if self._worker:
            self._worker.stop()
            self._worker = None
        if self._x2c:
            try:
                self._x2c.disconnect()
            except Exception:
                pass
            self._x2c = None
        self._connected = False
        self._connect_btn.setText("Connect")
        self._port_combo.setEnabled(True)
        self._baud_combo.setEnabled(True)
        self._elf_edit.setEnabled(True)
        self._set_status("Disconnected", ok=None)

    # ------------------------------------------------------------------
    # Auto-connect
    # ------------------------------------------------------------------
    def _on_autoconnect_toggle(self, state):
        if state == Qt.Checked:
            self._autoconnect_timer.start(AUTOCONNECT_INTERVAL_MS)
        else:
            self._autoconnect_timer.stop()

    def _try_autoconnect(self):
        if self._connected:
            return
        self._refresh_ports()
        ports = [self._port_combo.itemText(i)
                 for i in range(self._port_combo.count())]
        if not ports:
            self._set_status("Auto-connect: no ports found", ok=None)
            return
        for port in ports:
            self._set_status(f"Auto-connect: trying {port}…", ok=None)
            QApplication.processEvents()
            self._connect(port)
            if self._connected:
                self._autoconnect_timer.stop()
                return
        self._set_status("Auto-connect: no device responded", ok=False)

    # ------------------------------------------------------------------
    # Data reception
    # ------------------------------------------------------------------
    def _on_values(self, vals: list):
        for i, v in enumerate(vals):
            self._buffers[i].append(float(v))
        for i, curve in enumerate(self._curves):
            curve.setData(self._x_data, np.array(self._buffers[i]))

    def _on_worker_error(self, msg: str):
        self._set_status(f"Error: {msg}", ok=False)
        self._disconnect()

    # ------------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------------
    def closeEvent(self, event):
        self._autoconnect_timer.stop()
        self._disconnect()
        super().closeEvent(event)


# ---------------------------------------------------------------------------
def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = MLAbScopeWindow()
    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
