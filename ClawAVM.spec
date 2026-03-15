# -*- mode: python ; coding: utf-8 -*-
"""
ClawAVM Windows 打包配置
生成单个可执行文件，包含 GUI 界面
"""

block_cipher = None

a = Analysis(
    ['claw_avm/__main__.py'],  # 入口点
    pathex=['.'],
    binaries=[],
    datas=[
        ('claw_avm/locales', 'claw_avm/locales'),
        ('assets/banner.svg', 'assets'),
    ],
    hiddenimports=[
        'claw_avm.secure.engine',
        'claw_avm.engine.vmware',
        'claw_avm.engine.vmware_fusion',
        'claw_avm.engine.virtualbox',
        'claw_avm.gui.components',
        'claw_avm.api',
        'pydantic',
        'fastapi',
        'uvicorn',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'pytest',
        'black',
        'flake8',
        'mypy',
        'libvirt-python',  # Linux only
    ],
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
    name='ClawAVM',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Windows GUI 应用，无控制台窗口
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/clawavm.ico',  # 需要创建图标文件
)
