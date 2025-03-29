# vim: set filetype=python fileencoding=utf-8:
# -*- mode: python ; coding: utf-8 -*-

import os

# https://stackoverflow.com/a/77548608/14833542
from PyInstaller.utils.hooks import copy_metadata


datas = [ ]
datas += copy_metadata( 'readchar', recursive=True )

name = os.environ.get( '_PYI_EXECUTABLE_NAME', 'mimeogram' )
block_cipher = None


a = Analysis(
    [ 'sources/mimeogram/__main__.py' ],
    pathex = [ ],
    binaries = [ ],
    datas = [
        *datas,
        ('pyproject.toml', '.'),
        # --- BEGIN: Injected by Copier ---
        ('data', 'data'),
        # --- END: Injected by Copier ---
    ],
    hiddenimports = [
        # https://github.com/openai/tiktoken/issues/80#issuecomment-1484965176
        'tiktoken_ext',
        'tiktoken_ext.openai_public',
    ],
    hookspath = [ ],
    hooksconfig = { },
    runtime_hooks = [ ],
    excludes = [ ],
    win_no_prefer_redirects = False,
    win_private_assemblies = False,
    cipher = block_cipher,
    noarchive = False,
    optimize = 0,
)

pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher
)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    a.zipfiles,
    [ ],
    name = name,
    debug = False,
    bootloader_ignore_signals = False,
    strip = False,
    upx = True,
    upx_exclude = [],
    runtime_tmpdir = None,
    console = True,
    disable_windowed_traceback = False,
    argv_emulation = False,
    target_arch = None,
    codesign_identity = None,
    entitlements_file = None,
)
