# PyInstaller spec for mLabScope
# Run from the sw/ directory:  venv\Scripts\pyinstaller mlab_scope.spec

from PyInstaller.utils.hooks import collect_all, collect_submodules

block_cipher = None

# Collect packages that use dynamic/plugin-style imports
pyx2c_datas, pyx2c_binaries, pyx2c_hiddens = collect_all("pyx2cscope")
mchpl_datas,  mchpl_binaries,  mchpl_hiddens  = collect_all("mchplnet")
eio_datas,    eio_binaries,    eio_hiddens    = collect_all("engineio")
sio_datas,    sio_binaries,    sio_hiddens    = collect_all("socketio")
flask_datas,  flask_binaries,  flask_hiddens  = collect_all("flask")

a = Analysis(
    ["support/mlab_scope.py"],
    pathex=["."],
    binaries=(
        mchpl_binaries + pyx2c_binaries + eio_binaries + sio_binaries + flask_binaries
    ),
    datas=(
        pyx2c_datas + mchpl_datas + eio_datas + sio_datas + flask_datas
    ),
    hiddenimports=(
        pyx2c_hiddens + mchpl_hiddens + eio_hiddens + sio_hiddens + flask_hiddens
        + collect_submodules("pyqtgraph")
        + collect_submodules("pyelftools")
        + collect_submodules("can")
        + collect_submodules("yaml")
        + [
            "serial.tools.list_ports_windows",
            "serial.tools.list_ports_posix",
            "pkg_resources.py2_warn",
            "pkg_resources._vendor.jaraco.text",
        ]
    ),
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter", "unittest", "test"],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="mLabScope",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,          # no console window
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="mLabScope",
)
