# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for KB Support Basedoc Standalone
Generates a single-folder executable
"""

import sys
from pathlib import Path

block_cipher = None

# Base directory
base_dir = Path(SPECPATH)

# Data files to include
datas = [
    ('.env.standalone', '.'),
    ('app/templates', 'app/templates'),
    ('app/static', 'app/static'),
]

# Hidden imports (modules not automatically detected)
hiddenimports = [
    'flask',
    'flask_sqlalchemy',
    'flask_login',
    'flask_migrate',
    'flask_wtf',
    'flask_caching',
    'flask_limiter',
    'sqlalchemy',
    'sqlalchemy.ext.declarative',
    'sqlalchemy.orm',
    'anthropic',
    'werkzeug',
    'jinja2',
    'wtforms',
    'email_validator',
    'dotenv',
    'markdown',
    'bleach',
    'PIL',
    'PyPDF2',
    'python-docx',
    'openpyxl',
]

a = Analysis(
    ['standalone.py'],
    pathex=[str(base_dir)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name='KBBasedoc',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Pas de console Windows
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Vous pouvez ajouter un icône ici
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='KBBasedoc',
)
