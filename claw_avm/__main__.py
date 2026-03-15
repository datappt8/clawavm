"""
ClawAVM - 入口点
"""
import sys
from pathlib import Path

# 添加当前目录到路径（用于 PyInstaller）
if getattr(sys, 'frozen', False):
    # 打包后的路径
    BASE_DIR = Path(sys.executable).parent
else:
    # 开发环境路径
    BASE_DIR = Path(__file__).parent.parent

# 设置工作目录
import os
os.chdir(BASE_DIR)

# 启动 GUI
from claw_avm.gui import main

if __name__ == '__main__':
    main()
