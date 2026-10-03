# mLabCuriosity

Control and observe the peripherals of a Microchip **dsPIC33A Curiosity Nano** board (dsPIC33AK512MPS506) from a PC, with no debugger session and no recompiling.

The firmware exposes one global structure, `mLabCuriosity`, that mirrors the board's ADC inputs, PWM outputs and digital I/O. A desktop GUI, **mLabScope**, reads and writes that structure over the board's USB virtual COM port using [X2Cscope](https://x2cscope.github.io/) and [pyX2Cscope](https://github.com/X2Cscope/pyx2cscope). The result is a small "lab in a box": a 4-channel software oscilloscope, a 4-channel PWM generator, 4 digital outputs and 4 digital inputs plus the on-board button.

```
┌──────────────────────────┐   USB (PKOB nano virtual COM port)   ┌──────────────────────────┐
│ PC: mLabScope (PyQt5)    │◄────────────────────────────────────►│ dsPIC33AK512MPS506       │
│  pyX2Cscope + ELF symbols│        LNet protocol, 460800 8N1      │  X2Cscope lib on UART1   │
│  scope · PWM · GPIO      │                                        │  mLabCuriosity struct    │
└──────────────────────────┘                                        └──────────────────────────┘
```

---

## Contents

- [Repository layout](#repository-layout)
- [How it works](#how-it-works)
- [Hardware](#hardware)
- [Firmware](#firmware)
- [PC software: mLabScope](#pc-software-mlabscope)
- [Quick start](#quick-start)
- [Adding your own variables](#adding-your-own-variables)
- [Troubleshooting](#troubleshooting)
- [Known limitations and roadmap](#known-limitations-and-roadmap)
- [License](#license)

---

## Repository layout

| Path | Contents |
|------|----------|
| `fw/mLabCuriosity/` | Firmware project for VS Code with the MPLAB extensions (CMake build, XC-DSC compiler). |
| `fw/mLabCuriosity/config.mcc/main.c` | Application code: the `mLabCuriosity` structure and the 200 kHz control loop. |
| `fw/mLabCuriosity/config.mcc/mcc_generated_files/` | MCC Melody drivers (clock, pins, ADC1–5, SCCP1–5, TMR1, UART1–3, SPI1, I2C1) and the `X2Cscope/` integration. |
| `fw/mLabCuriosity/.vscode/` | `mLabCuriosity.mplab.json` (the MPLAB project file), build task and debug launch config. |
| `fw/mLabCuriosity/helper/` | Reference material, excluded from the build: an MPLAB X X2Cscope example for dsPIC33AK and the X2Cscope 3.1 library sources with a Windows build script. |
| `sw/support/mlab_scope.py` | The mLabScope GUI. |
| `sw/mlab_scope.spec`, `sw/build_installer.bat` | PyInstaller recipe and build script for a standalone `mLabScope.exe`. |
| `sw/mlab_scope_config.json` | Example saved GUI configuration. |
| `sw/config.ini` | pyX2Cscope settings template (ELF path, COM port, TCP and CAN options). |
| `doc/` | Board documentation, including the dsPIC33AK512MPS506 Curiosity Nano User Guide (DS70005634). |
| `hw/`, `mec/` | Placeholders for KiCad hardware and mechanical files (KiCad job sets only so far). |

---

## How it works

1. **Timer 1** interrupts every **5 µs (200 kHz)**. Its callback (`TMR1_Callback` in `main.c`):
   - copies the PWM duty cycle and period fields of `mLabCuriosity` into SCCP1–4,
   - reads the last ADC1–5 conversion results into `adc1`…`adc5` and starts the next conversion on ADC1–4,
   - samples the digital inputs `DI0`–`DI3` and the button `SW0`,
   - drives the digital outputs `DO0`–`DO3` from `dpo0`…`dpo3`,
   - calls `X2Cscope_Update()`, which records the selected scope channels at the 200 kHz rate.

   `LED0` is set high at the start of the callback and low at the end, so you can measure the ISR load on the LED pin with an oscilloscope.
2. The **main loop** only calls `X2Cscope_Communicate()`, which services the LNet protocol on UART1.
3. On the PC, **pyX2Cscope** parses the firmware's ELF file to find the address and type of every global variable. mLabScope then reads, writes and samples `mLabCuriosity.*` fields by name.

Because the PC addresses variables by their symbol names, **the ELF file must match the firmware that is flashed on the board.**

---

## Hardware

### Board

- **Board:** dsPIC33AK512MPS506 Curiosity Nano (see `doc/dsPIC33AK512MPS506-Curiosity-Nano-User-Guide-DS70005634.pdf`).
- **On-board debugger:** PKOB nano. It provides programming, debugging and the USB virtual COM port that X2Cscope uses. One USB cable is all you need.
- **Clock:** PLL1 at 320 MHz gives Fosc = 160 MHz. The peripherals (UART, SCCP, TMR1) run from an 80 MHz clock.

### Pin assignment

Taken from `mcc_generated_files/system/src/pins.c` and `pins.h`. Check the user guide for the Curiosity Nano edge-connector position of each pin.

| Function | Pin | Firmware name | Notes |
|----------|-----|---------------|-------|
| X2Cscope UART1 TX | RC10 | U1TX | Goes to the PKOB nano virtual COM port. |
| X2Cscope UART1 RX | RC11 | U1RX | Goes to the PKOB nano virtual COM port. |
| PWM0 | RD2 | SCCP1 / OCM1 | |
| PWM1 | RD3 | SCCP2 / OCM2 | |
| PWM2 | RB2 | SCCP3 / OCM3 | |
| PWM3 | RB8 | SCCP4 / OCM4 | |
| Digital out DO0 | RA3 | `DO0` | Pull-down enabled. |
| Digital out DO1 | RA4 | `DO1` | Pull-down enabled. |
| Digital out DO2 | RA5 | `DO2` | Pull-down enabled. |
| Digital out DO3 | RA6 | `DO3` | Pull-down enabled. |
| Digital in DI0 | RC4 | `DI0` | Pull-down enabled. |
| Digital in DI1 | RD4 | `DI1` | Pull-down enabled. |
| Digital in DI2 | RB10 | `DI2` | Pull-down enabled. |
| Digital in DI3 | RB9 | `DI3` | Pull-down enabled. |
| User button SW0 | RC3 | `SW0` | Pull-up enabled, reads 0 when pressed. |
| User LED0 | RD0 | `LED0` | Toggled by the 200 kHz ISR (ISR timing marker). |
| Analog in adc1 | AD1AN0 | ADC1 | |
| Analog in adc2 | AD2AN2 | ADC2 | |
| Analog in adc3 | AD3AN5 | ADC3 | |
| Analog in adc4 | AD4AN1 | ADC4 | |
| Analog in adc5 | AD5AN1 | ADC5 | Configured, but not triggered yet (see [limitations](#known-limitations-and-roadmap)). |
| UART2 TX / RX | RB5 / RB11 | UART2 | 115200 baud, initialised but not used yet. |
| UART3 TX / RX | RD7 / RB0 | UART3 | Initialised but not used yet. |
| SPI1 SCK / SDO / SDI | RD6 / RC6 / RC7 | SPI1 | Host mode, initialised but not used yet. |
| I2C1 | dedicated I2C1 pins | I2C1 | Host mode, initialised but not used yet. |

> **Voltage levels:** the dsPIC33A I/O runs at the board's VDD (3.3 V by default on the Curiosity Nano). Do not apply 5 V signals to the inputs or the ADC pins.

---

## Firmware

### Toolchain

| Item | Version used |
|------|--------------|
| IDE | VS Code with the MPLAB extension pack (CMake-based build) |
| Compiler | MPLAB XC-DSC **v4.00** |
| Device pack | `dsPIC33AK-MP_DFP` **1.6.273** |
| Code configurator | MCC Melody (the configuration lives in `config.mcc/`) |
| X2Cscope library | **3.1**, built for `generic-32dsp-ak` as `libx2cscope-generic-32dsp-dspic33a-elf.a` |

### The `mLabCuriosity` structure

Every value the GUI touches lives in this one global (`main.c`). All fields are `uint16_t`.

| Field | Direction | Meaning |
|-------|-----------|---------|
| `cnt` | MCU → PC | Free-running counter, 0…4094, incremented every ISR. Useful as a test signal. |
| `adc1` … `adc5` | MCU → PC | Raw ADC results. Each ADC accumulates 4 samples, giving a 13-bit result (0…8191). |
| `dpi0` … `dpi3` | MCU → PC | Digital inputs DI0–DI3 (0 or 1). |
| `SW0` | MCU → PC | User button (1 = released, 0 = pressed). |
| `dpo0` … `dpo3` | PC → MCU | Digital outputs DO0–DO3 (0 = low, any other value = high). |
| `pwm_dc0` … `pwm_dc3` | PC → MCU | PWM duty cycle for PWM0–3 in timer counts. Default 1000. |
| `pwm_f0` … `pwm_f3` | PC → MCU | PWM period for PWM0–3 in timer counts. Default 20000. |

**PWM units:** SCCP1–4 count at the 80 MHz peripheral clock, so one count is 12.5 ns. Period 20000 is 250 µs (**4 kHz**), and duty 1000 is 12.5 µs high (**5 %**). Keep `pwm_dcN` ≤ `pwm_fN`.

> These conversions are worked out from the MCC clock and SCCP settings, not measured on the board yet.

### X2Cscope integration

- The sources are in `config.mcc/mcc_generated_files/X2Cscope/`: `X2Cscope.c/.h`, the UART version of `X2CscopeComm.c/.h` (hooked to the MCC UART1 driver), and the prebuilt library `libx2cscope-generic-32dsp-dspic33a-elf.a`.
- UART1 runs at **460800 baud, 8N1** (BRG = 174 at 80 MHz, actual 459 770 baud, −0.2 %).
- `X2Cscope_Update()` runs in the 200 kHz Timer 1 ISR. One scope sample therefore equals **5 µs** at a sample-time setting of 1.
- The scope buffer takes about 5 kB of RAM.

### Rebuilding the X2Cscope library

You only need this if you change the X2Cscope version or the compiler options.

1. Open `fw\mLabCuriosity\helper\X2Cscope_library_make-3.1\`.
2. Run `build_x2cscope_lib.bat`. It compiles the 10 library sources with XC-DSC (`-mcpu=generic-32dsp-ak -O2`), archives them with `xc-dsc-ar` and copies the `.a` into the firmware project. It writes a log to `build_x2cscope_lib.log`.
3. You can ignore `Could not open resource file ... c30_device.info` (the archiver prints it when run without `-mdfp`) and two pointer-type warnings from the library's own `TableStruct.c` and `Scope_Main.h`.

### Build and flash

1. Open `fw/mLabCuriosity/` as a folder in VS Code.
2. Run the task **mLabCuriosity: default - Build** (Ctrl+Shift+B). The output is `out/mLabCuriosity/default.elf`.
3. Connect the Curiosity Nano over USB and program it with the **Launch mLabCuriosity: default** configuration (tool: PKOB nano), or with MPLAB IPE.

`helper/` and the build folders are excluded from the build by the file set in `.vscode/mLabCuriosity.mplab.json`. Keep it that way: the helper example has its own `main()`.

---

## PC software: mLabScope

`sw/support/mlab_scope.py` is a PyQt5 + pyqtgraph desktop application built on pyX2Cscope.

### Features

**Connection**
- ELF file selector. The default is `C:\_data\github\mLabCuriosity\fw\mLabCuriosity\out\mLabCuriosity\default.elf`.
- Fixed at 460800 baud. The COM port is detected automatically, and mLabScope retries every 2 s until a board answers.
- *Load Config* and *Save Config* store the ELF path, channel, PWM and scope settings as JSON (see `sw/mlab_scope_config.json`).

**Scope (Main tab)**
- 4 channels: `adc1`–`adc4`, each with enable, gain, offset and a trigger-source selector.
- Sample time (decimation 1…1000), trigger level, rising or falling edge, *Auto* or *Triggered* mode, and trigger delay in %.
- *Sample* or *Stop* for continuous capture, or *Single shot* for one buffer. *Apply* pushes changed trigger and sample settings while sampling.
- The time axis is in ms, using sample time × 5 µs.

**PWM Control**
- Duty and period for PWM0–3, written to the board with each row's *Set* button. When it connects, mLabScope reads the current values from the MCU.

**Digital I/O**
- GPO: 4 checkboxes that drive DO0–DO3 immediately.
- GPI: DI0–DI3 and SW0, refreshed every 100 ms.

**Other tabs:** *Serial*, *I²C*, *SPI* and *Scripting* are placeholders ("coming soon").

### Requirements

- Windows (the default paths and the installer script are Windows-specific; the Python code itself is portable).
- Python 3.10 or newer. The packaged build uses Python 3.14.
- Packages: `pyx2cscope`, `PyQt5`, `pyqtgraph`, `numpy`. `pyx2cscope` pulls in `mchplnet`, `pyserial`, `pyelftools` and its own dependencies.

### Run from source

```bat
cd sw
python -m venv venv
venv\Scripts\pip install pyx2cscope PyQt5 pyqtgraph numpy
venv\Scripts\python support\mlab_scope.py
```

### Build the standalone executable

```bat
cd sw
build_installer.bat
```

The script installs PyInstaller into the venv if needed, removes old build output, runs `pyinstaller mlab_scope.spec` and opens `dist\mLabScope\`. Ship the whole `dist\mLabScope\` folder: `mLabScope.exe` needs the `_internal\` folder next to it. It runs without a console window.

### Using the generic pyX2Cscope GUI instead

You can also use pyX2Cscope's own GUI (`python -m pyx2cscope`) with the same ELF file at 460800 baud. Add any `mLabCuriosity.*` field to the watch or scope view.

---

## Quick start

1. Build and flash the firmware ([Build and flash](#build-and-flash)).
2. Start mLabScope (`mLabScope.exe` or `python support\mlab_scope.py`).
3. Check that the ELF path points to the `default.elf` you just flashed. mLabScope connects on its own; the status bar shows `Connected — COMx @ 460800`.
4. Click **Sample** to see `adc1`–`adc4`. Apply a voltage to an analog input to see the trace move.
5. Tick **DO0** and measure RA3, or change **PWM0** duty or period, press **Set** and watch RD2 on a scope.
6. Press **SW0** on the board; the SW0 field in the GPI box changes to 0.

---

## Adding your own variables

1. Add a field to `MLABCURIOSITY_t` in `main.c` (or create any other global variable).
2. Update or read it in `TMR1_Callback` (keep that ISR short: it runs every 5 µs).
3. Rebuild and flash, then point the GUI at the new ELF.
4. In `mlab_scope.py`, add the name (for example `"mLabCuriosity.myvar"`) to the relevant list such as `ADC_CHANNELS`, `GPI_VARS` or `GPO_VARS`, or read it with `x2c.get_variable("mLabCuriosity.myvar").get_value()`.

Scripting example with pyX2Cscope only:

```python
from pyx2cscope.x2cscope import X2CScope

x2c = X2CScope(port="COM5", baud_rate=460800,
               elf_file=r"fw\mLabCuriosity\out\mLabCuriosity\default.elf")
x2c.get_variable("mLabCuriosity.dpo0").set_value(1)        # DO0 high
print(x2c.get_variable("mLabCuriosity.adc1").get_value())  # read ADC1
x2c.get_variable("mLabCuriosity.pwm_dc0").set_value(10000) # PWM0 to 50 %
```

---

## Troubleshooting

| Symptom | Likely cause and fix |
|---------|----------------------|
| The status bar keeps saying "Auto-connect: scanning…" | The board isn't flashed with X2Cscope firmware, another program (MPLAB data visualizer, a terminal) has the COM port open, or the baud rate doesn't match. The firmware and GUI both use 460800. |
| "Variable 'mLabCuriosity.adc1' not found" | The ELF file doesn't match the flashed firmware, or the ELF has no debug symbols. Rebuild, reflash, and select `out/mLabCuriosity/default.elf`. |
| Values read back as garbage | The ELF file is from a different build than the one on the chip. |
| Firmware link error: duplicate `main` | `helper/` was included in the build. Check the file-set excludes in `.vscode/mLabCuriosity.mplab.json`. |
| X2Cscope library build: archive step fails | Older versions of the batch file passed `*.o` to `xc-dsc-ar`, which doesn't expand wildcards on Windows. The current script lists every object file. |
| Scope time axis looks wrong | The axis assumes `X2Cscope_Update()` runs every 5 µs. If you change the TMR1 period, update `dt_ms` in `_on_scope_data()`. |

---

## Known limitations and roadmap

- **ADC5** is configured and read in the ISR, but the code never triggers a conversion (`AD5SWTRGbits.CH0TRG` is missing), and the GUI doesn't show it.
- **SCCP5** (pulse output), **UART2/3**, **SPI1** and **I2C1** are initialised by MCC but not used yet. The matching GUI tabs are placeholders.
- The default ELF path in `mlab_scope.py` and in `mlab_scope_config.json` is an absolute path on the author's PC.
- PWM duty and period are raw timer counts. A frequency and percentage view in the GUI would be easier to use.
- The ISR does all its peripheral work every 5 µs. Watch LED0 on a scope when you add work there.
- `sw/venv/`, `sw/build/`, `sw/dist/` and the `*.log` files are build output and should stay out of git.

---

## License

BSD 3-Clause, © 2023 tronicbaumi. See [LICENSE](LICENSE).
MCC-generated drivers and the X2Cscope library are © Microchip Technology Inc. and are subject to Microchip's license terms in their file headers.
