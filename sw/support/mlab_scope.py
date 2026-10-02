"""mLabCuriosity Scope GUI — ADC channels via pyx2cscope."""

import sys
import time
from pathlib import Path

import numpy as np
from PyQt5.QtCore import Qt, QThread, QTimer, pyqtSignal
from PyQt5.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFileDialog,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QRadioButton,
    QSpinBox,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from pyx2cscope.x2cscope import X2CScope, TriggerConfig

# ---------------------------------------------------------------------------
DEFAULT_ELF = str(
    Path(r"C:\_data\github\mLabCuriosity\fw\mLabCuriosity\out\mLabCuriosity\default.elf")
)
BAUD_RATE = 460800
AUTOCONNECT_INTERVAL_MS = 2000

ADC_CHANNELS = [
    "mLabCuriosity.adc1",
    "mLabCuriosity.adc2",
    "mLabCuriosity.adc3",
    "mLabCuriosity.adc4",
]
CHANNEL_LABELS = ["adc1", "adc2", "adc3", "adc4"]
COLORS = ["#e74c3c", "#2ecc71", "#3498db", "#f39c12"]

PWM_COUNT = 4
PWM_DC_VARS  = [f"mLabCuriosity.pwm_dc{i}" for i in range(PWM_COUNT)]
PWM_F_VARS   = [f"mLabCuriosity.pwm_f{i}"  for i in range(PWM_COUNT)]
PWM_DC_DEFAULT = 1000
PWM_F_DEFAULT  = 20000

GPO_COUNT = 4
GPO_VARS   = [f"mLabCuriosity.dpo{i}" for i in range(GPO_COUNT)]
GPO_LABELS = ["DO0", "DO1", "DO2", "DO3"]

GPI_COUNT = 4
GPI_VARS   = [f"mLabCuriosity.dpi{i}" for i in range(GPI_COUNT)]
GPI_LABELS = ["DI0", "DI1", "DI2", "DI3"]
GPI_SW_VAR = "mLabCuriosity.SW0"

GPI_REFRESH_MS = 100


# ---------------------------------------------------------------------------
class ScopeWorker(QThread):
    data_ready = pyqtSignal(dict)
    error = pyqtSignal(str)
    done = pyqtSignal()  # fired once after a single-shot capture completes

    POLL_INTERVAL_S = 0.05  # 50 ms, matches pyx2cscope GUI polling cadence

    def __init__(self, x2c: X2CScope, single_shot: bool = False):
        super().__init__()
        self._x2c = x2c
        self._single_shot = single_shot
        self._running = False

    def run(self):
        self._running = True
        try:
            self._x2c.request_scope_data()  # kick off first capture
        except Exception as exc:
            self.error.emit(str(exc))
            return

        while self._running:
            try:
                if self._x2c.is_scope_data_ready():
                    data = self._x2c.get_scope_channel_data()
                    if data:
                        self.data_ready.emit(data)
                    if self._single_shot:
                        self._running = False
                        self.done.emit()
                        return
                    self._x2c.request_scope_data()  # arm for next capture
                time.sleep(self.POLL_INTERVAL_S)
            except Exception as exc:
                self.error.emit(str(exc))
                self._running = False

    def stop(self):
        self._running = False
        self.wait(3000)


# ---------------------------------------------------------------------------
class MLAbScopeWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("mLabCuriosity Scope")
        self.resize(1200, 820)

        self._x2c: X2CScope | None = None
        self._worker: ScopeWorker | None = None
        self._connected = False
        self._sampling = False
        self._vars: dict = {}
        self._pwm_vars: dict = {}
        self._gpo_vars: dict = {}
        self._gpi_vars: dict = {}
        self._detected_port = ""

        self._autoconnect_timer = QTimer(self)
        self._gpi_timer = QTimer(self)
        self._gpi_timer.timeout.connect(self._refresh_gpi)
        self._autoconnect_timer.timeout.connect(self._try_autoconnect)

        self._build_ui()
        self._build_plot()
        self._autoconnect_timer.start(AUTOCONNECT_INTERVAL_MS)

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------
    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setSpacing(6)

        # ---- Connection ----
        conn_box = QGroupBox("Connection")
        conn_layout = QHBoxLayout(conn_box)
        conn_layout.addWidget(QLabel("ELF:"))
        self._elf_edit = QLineEdit(DEFAULT_ELF)
        self._elf_edit.setMinimumWidth(380)
        conn_layout.addWidget(self._elf_edit)
        browse_btn = QPushButton("...")
        browse_btn.setFixedWidth(28)
        browse_btn.clicked.connect(self._browse_elf)
        conn_layout.addWidget(browse_btn)
        conn_layout.addWidget(QLabel(f"<i>{BAUD_RATE} baud · AUTO port</i>"))
        conn_layout.addStretch()
        self._connect_btn = QPushButton("Connect")
        self._connect_btn.setMinimumWidth(100)
        self._connect_btn.clicked.connect(self._on_connect_clicked)
        conn_layout.addWidget(self._connect_btn)
        root.addWidget(conn_box)

        # ---- Channels (placed as sidebar next to plot below) ----
        ch_box = QGroupBox("Channels")
        ch_grid = QGridLayout(ch_box)
        ch_grid.setSpacing(3)
        ch_grid.setContentsMargins(4, 4, 4, 4)
        for col, (hdr, tip) in enumerate([
            ("En",   "Enable channel"),
            ("Ch",   "Channel"),
            ("Gain", "Gain multiplier"),
            ("Off",  "Additive offset after gain"),
            ("Trig", "Trigger source"),
        ]):
            lbl = QLabel(f"<b>{hdr}</b>")
            lbl.setToolTip(tip)
            ch_grid.addWidget(lbl, 0, col, Qt.AlignCenter)

        self._ch_enable: list[QCheckBox] = []
        self._ch_gain: list[QDoubleSpinBox] = []
        self._ch_offset: list[QDoubleSpinBox] = []
        self._ch_trig: list[QRadioButton] = []

        for i, (label, color) in enumerate(zip(CHANNEL_LABELS, COLORS)):
            row = i + 1
            cb = QCheckBox()
            cb.setChecked(True)
            ch_grid.addWidget(cb, row, 0, Qt.AlignCenter)
            self._ch_enable.append(cb)

            ch_grid.addWidget(
                QLabel(f'<font color="{color}">\u25a0</font> {label}'), row, 1
            )

            gain = QDoubleSpinBox()
            gain.setRange(-1e6, 1e6)
            gain.setValue(1.0)
            gain.setDecimals(4)
            gain.setSingleStep(0.1)
            gain.setFixedWidth(80)
            gain.setToolTip("Gain multiplier")
            ch_grid.addWidget(gain, row, 2)
            self._ch_gain.append(gain)

            offset = QDoubleSpinBox()
            offset.setRange(-1e6, 1e6)
            offset.setValue(0.0)
            offset.setDecimals(2)
            offset.setSingleStep(1.0)
            offset.setFixedWidth(72)
            offset.setToolTip("Additive offset after gain")
            ch_grid.addWidget(offset, row, 3)
            self._ch_offset.append(offset)

            rb = QRadioButton()
            if i == 0:
                rb.setChecked(True)
            ch_grid.addWidget(rb, row, 4, Qt.AlignCenter)
            self._ch_trig.append(rb)

        self._ch_box = ch_box  # inserted into plot area below

        # ---- PWM control (placed in left sidebar below) ----
        pwm_box = QGroupBox("PWM Control")
        pwm_grid = QGridLayout(pwm_box)
        pwm_grid.setSpacing(4)
        pwm_grid.setContentsMargins(6, 4, 6, 4)
        for col, hdr in enumerate(["Ch", "Duty", "Period", "Set"]):
            pwm_grid.addWidget(QLabel(f"<b>{hdr}</b>"), 0, col)

        self._pwm_dc_sb: list[QSpinBox] = []
        self._pwm_f_sb: list[QSpinBox] = []
        self._pwm_set_btns: list[QPushButton] = []

        for i in range(PWM_COUNT):
            row = i + 1
            pwm_grid.addWidget(QLabel(f"PWM{i}"), row, 0)

            dc_sb = QSpinBox()
            dc_sb.setRange(0, 65535)
            dc_sb.setValue(PWM_DC_DEFAULT)
            dc_sb.setToolTip(f"PWM{i} duty cycle (0–65535)")
            dc_sb.setEnabled(False)
            dc_sb.setFixedWidth(68)
            pwm_grid.addWidget(dc_sb, row, 1)
            self._pwm_dc_sb.append(dc_sb)

            f_sb = QSpinBox()
            f_sb.setRange(1, 65535)
            f_sb.setValue(PWM_F_DEFAULT)
            f_sb.setToolTip(f"PWM{i} period (1–65535)")
            f_sb.setEnabled(False)
            f_sb.setFixedWidth(68)
            pwm_grid.addWidget(f_sb, row, 2)
            self._pwm_f_sb.append(f_sb)

            set_btn = QPushButton("Set")
            set_btn.setFixedWidth(38)
            set_btn.setEnabled(False)
            set_btn.clicked.connect(lambda _=False, idx=i: self._write_pwm(idx))
            pwm_grid.addWidget(set_btn, row, 3)
            self._pwm_set_btns.append(set_btn)

        self._pwm_box = pwm_box  # inserted into left sidebar below

        # ---- Digital I/O (placed in left sidebar below) ----
        dio_box = QGroupBox("Digital I/O")
        dio_layout = QVBoxLayout(dio_box)
        dio_layout.setSpacing(4)
        dio_layout.setContentsMargins(4, 4, 4, 4)

        gpo_box = QGroupBox("GPO (write)")
        gpo_grid = QGridLayout(gpo_box)
        self._gpo_cbs: list[QCheckBox] = []
        for i, label in enumerate(GPO_LABELS):
            gpo_grid.addWidget(QLabel(f"<b>{label}</b>"), 0, i, Qt.AlignCenter)
            cb = QCheckBox()
            cb.setEnabled(False)
            cb.stateChanged.connect(lambda state, idx=i: self._write_gpo(idx, state))
            gpo_grid.addWidget(cb, 1, i, Qt.AlignCenter)
            self._gpo_cbs.append(cb)
        dio_layout.addWidget(gpo_box)

        gpi_box = QGroupBox("GPI (read)")
        gpi_grid = QGridLayout(gpi_box)
        self._gpi_value_labels: list[QLabel] = []
        for i, label in enumerate(GPI_LABELS):
            gpi_grid.addWidget(QLabel(f"<b>{label}</b>"), 0, i, Qt.AlignCenter)
            lbl = QLabel("—")
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setMinimumWidth(32)
            gpi_grid.addWidget(lbl, 1, i, Qt.AlignCenter)
            self._gpi_value_labels.append(lbl)
        gpi_grid.addWidget(QLabel("<b>SW0</b>"), 0, GPI_COUNT, Qt.AlignCenter)
        self._gpi_sw_label = QLabel("—")
        self._gpi_sw_label.setAlignment(Qt.AlignCenter)
        self._gpi_sw_label.setMinimumWidth(32)
        gpi_grid.addWidget(self._gpi_sw_label, 1, GPI_COUNT, Qt.AlignCenter)
        dio_layout.addWidget(gpi_box)

        self._dio_box = dio_box  # inserted into left sidebar below

        # ---- Scope settings ----
        scope_box = QGroupBox("Scope Settings")
        scope_layout = QHBoxLayout(scope_box)

        scope_layout.addWidget(QLabel("Sample time:"))
        self._sample_time_sb = QSpinBox()
        self._sample_time_sb.setRange(1, 1000)
        self._sample_time_sb.setValue(1)
        self._sample_time_sb.setToolTip("Decimation: 1 = every sample, 2 = every 2nd, …")
        scope_layout.addWidget(self._sample_time_sb)

        scope_layout.addSpacing(16)
        scope_layout.addWidget(QLabel("Trig level:"))
        self._trig_level_sb = QDoubleSpinBox()
        self._trig_level_sb.setRange(-32768, 32767)
        self._trig_level_sb.setValue(0)
        self._trig_level_sb.setDecimals(0)
        scope_layout.addWidget(self._trig_level_sb)

        scope_layout.addWidget(QLabel("Edge:"))
        self._trig_edge_combo = QComboBox()
        self._trig_edge_combo.addItems(["Falling", "Rising"])
        self._trig_edge_combo.setCurrentIndex(1)
        scope_layout.addWidget(self._trig_edge_combo)

        scope_layout.addWidget(QLabel("Mode:"))
        self._trig_mode_combo = QComboBox()
        self._trig_mode_combo.addItems(["Auto", "Triggered"])
        self._trig_mode_combo.setCurrentIndex(0)
        scope_layout.addWidget(self._trig_mode_combo)

        scope_layout.addWidget(QLabel("Delay %:"))
        self._trig_delay_sb = QSpinBox()
        self._trig_delay_sb.setRange(0, 100)
        self._trig_delay_sb.setValue(0)
        scope_layout.addWidget(self._trig_delay_sb)

        scope_layout.addSpacing(16)
        self._apply_btn = QPushButton("Apply")
        self._apply_btn.setEnabled(False)
        self._apply_btn.setToolTip("Push trigger/sample settings to running scope")
        self._apply_btn.clicked.connect(self._apply_scope_settings)
        scope_layout.addWidget(self._apply_btn)

        scope_layout.addSpacing(16)
        self._single_shot_cb = QCheckBox("Single shot")
        self._single_shot_cb.setToolTip("Capture one buffer then stop automatically")
        scope_layout.addWidget(self._single_shot_cb)

        scope_layout.addSpacing(8)
        self._sample_btn = QPushButton("Sample")
        self._sample_btn.setMinimumWidth(90)
        self._sample_btn.setEnabled(False)
        self._sample_btn.clicked.connect(self._on_sample_clicked)
        scope_layout.addWidget(self._sample_btn)

        scope_layout.addStretch()
        self._scope_box = scope_box  # inserted below plot in main area

        # ---- main area: left sidebar (channels + PWM + DIO) + plot ----
        main_area = QWidget()
        main_h = QHBoxLayout(main_area)
        main_h.setContentsMargins(0, 0, 0, 0)
        main_h.setSpacing(4)

        sidebar = QWidget()
        sidebar_vbox = QVBoxLayout(sidebar)
        sidebar_vbox.setContentsMargins(0, 0, 0, 0)
        sidebar_vbox.setSpacing(4)
        sidebar_vbox.addWidget(self._ch_box)
        sidebar_vbox.addWidget(self._pwm_box)
        sidebar_vbox.addWidget(self._dio_box)
        sidebar_vbox.addStretch()
        main_h.addWidget(sidebar)

        right_side = QWidget()
        right_vbox = QVBoxLayout(right_side)
        right_vbox.setContentsMargins(0, 0, 0, 0)
        right_vbox.setSpacing(4)
        self._plot_placeholder = QVBoxLayout()
        _plot_container = QWidget()
        _plot_container.setLayout(self._plot_placeholder)
        right_vbox.addWidget(_plot_container, stretch=1)
        right_vbox.addWidget(self._scope_box)
        main_h.addWidget(right_side, stretch=1)
        root.addWidget(main_area, stretch=1)

        # ---- status bar ----
        self._status = QStatusBar()
        self.setStatusBar(self._status)
        self._set_status("Ready — not connected", ok=None)

    def _build_plot(self):
        self._plot_widget = pg.PlotWidget()
        self._plot_placeholder.addWidget(self._plot_widget)

        self._plot = self._plot_widget.getPlotItem()
        self._plot.setTitle("ADC Channels")
        self._plot.showGrid(x=True, y=True, alpha=0.3)
        self._plot.setLabel("left", "Value")
        self._plot.setLabel("bottom", "Time (ms)")
        self._plot.addLegend(offset=(10, 10))

        self._curves = []
        for label, color in zip(CHANNEL_LABELS, COLORS):
            pen = pg.mkPen(color=color, width=2)
            self._curves.append(self._plot.plot(pen=pen, name=label))

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _browse_elf(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select ELF file", str(Path(self._elf_edit.text()).parent),
            "ELF files (*.elf);;All files (*)",
        )
        if path:
            self._elf_edit.setText(path)

    def _set_status(self, msg: str, ok=True):
        self._status.showMessage(msg)
        color = {"True": "#2ecc71", "False": "#e74c3c", "None": "#cdd6f4"}[str(ok)]
        self._status.setStyleSheet(f"color: {color};")

    def _update_buttons(self):
        self._elf_edit.setEnabled(not self._connected)
        self._connect_btn.setText("Disconnect" if self._connected else "Connect")
        self._sample_btn.setEnabled(self._connected)
        self._sample_btn.setText("Stop" if self._sampling else "Sample")
        self._apply_btn.setEnabled(self._connected and self._sampling)
        for sb in self._pwm_dc_sb + self._pwm_f_sb:
            sb.setEnabled(self._connected)
        for btn in self._pwm_set_btns:
            btn.setEnabled(self._connected)
        for cb in self._gpo_cbs:
            cb.setEnabled(self._connected)

    # ------------------------------------------------------------------
    # Connection — only establishes serial link, no scope setup
    # ------------------------------------------------------------------
    def _on_connect_clicked(self):
        if self._connected:
            self._disconnect()
        else:
            self._set_status("Connecting…", ok=None)
            QApplication.processEvents()
            self._connect()

    def _connect(self, port: str | None = None):
        elf = self._elf_edit.text().strip()
        try:
            kwargs: dict = {"elf_file": elf if elf else None, "baud_rate": BAUD_RATE}
            if port:
                kwargs["port"] = port
            self._x2c = X2CScope(**kwargs)
        except Exception as exc:
            self._set_status(f"Connection failed: {exc}", ok=False)
            self._x2c = None
            return

        self._detected_port = getattr(self._x2c.interface, "com_port", port or "AUTO")
        self._connected = True
        self._update_buttons()
        self._load_pwm_vars()
        self._load_gpio_vars()
        self._gpi_timer.start(GPI_REFRESH_MS)
        self._set_status(
            f"Connected — {self._detected_port} @ {BAUD_RATE}  · click Sample to start",
            ok=True,
        )

    def _disconnect(self):
        self._gpi_timer.stop()
        self._stop_sampling()
        if self._x2c:
            try:
                self._x2c.clear_all_scope_channel()
                self._x2c.disconnect()
            except Exception:
                pass
            self._x2c = None
        self._vars = {}
        self._pwm_vars = {}
        self._gpo_vars = {}
        self._gpi_vars = {}
        for lbl in self._gpi_value_labels:
            lbl.setText("—")
        self._gpi_sw_label.setText("—")
        self._connected = False
        self._update_buttons()
        self._set_status("Disconnected", ok=None)

    # ------------------------------------------------------------------
    # Sampling
    # ------------------------------------------------------------------
    def _on_sample_clicked(self):
        if self._sampling:
            self._stop_sampling()
        else:
            self._start_sampling(single_shot=self._single_shot_cb.isChecked())

    def _start_sampling(self, single_shot: bool = False):
        if not self._connected or self._x2c is None:
            return
        try:
            self._x2c.clear_all_scope_channel()
            self._vars = {}
            enabled = [
                (i, name) for i, name in enumerate(ADC_CHANNELS)
                if self._ch_enable[i].isChecked()
            ]
            if not enabled:
                self._set_status("No channels enabled — check channel enable boxes", ok=False)
                return
            for i, name in enabled:
                var = self._x2c.get_variable(name)
                if var is None:
                    avail = [v for v in self._x2c.list_variables() if "adc" in v.lower()]
                    self._set_status(
                        f"Variable '{name}' not found. ADC vars in ELF: {avail[:6]}",
                        ok=False,
                    )
                    return
                self._vars[name] = var
                self._x2c.add_scope_channel(var)
            self._apply_scope_settings()
        except Exception as exc:
            self._set_status(f"Scope setup failed: {exc}", ok=False)
            return

        self._worker = ScopeWorker(self._x2c, single_shot=single_shot)
        self._worker.data_ready.connect(self._on_scope_data)
        self._worker.error.connect(self._on_worker_error)
        self._worker.done.connect(self._on_single_shot_done)
        self._worker.start()
        self._sampling = True
        self._update_buttons()
        mode = "Single shot" if single_shot else "Sampling"
        self._set_status(f"{mode} — {self._detected_port} @ {BAUD_RATE}", ok=True)

    def _stop_sampling(self):
        if self._worker:
            self._worker.stop()
            self._worker = None
        self._sampling = False
        self._update_buttons()
        if self._connected:
            self._set_status(
                f"Stopped — {self._detected_port} @ {BAUD_RATE}", ok=None
            )

    def _on_single_shot_done(self):
        if self._worker:
            self._worker.wait(500)
        self._worker = None
        self._sampling = False
        self._update_buttons()
        self._set_status(
            f"Single shot complete — {self._detected_port} @ {BAUD_RATE}", ok=True
        )

    # ------------------------------------------------------------------
    # PWM control
    # ------------------------------------------------------------------
    def _load_pwm_vars(self):
        """Fetch PWM Variable objects and read current MCU values into spinboxes."""
        self._pwm_vars = {}
        for i in range(PWM_COUNT):
            for name, sb in [
                (PWM_DC_VARS[i], self._pwm_dc_sb[i]),
                (PWM_F_VARS[i],  self._pwm_f_sb[i]),
            ]:
                var = self._x2c.get_variable(name)
                if var is not None:
                    self._pwm_vars[name] = var
                    try:
                        val = var.get_value()
                        if val is not None:
                            sb.setValue(int(val))
                    except Exception:
                        pass

    def _write_pwm(self, channel: int):
        """Write duty cycle and period for one PWM channel to the MCU."""
        if not self._connected:
            return
        errors = []
        for name, sb in [
            (PWM_DC_VARS[channel], self._pwm_dc_sb[channel]),
            (PWM_F_VARS[channel],  self._pwm_f_sb[channel]),
        ]:
            var = self._pwm_vars.get(name)
            if var is None:
                errors.append(f"{name} not found")
                continue
            try:
                var.set_value(sb.value())
            except Exception as exc:
                errors.append(f"{name}: {exc}")
        if errors:
            self._set_status(f"PWM write error: {'; '.join(errors)}", ok=False)
        else:
            self._set_status(
                f"PWM{channel} set — dc={self._pwm_dc_sb[channel].value()} "
                f"period={self._pwm_f_sb[channel].value()}",
                ok=True,
            )

    # ------------------------------------------------------------------
    # GPIO control
    # ------------------------------------------------------------------
    def _load_gpio_vars(self):
        """Fetch GPO/GPI Variable objects and read initial GPO state into checkboxes."""
        self._gpo_vars = {}
        for i, name in enumerate(GPO_VARS):
            var = self._x2c.get_variable(name)
            if var is not None:
                self._gpo_vars[name] = var
                try:
                    val = var.get_value()
                    if val is not None:
                        cb = self._gpo_cbs[i]
                        cb.blockSignals(True)
                        cb.setChecked(bool(val))
                        cb.blockSignals(False)
                except Exception:
                    pass

        self._gpi_vars = {}
        for name in GPI_VARS + [GPI_SW_VAR]:
            var = self._x2c.get_variable(name)
            if var is not None:
                self._gpi_vars[name] = var

    def _write_gpo(self, channel: int, state: int):
        """Write one GPO output to MCU."""
        if not self._connected:
            return
        name = GPO_VARS[channel]
        var = self._gpo_vars.get(name)
        if var is None:
            self._set_status(f"{name} not found", ok=False)
            return
        try:
            var.set_value(1 if state else 0)
            self._set_status(
                f"{GPO_LABELS[channel]} = {'1' if state else '0'}", ok=True
            )
        except Exception as exc:
            self._set_status(f"GPO write error: {exc}", ok=False)

    def _refresh_gpi(self):
        """Poll GPI values from MCU and update display labels."""
        if not self._connected or self._x2c is None:
            return
        for i, name in enumerate(GPI_VARS):
            var = self._gpi_vars.get(name)
            if var is None:
                continue
            try:
                val = var.get_value()
                self._gpi_value_labels[i].setText("1" if val else "0")
            except Exception:
                pass
        sw_var = self._gpi_vars.get(GPI_SW_VAR)
        if sw_var is not None:
            try:
                val = sw_var.get_value()
                self._gpi_sw_label.setText("1" if val else "0")
            except Exception:
                pass

    # ------------------------------------------------------------------
    # Scope settings
    # ------------------------------------------------------------------
    def _apply_scope_settings(self):
        if self._x2c is None:
            return
        self._x2c.set_sample_time(self._sample_time_sb.value())
        mode = self._trig_mode_combo.currentIndex()  # 0=Auto, 1=Triggered
        if mode == 0:
            # Auto: no trigger condition — reset clears any previous trigger config
            self._x2c.reset_scope_trigger()
        else:
            trig_idx = next(
                (i for i, rb in enumerate(self._ch_trig) if rb.isChecked()), 0
            )
            trig_var = self._vars.get(ADC_CHANNELS[trig_idx])
            if trig_var is not None:
                config = TriggerConfig(
                    variable=trig_var,
                    trigger_level=self._trig_level_sb.value(),
                    trigger_mode=1,
                    trigger_delay=self._trig_delay_sb.value(),
                    trigger_edge=self._trig_edge_combo.currentIndex(),  # 0=Falling 1=Rising
                )
                self._x2c.set_scope_trigger(config)

    # ------------------------------------------------------------------
    # Auto-connect
    # ------------------------------------------------------------------
    def _try_autoconnect(self):
        if self._connected:
            return
        self._set_status("Auto-connect: scanning for LNet device…", ok=None)
        QApplication.processEvents()
        self._connect()
        if self._connected:
            self._autoconnect_timer.stop()

    # ------------------------------------------------------------------
    # Data
    # ------------------------------------------------------------------
    def _on_scope_data(self, data: dict):
        for i, name in enumerate(ADC_CHANNELS):
            if not self._ch_enable[i].isChecked():
                self._curves[i].setData([], [])
                continue
            # pyx2cscope key may be full name or short name depending on version
            ch_data = data.get(name) or data.get(CHANNEL_LABELS[i])
            if not ch_data:
                continue
            gain = self._ch_gain[i].value()
            offset = self._ch_offset[i].value()
            y = np.array(ch_data, dtype=float) * gain + offset
            dt_ms = self._sample_time_sb.value() * 0.005  # sample_time × 5 µs → ms
            t = np.arange(len(y)) * dt_ms
            self._curves[i].setData(t, y)

    def _on_worker_error(self, msg: str):
        self._set_status(f"Scope error: {msg}", ok=False)
        self._stop_sampling()

    # ------------------------------------------------------------------
    def closeEvent(self, event):
        self._autoconnect_timer.stop()
        self._gpi_timer.stop()
        self._disconnect()
        super().closeEvent(event)


# ---------------------------------------------------------------------------
def main():
    global pg
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    import pyqtgraph as pg  # delayed: requires QApplication to exist first
    pg.setConfigOptions(antialias=True, background="#1e1e2e", foreground="#cdd6f4")
    win = MLAbScopeWindow()
    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
