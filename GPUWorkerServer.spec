# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

block_cipher = None

# Collect CustomTkinter assets (themes, json fonts, etc.)
datas = collect_data_files('customtkinter')
datas += [
    ('shared', 'shared'),
    ('server/.env.example', 'server'),
    ('client/assets', 'client/assets'),
]
datas += collect_data_files('imageio_ffmpeg')

hiddenimports = [
    'customtkinter',
    'darkdetect',
    'PIL',
    'PIL.Image',
    'uvicorn',
    'uvicorn.logging',
    'uvicorn.loops',
    'uvicorn.loops.auto',
    'uvicorn.protocols',
    'uvicorn.protocols.http',
    'uvicorn.protocols.http.auto',
    'uvicorn.protocols.websockets',
    'uvicorn.protocols.websockets.auto',
    'fastapi',
    'websockets',
    'pydantic',
    'pydantic_settings',
    'imageio_ffmpeg',
    'psutil',
    'aiofiles',
    'multipart',
    'server',
    'server.app',
    'server.app.main',
    'server.app.server_state',
    'server.app.services.connection_tracker',
    'server.ui',
    'server.ui.server_app',
]

a = Analysis(
    ['server_entrypoint.py'],
    pathex=['.'],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['pytest'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='GPUWorkerServer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False, # Pure Desktop GUI Application
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='client/assets/icon.ico'
)
