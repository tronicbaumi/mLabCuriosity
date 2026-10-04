"""mLabCuriosity Scope GUI — ADC channels via pyx2cscope."""

import json
import sys
import threading
import time
from pathlib import Path

import numpy as np
from PyQt5.QtCore import Qt, QThread, QTimer, QUrl, pyqtSignal
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
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QRadioButton,
    QSpinBox,
    QSplitter,
    QStatusBar,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from pyx2cscope.x2cscope import X2CScope, TriggerConfig

# Must be imported before QApplication exists. Optional: without PyQtWebEngine
# the Blockly tab just shows an install hint.
try:
    from PyQt5.QtWebEngineWidgets import QWebEngineView
    _WEBENGINE_ERROR = ""
except ImportError as _exc:
    QWebEngineView = None
    _WEBENGINE_ERROR = str(_exc)

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

ADC_VREF = 3.3
ADC_FULL_SCALE = 4095

# Blockly assets: sw/support/blockly when run from source, <bundle>/blockly in the exe
_BASE_DIR = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
BLOCKLY_DIR = _BASE_DIR / "blockly"
BLOCKLY_HIGHLIGHT_MIN_S = 0.05  # throttle block highlighting to ~20 Hz


# ---------------------------------------------------------------------------
class ScopeWorker(QThread):
    data_ready = pyqtSignal(dict)
    error = pyqtSignal(str)
    done = pyqtSignal()  # fired once after a single-shot capture completes

    POLL_INTERVAL_S = 0.05  # 50 ms, matches pyx2cscope GUI polling cadence

    def __init__(self, x2c: X2CScope, lock: threading.RLock, single_shot: bool = False):
        super().__init__()
        self._x2c = x2c
        self._lock = lock
        self._single_shot = single_shot
        self._running = False

    def run(self):
        self._running = True
        try:
            with self._lock:
                self._x2c.request_scope_data()  # kick off first capture
        except Exception as exc:
            self.error.emit(str(exc))
            return

        while self._running:
            try:
                with self._lock:
                    ready = self._x2c.is_scope_data_ready()
                    data = self._x2c.get_scope_channel_data() if ready else None
                if ready:
                    if data:
                        self.data_ready.emit(data)
                    if self._single_shot:
                        self._running = False
                        self.done.emit()
                        return
                    with self._lock:
                        self._x2c.request_scope_data()  # arm for next capture
                time.sleep(self.POLL_INTERVAL_S)
            except Exception as exc:
                self.error.emit(str(exc))
                self._running = False

    def stop(self):
        self._running = False
        self.wait(3000)


# ---------------------------------------------------------------------------
class ScriptStopped(Exception):
    """Raised inside a running Blockly script when Stop is pressed."""


class BlocklyHAL:
    """The `mlab` object generated Blockly code calls (see blockly/mlab_blocks.js).

    Maps blocks onto the same X2Cscope variables the Main tab uses.
    Runs in the BlocklyWorker thread; every X2Cscope access takes the shared lock.
    """

    def __init__(self, x2c: X2CScope, lock: threading.RLock, stop_event: threading.Event):
        self._x2c = x2c
        self._lock = lock
        self._stop = stop_event
        self._vars: dict = {}
        self._t0 = time.monotonic()

    # ---- plumbing ----
    def check_stop(self):
        if self._stop.is_set():
            raise ScriptStopped()

    def _sleep(self, seconds: float):
        end = time.monotonic() + seconds
        while True:
            self.check_stop()
            remaining = end - time.monotonic()
            if remaining <= 0:
                return
            time.sleep(min(remaining, 0.02))

    def _var(self, name: str):
        var = self._vars.get(name)
        if var is None:
            with self._lock:
                var = self._x2c.get_variable(name)
            if var is None:
                raise RuntimeError(f"Variable '{name}' not found in ELF")
            self._vars[name] = var
        return var

    def _read(self, name: str):
        self.check_stop()
        var = self._var(name)
        with self._lock:
            val = var.get_value()
        return 0 if val is None else val

    def _write(self, name: str, value):
        self.check_stop()
        var = self._var(name)
        with self._lock:
            var.set_value(value)

    @staticmethod
    def _u16(value, low: int = 0) -> int:
        return max(low, min(65535, int(round(float(value)))))

    # ---- digital outputs ----
    def set_do(self, ch, value):
        self._write(GPO_VARS[int(ch)], 1 if value else 0)

    def get_do(self, ch) -> bool:
        return bool(self._read(GPO_VARS[int(ch)]))

    def toggle_do(self, ch):
        self.set_do(ch, not self.get_do(ch))

    # ---- digital inputs ----
    def get_di(self, ch) -> bool:
        name = GPI_SW_VAR if ch == "SW0" else GPI_VARS[int(ch)]
        return bool(self._read(name))

    def wait_di(self, ch, level):
        while self.get_di(ch) != bool(level):
            self._sleep(0.02)

    # ---- PWM ----
    def set_pwm_duty(self, ch, value):
        self._write(PWM_DC_VARS[int(ch)], self._u16(value, 0))

    def set_pwm_period(self, ch, value):
        self._write(PWM_F_VARS[int(ch)], self._u16(value, 1))

    def set_pwm_duty_pct(self, ch, percent):
        pct = max(0.0, min(100.0, float(percent)))
        self.set_pwm_duty(ch, self.get_pwm_period(ch) * pct / 100.0)

    def get_pwm_duty(self, ch) -> int:
        return int(self._read(PWM_DC_VARS[int(ch)]))

    def get_pwm_period(self, ch) -> int:
        return int(self._read(PWM_F_VARS[int(ch)]))

    # ---- ADC ----
    def read_adc(self, ch) -> int:
        return int(self._read(f"mLabCuriosity.adc{int(ch)}"))

    def read_adc_volts(self, ch) -> float:
        return self.read_adc(ch) * ADC_VREF / ADC_FULL_SCALE

    # ---- time ----
    def wait_ms(self, ms):
        self._sleep(max(0.0, float(ms)) / 1000.0)

    def millis(self) -> int:
        return int((time.monotonic() - self._t0) * 1000)


class BlocklyWorker(QThread):
    """Executes Python generated from the Blockly workspace."""

    log = pyqtSignal(str)
    highlight = pyqtSignal(str)

    def __init__(self, code: str, hal: BlocklyHAL):
        super().__init__()
        self._code = code
        self._hal = hal

    def run(self):
        last = {"t": 0.0, "id": None}

        def highlight(block_id):
            self._hal.check_stop()
            now = time.monotonic()
            if block_id != last["id"] and now - last["t"] >= BLOCKLY_HIGHLIGHT_MIN_S:
                last["t"], last["id"] = now, block_id
                self.highlight.emit(block_id)

        def _print(*args, **_kwargs):
            self.log.emit(" ".join(str(a) for a in args))

        env = {
            "__name__": "__blockly__",
            "mlab": self._hal,
            "check_stop": self._hal.check_stop,
            "highlight": highlight,
            "print": _print,
        }
        self.log.emit("Script started.")
        try:
            exec(compile(self._code, "<blockly>", "exec"), env)
            self.log.emit("Script finished.")
        except ScriptStopped:
            self.log.emit("Script stopped.")
        except Exception as exc:
            self.log.emit(f"Error: {type(exc).__name__}: {exc}")
        finally:
            self.highlight.emit("")


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
        self._last_config_path = ""
        # Serialises X2Cscope access between GUI, scope worker and Blockly worker
        self._x2c_lock = threading.RLock()

        self._blockly_view = None
        self._blockly_worker: BlocklyWorker | None = None
        self._blockly_stop_event: threading.Event | None = None
        self._blockly_last_path = ""

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
        self._tabs = QTabWidget()
        self.setCentralWidget(self._tabs)

        main_tab = QWidget()
        self._tabs.addTab(main_tab, "Main")
        root = QVBoxLayout(main_tab)
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
        load_cfg_btn = QPushButton("Load Config")
        load_cfg_btn.clicked.connect(self._load_config)
        conn_layout.addWidget(load_cfg_btn)
        save_cfg_btn = QPushButton("Save Config")
        save_cfg_btn.clicked.connect(self._save_config)
        conn_layout.addWidget(save_cfg_btn)
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

        # ---- Blockly tab ----
        self._build_blockly_tab()

        # ---- Serial tab ----
        serial_tab = QWidget()
        self._tabs.addTab(serial_tab, "Serial")
        serial_layout = QVBoxLayout(serial_tab)
        serial_layout.addWidget(QLabel("Serial monitor — coming soon"))
        serial_layout.addStretch()

        # ---- I²C tab ----
        i2c_tab = QWidget()
        self._tabs.addTab(i2c_tab, "I²C")
        i2c_layout = QVBoxLayout(i2c_tab)
        i2c_layout.addWidget(QLabel("I²C monitor — coming soon"))
        i2c_layout.addStretch()

        # ---- SPI tab ----
        spi_tab = QWidget()
        self._tabs.addTab(spi_tab, "SPI")
        spi_layout = QVBoxLayout(spi_tab)
        spi_layout.addWidget(QLabel("SPI monitor — coming soon"))
        spi_layout.addStretch()

        # ---- Scripting tab ----
        scripting_tab = QWidget()
        self._tabs.addTab(scripting_tab, "Scripting")
        scripting_layout = QVBoxLayout(scripting_tab)
        scripting_layout.addWidget(QLabel("Scripting — coming soon"))
        scripting_layout.addStretch()

        # ---- status bar ----
        self._status = QStatusBar()
        self.setStatusBar(self._status)
        self._set_status("Ready — not connected", ok=None)

    def _build_blockly_tab(self):
        tab = QWidget()
        self._tabs.addTab(tab, "Blockly")
        layout = QVBoxLayout(tab)
        layout.setSpacing(4)

        if QWebEngineView is None:
            msg = QLabel(
                "Blockly needs the Qt web engine. Install it with "
                "<code>pip install PyQtWebEngine</code> and restart.<br>"
                f"<i>{_WEBENGINE_ERROR}</i>"
            )
            msg.setWordWrap(True)
            layout.addWidget(msg)
            layout.addStretch()
            return

        bar = QHBoxLayout()
        self._blockly_run_btn = QPushButton("\u25b6 Run")
        self._blockly_run_btn.setToolTip("Run the blocks on the connected board")
        self._blockly_run_btn.clicked.connect(self._blockly_run)
        bar.addWidget(self._blockly_run_btn)
        self._blockly_stop_btn = QPushButton("\u25a0 Stop")
        self._blockly_stop_btn.clicked.connect(lambda: self._blockly_stop())
        bar.addWidget(self._blockly_stop_btn)
        bar.addSpacing(16)
        for text, slot in [
            ("New", self._blockly_new),
            ("Load…", self._blockly_load),
            ("Save…", self._blockly_save),
            ("Show code", self._blockly_show_code),
        ]:
            btn = QPushButton(text)
            btn.clicked.connect(slot)
            bar.addWidget(btn)
        bar.addStretch()
        layout.addLayout(bar)

        self._blockly_fetch_btn = QPushButton("Download Blockly")
        self._blockly_fetch_btn.setToolTip("Fetch the Blockly library files (runs fetch_blockly.py)")
        self._blockly_fetch_btn.clicked.connect(self._blockly_fetch)
        bar.insertWidget(bar.count() - 1, self._blockly_fetch_btn)

        self._blockly_view = QWebEngineView()
        self._blockly_load_page()

        self._blockly_code = QPlainTextEdit()
        self._blockly_code.setReadOnly(True)
        self._blockly_code.setPlaceholderText("Generated Python (click Show code)")
        self._blockly_log = QPlainTextEdit()
        self._blockly_log.setReadOnly(True)
        self._blockly_log.setMaximumBlockCount(2000)
        self._blockly_log.setPlaceholderText("Script output")
        for edit in (self._blockly_code, self._blockly_log):
            edit.setStyleSheet("font-family: Consolas, monospace;")

        bottom = QSplitter(Qt.Horizontal)
        bottom.addWidget(self._blockly_code)
        bottom.addWidget(self._blockly_log)
        split = QSplitter(Qt.Vertical)
        split.addWidget(self._blockly_view)
        split.addWidget(bottom)
        split.setStretchFactor(0, 4)
        split.setStretchFactor(1, 1)
        layout.addWidget(split, stretch=1)
        self._update_blockly_buttons()

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
        self._update_blockly_buttons()

    def _update_blockly_buttons(self):
        if self._blockly_view is None:
            return
        running = self._blockly_worker is not None
        self._blockly_run_btn.setEnabled(self._connected and not running)
        self._blockly_stop_btn.setEnabled(running)

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
        self._blockly_stop(wait=True)
        self._stop_sampling()
        if self._x2c:
            try:
                with self._x2c_lock:
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
            with self._x2c_lock:
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
                with self._x2c_lock:
                    var = self._x2c.get_variable(name)
                if var is None:
                    avail = [v for v in self._x2c.list_variables() if "adc" in v.lower()]
                    self._set_status(
                        f"Variable '{name}' not found. ADC vars in ELF: {avail[:6]}",
                        ok=False,
                    )
                    return
                self._vars[name] = var
                with self._x2c_lock:
                    self._x2c.add_scope_channel(var)
            self._apply_scope_settings()
        except Exception as exc:
            self._set_status(f"Scope setup failed: {exc}", ok=False)
            return

        self._worker = ScopeWorker(self._x2c, self._x2c_lock, single_shot=single_shot)
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
                with self._x2c_lock:
                    var = self._x2c.get_variable(name)
                if var is not None:
                    self._pwm_vars[name] = var
                    try:
                        with self._x2c_lock:
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
                with self._x2c_lock:
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
            with self._x2c_lock:
                var = self._x2c.get_variable(name)
            if var is not None:
                self._gpo_vars[name] = var
                try:
                    with self._x2c_lock:
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
            with self._x2c_lock:
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
            with self._x2c_lock:
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
                with self._x2c_lock:
                    val = var.get_value()
                self._gpi_value_labels[i].setText("1" if val else "0")
            except Exception:
                pass
        sw_var = self._gpi_vars.get(GPI_SW_VAR)
        if sw_var is not None:
            try:
                with self._x2c_lock:
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
        with self._x2c_lock:
            self._apply_scope_settings_locked()

    def _apply_scope_settings_locked(self):
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
    # Blockly
    # ------------------------------------------------------------------
    def _blockly_js(self, script: str, callback=None):
        if self._blockly_view is None:
            return
        if callback is None:
            self._blockly_view.page().runJavaScript(script)
        else:
            self._blockly_view.page().runJavaScript(script, callback)

    def _blockly_load_page(self):
        lib = BLOCKLY_DIR / "blockly_compressed.js"
        missing = not lib.exists()
        self._blockly_fetch_btn.setVisible(missing)
        if missing:
            self._blockly_view.setHtml(
                "<body style='font-family:sans-serif;padding:20px'>"
                "<h3>Blockly library files are missing</h3>"
                f"<p>Not found: <code>{lib}</code></p>"
                "<p>Click <b>Download Blockly</b> above, or run "
                "<code>venv\\Scripts\\python fetch_blockly.py</code> in the <code>sw</code> folder.</p>"
                "</body>"
            )
        else:
            self._blockly_view.setUrl(QUrl.fromLocalFile(str(BLOCKLY_DIR / "blockly.html")))

    def _blockly_fetch(self):
        sw_dir = Path(__file__).resolve().parent.parent
        if not (sw_dir / "fetch_blockly.py").exists():
            self._set_status(f"fetch_blockly.py not found in {sw_dir}", ok=False)
            return
        if str(sw_dir) not in sys.path:
            sys.path.insert(0, str(sw_dir))
        QApplication.setOverrideCursor(Qt.WaitCursor)
        self._set_status("Downloading Blockly…", ok=None)
        QApplication.processEvents()
        try:
            import fetch_blockly
            ok = fetch_blockly.main() == 0
        except Exception as exc:
            ok = False
            self._set_status(f"Blockly download failed: {exc}", ok=False)
        finally:
            QApplication.restoreOverrideCursor()
        if ok:
            self._set_status("Blockly downloaded", ok=True)
            self._blockly_load_page()

    def _blockly_log_line(self, text: str):
        self._blockly_log.appendPlainText(f"[{time.strftime('%H:%M:%S')}] {text}")

    def _blockly_run(self):
        if self._blockly_worker is not None:
            return
        if not self._connected or self._x2c is None:
            self._set_status("Blockly: connect to the board first", ok=False)
            return
        self._blockly_js("mlabGenerate(false)", self._blockly_code.setPlainText)
        self._blockly_js("mlabGenerate(true)", self._blockly_start)

    def _blockly_start(self, code):
        if self._blockly_worker is not None or not self._connected or self._x2c is None:
            return
        if code is None:
            self._blockly_log_line("Error: could not generate code from the workspace.")
            return
        if not code.strip():
            self._blockly_log_line("Workspace is empty.")
            return
        self._blockly_stop_event = threading.Event()
        hal = BlocklyHAL(self._x2c, self._x2c_lock, self._blockly_stop_event)
        worker = BlocklyWorker(code, hal)
        worker.log.connect(self._blockly_log_line)
        worker.highlight.connect(
            lambda block_id: self._blockly_js(f"mlabHighlight({json.dumps(block_id)})")
        )
        worker.finished.connect(lambda w=worker: self._blockly_finished(w))
        self._blockly_worker = worker
        worker.start()
        self._update_blockly_buttons()
        self._set_status("Blockly script running", ok=True)

    def _blockly_stop(self, wait: bool = False):
        if self._blockly_worker is None:
            return
        self._blockly_stop_event.set()
        if wait:
            self._blockly_worker.wait(3000)

    def _blockly_finished(self, worker: BlocklyWorker):
        if worker is not self._blockly_worker:
            return
        self._blockly_worker = None
        self._update_blockly_buttons()
        if self._connected and self._x2c is not None:
            # script may have changed outputs/PWM: resync the Main tab widgets
            self._load_pwm_vars()
            self._load_gpio_vars()
            self._set_status("Blockly script ended", ok=None)

    def _blockly_new(self):
        if QMessageBox.question(
            self, "New workspace", "Discard the current blocks?"
        ) == QMessageBox.Yes:
            self._blockly_js("mlabNew()")

    def _blockly_show_code(self):
        self._blockly_js("mlabGenerate(false)", self._blockly_code.setPlainText)

    def _blockly_save(self):
        if self._blockly_view is None:
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Blockly workspace",
            self._blockly_last_path or "blockly_program.json",
            "Blockly workspace (*.json);;All files (*)",
        )
        if not path:
            return

        def write(text):
            if text is None:
                self._set_status("Blockly save failed: could not read workspace", ok=False)
                return
            try:
                Path(path).write_text(text, encoding="utf-8")
                self._blockly_last_path = path
                self._set_status(f"Blockly workspace saved: {path}", ok=True)
            except Exception as exc:
                self._set_status(f"Blockly save failed: {exc}", ok=False)

        self._blockly_js("mlabSave()", write)

    def _blockly_load(self):
        if self._blockly_view is None:
            return
        path, _ = QFileDialog.getOpenFileName(
            self, "Load Blockly workspace",
            self._blockly_last_path or "",
            "Blockly workspace (*.json);;All files (*)",
        )
        if not path:
            return
        try:
            text = Path(path).read_text(encoding="utf-8")
        except Exception as exc:
            self._set_status(f"Blockly load failed: {exc}", ok=False)
            return

        def done(ok):
            if ok:
                self._blockly_last_path = path
                self._set_status(f"Blockly workspace loaded: {path}", ok=True)
            else:
                self._set_status(f"Blockly load failed: not a valid workspace: {path}", ok=False)

        self._blockly_js(f"mlabLoad({json.dumps(text)})", done)

    # ------------------------------------------------------------------
    # Configuration save / load
    # ------------------------------------------------------------------
    def _save_config(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Save configuration",
            self._last_config_path or "mlab_scope_config.json",
            "JSON files (*.json);;All files (*)",
        )
        if not path:
            return
        cfg = {
            "elf": self._elf_edit.text(),
            "channels": [
                {
                    "enabled": self._ch_enable[i].isChecked(),
                    "gain":    self._ch_gain[i].value(),
                    "offset":  self._ch_offset[i].value(),
                    "trig":    self._ch_trig[i].isChecked(),
                }
                for i in range(len(CHANNEL_LABELS))
            ],
            "pwm": [
                {
                    "duty":   self._pwm_dc_sb[i].value(),
                    "period": self._pwm_f_sb[i].value(),
                }
                for i in range(PWM_COUNT)
            ],
            "scope": {
                "sample_time": self._sample_time_sb.value(),
                "trig_level":  self._trig_level_sb.value(),
                "trig_edge":   self._trig_edge_combo.currentIndex(),
                "trig_mode":   self._trig_mode_combo.currentIndex(),
                "trig_delay":  self._trig_delay_sb.value(),
                "single_shot": self._single_shot_cb.isChecked(),
            },
        }
        try:
            Path(path).write_text(json.dumps(cfg, indent=2))
            self._last_config_path = path
            self._set_status(f"Config saved: {path}", ok=True)
        except Exception as exc:
            self._set_status(f"Save failed: {exc}", ok=False)

    def _load_config(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Load configuration",
            self._last_config_path or "",
            "JSON files (*.json);;All files (*)",
        )
        if not path:
            return
        try:
            cfg = json.loads(Path(path).read_text())
        except Exception as exc:
            self._set_status(f"Load failed: {exc}", ok=False)
            return

        if "elf" in cfg:
            self._elf_edit.setText(cfg["elf"])

        for i, ch in enumerate(cfg.get("channels", [])):
            if i >= len(CHANNEL_LABELS):
                break
            self._ch_enable[i].setChecked(ch.get("enabled", True))
            self._ch_gain[i].setValue(ch.get("gain", 1.0))
            self._ch_offset[i].setValue(ch.get("offset", 0.0))
            if ch.get("trig", False):
                self._ch_trig[i].setChecked(True)

        for i, pw in enumerate(cfg.get("pwm", [])):
            if i >= PWM_COUNT:
                break
            self._pwm_dc_sb[i].setValue(pw.get("duty", PWM_DC_DEFAULT))
            self._pwm_f_sb[i].setValue(pw.get("period", PWM_F_DEFAULT))

        sc = cfg.get("scope", {})
        if "sample_time" in sc:
            self._sample_time_sb.setValue(sc["sample_time"])
        if "trig_level" in sc:
            self._trig_level_sb.setValue(sc["trig_level"])
        if "trig_edge" in sc:
            self._trig_edge_combo.setCurrentIndex(sc["trig_edge"])
        if "trig_mode" in sc:
            self._trig_mode_combo.setCurrentIndex(sc["trig_mode"])
        if "trig_delay" in sc:
            self._trig_delay_sb.setValue(sc["trig_delay"])
        if "single_shot" in sc:
            self._single_shot_cb.setChecked(sc["single_shot"])

        self._last_config_path = path
        self._set_status(f"Config loaded: {path}", ok=True)

    # ------------------------------------------------------------------
    def closeEvent(self, event):
        self._autoconnect_timer.stop()
        self._gpi_timer.stop()
        self._disconnect()
        super().closeEvent(event)


# ---------------------------------------------------------------------------
def main():
    global pg
    QApplication.setAttribute(Qt.AA_ShareOpenGLContexts)  # required by QtWebEngine
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    import pyqtgraph as pg  # delayed: requires QApplication to exist first
    pg.setConfigOptions(antialias=True, background="#1e1e2e", foreground="#cdd6f4")
    win = MLAbScopeWindow()
    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
