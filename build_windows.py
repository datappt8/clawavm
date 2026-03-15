"""
ClawAVM 构建脚本
支持 Windows 自动化打包
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def check_pyinstaller():
    """检查 PyInstaller 是否安装"""
    try:
        import PyInstaller
        return True
    except ImportError:
        return False


def install_pyinstaller():
    """安装 PyInstaller"""
    print("📦 安装 PyInstaller...")
    subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
    print("✅ PyInstaller 安装完成")


def build_windows():
    """构建 Windows 版本"""
    print("🔨 开始构建 Windows 版本...")
    
    # 清理旧构建
    for folder in ['build', 'dist']:
        if os.path.exists(folder):
            shutil.rmtree(folder)
            print(f"🗑️ 清理 {folder}/")
    
    # 运行 PyInstaller
    subprocess.run([
        sys.executable, "-m", "PyInstaller",
        "--clean",
        "--onefile",
        "--windowed",
        "--name", "ClawAVM",
        "--icon", "assets/clawavm.ico",
        "--add-data", "claw_avm/locales;claw_avm/locales",
        "--add-data", "assets/banner.svg;assets",
        "--hidden-import", "claw_avm.secure.engine",
        "--hidden-import", "claw_avm.engine.vmware",
        "--hidden-import", "claw_avm.engine.virtualbox",
        "--hidden-import", "claw_avm.gui.components",
        "claw_avm/__main__.py"
    ], check=True)
    
    print("✅ Windows 构建完成！")
    print(f"📁 输出文件: {os.path.abspath('dist/ClawAVM.exe')}")


def create_installer_script():
    """创建 Windows 安装脚本"""
    script_content = '''@echo off
chcp 65001 >nul
title ClawAVM Windows 安装程序
echo.
echo  ==========================================
echo   🦞 ClawAVM - OpenClaw 安全隔离虚拟机
echo   Windows 自动安装程序
echo  ==========================================
echo.

:: 检查管理员权限
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ⚠️  需要管理员权限，正在重新启动...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

:: 设置安装目录
set "INSTALL_DIR=C:\\Program Files\\ClawAVM"
set "DATA_DIR=%USERPROFILE%\\ClawAVM"

echo 📂 安装目录: %INSTALL_DIR%
echo 📂 数据目录: %DATA_DIR%
echo.

:: 创建目录
echo 📁 创建安装目录...
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"
if not exist "%DATA_DIR%" mkdir "%DATA_DIR%"
if not exist "%DATA_DIR%\\vm_workspace" mkdir "%DATA_DIR%\\vm_workspace"

:: 复制文件
echo 📦 复制程序文件...
xcopy /Y /E "%~dp0ClawAVM.exe" "%INSTALL_DIR%\\"
if exist "%~dp0README.md" xcopy /Y "%~dp0README.md" "%INSTALL_DIR%\\"

:: 创建快捷方式
echo 🎯 创建快捷方式...
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\ClawAVM.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\\ClawAVM.exe'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.IconLocation = '%INSTALL_DIR%\\ClawAVM.exe'; $Shortcut.Save();"
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\\Desktop\\ClawAVM.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\\ClawAVM.exe'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.IconLocation = '%INSTALL_DIR%\\ClawAVM.exe'; $Shortcut.Save();"

:: 添加到 PATH (可选)
echo 🔧 配置环境变量...
setx PATH "%PATH%;%INSTALL_DIR%" /M >nul 2>&1

:: 创建卸载程序
echo 🗑️  创建卸载程序...
(
echo @echo off
echo chcp 65001 ^>nul
echo title ClawAVM 卸载程序
echo echo 正在卸载 ClawAVM...
echo taskkill /F /IM ClawAVM.exe ^>nul 2^>^&1
echo rmdir /S /Q "%INSTALL_DIR%"
echo del /F /Q "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\ClawAVM.lnk"
echo del /F /Q "%USERPROFILE%\\Desktop\\ClawAVM.lnk"
echo echo ✅ 卸载完成
echo pause
echo exit
) > "%INSTALL_DIR%\\uninstall.bat"

echo.
echo  ==========================================
echo   ✅ 安装完成！
echo  ==========================================
echo.
echo   🎯 启动方式:
echo      • 开始菜单: ClawAVM
echo      • 桌面快捷方式
echo      • 安装目录: %INSTALL_DIR%
echo.
echo   📂 数据目录: %DATA_DIR%
echo.
echo   🗑️  卸载: 运行 %INSTALL_DIR%\\uninstall.bat
echo.

:: 询问是否立即启动
set /p START_NOW="是否立即启动 ClawAVM? (Y/N): "
if /I "%START_NOW%"=="Y" (
    start "" "%INSTALL_DIR%\\ClawAVM.exe"
)

echo.
echo 按任意键退出...
pause >nul
'''
    
    with open('install_windows.bat', 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    print("✅ 安装脚本已创建: install_windows.bat")


def create_portable_package():
    """创建便携版"""
    print("📦 创建便携版...")
    
    portable_dir = 'dist/ClawAVM-Portable'
    os.makedirs(portable_dir, exist_ok=True)
    
    # 复制主程序
    shutil.copy('dist/ClawAVM.exe', f'{portable_dir}/')
    
    # 创建启动脚本
    with open(f'{portable_dir}/启动 ClawAVM.bat', 'w', encoding='utf-8') as f:
        f.write('''@echo off
chcp 65001 >nul
title ClawAVM 便携版
echo 🦞 启动 ClawAVM...
echo 📂 工作目录: %~dp0
"%~dp0ClawAVM.exe"
''')
    
    # 创建 README
    with open(f'{portable_dir}/README.txt', 'w', encoding='utf-8') as f:
        f.write('''ClawAVM 便携版
==============

使用方法:
1. 双击 "启动 ClawAVM.bat" 运行
2. 或双击 ClawAVM.exe 直接运行

数据将保存在程序所在目录的 data/ 文件夹中。

系统要求:
- Windows 10/11
- VMware Workstation 或 VirtualBox 已安装

更多信息: https://github.com/datappt8/clawavm
''')
    
    print(f"✅ 便携版已创建: {os.path.abspath(portable_dir)}/")


def main():
    """主函数"""
    print("🦞 ClawAVM Windows 构建脚本")
    print("=" * 50)
    
    # 检查并安装 PyInstaller
    if not check_pyinstaller():
        install_pyinstaller()
    else:
        print("✅ PyInstaller 已安装")
    
    # 构建
    build_windows()
    
    # 创建安装脚本
    create_installer_script()
    
    # 创建便携版
    create_portable_package()
    
    print("\n" + "=" * 50)
    print("🎉 所有构建任务完成！")
    print("\n输出文件:")
    print("  📦 dist/ClawAVM.exe - 主程序")
    print("  📦 install_windows.bat - Windows 安装脚本")
    print("  📦 dist/ClawAVM-Portable/ - 便携版文件夹")


if __name__ == '__main__':
    main()
