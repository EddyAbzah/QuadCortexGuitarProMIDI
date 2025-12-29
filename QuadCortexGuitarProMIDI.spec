# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['QuadCortexGuitarProMIDI.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports = [
    "mido.backends.rtmidi",
    "rtmidi"
	],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='QuadCortexGuitarProMIDI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['icon.png'],
    contents_directory='QuadCortexGuitarProMIDI',
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='QuadCortexGuitarProMIDI',
)
