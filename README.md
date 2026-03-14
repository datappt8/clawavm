# 🔒 ClawAVM - Claw Anti-Virus Manager

**安全虚拟化管理器** - 基于 Python 的虚拟机安全管理平台

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![PyQt6](https://img.shields.io/badge/PyQt6-6.4+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

---

## 📋 功能特性

### 核心功能
- 🖥️ **虚拟机生命周期管理** - 创建、启动、停止、删除虚拟机
- 🔐 **安全隔离** - 网络隔离、剪贴板禁用、拖放禁用
- 📸 **快照管理** - 创建安全快照、快速恢复
- 📋 **克隆功能** - 快速复制虚拟机环境
- 🌐 **多虚拟化支持** - VMware Workstation/Player、VirtualBox

### 安全特性
- ✅ 网络隔离模式（仅主机/无网络）
- ✅ 剪贴板共享控制
- ✅ 拖放文件禁用
- ✅ USB 设备控制
- ✅ 共享文件夹禁用
- ✅ 安全快照（干净状态标记）

### GUI 功能
- 📊 安全仪表盘 - 实时 VM 状态监控
- 🧙 创建向导 - 逐步引导创建安全 VM
- 📝 系统日志 - 操作记录和审计
- 🎨 暗黑主题 - 现代化界面设计

---

## 🚀 快速开始

### 环境要求
- Python 3.9+
- VMware Workstation/Player (Windows/Linux)
- 4GB+ RAM

### 安装

```bash
# 克隆仓库
git clone https://github.com/yourusername/claw_avm.git
cd claw_avm

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或: venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 运行

```bash
# 启动 GUI
python -m claw_avm.gui

# 或运行示例
python examples/basic_usage.py
```

---

## 📖 使用示例

### 基本使用

```python
from claw_avm import ClawSecureVMwareEngine
from claw_avm.secure.engine import VMConfig
from pathlib import Path

# 初始化引擎
engine = ClawSecureVMwareEngine(
    workspace_path=Path("./vm_workspace")
)

# 创建安全虚拟机
config = VMConfig(
    name="MalwareAnalysis",
    memory_mb=4096,
    cpu_cores=2,
    disk_gb=50,
    network_isolated=True,  # 网络隔离
    clipboard_shared=False,  # 禁用剪贴板
    drag_drop_enabled=False  # 禁用拖放
)

vm_id = engine.create_secure_vm(config)
print(f"VM created with ID: {vm_id}")

# 启动虚拟机
engine.start_vm(vm_id)

# 创建安全快照（干净状态）
snapshot = engine.create_security_snapshot(
    vm_id=vm_id,
    name="CleanState",
    description="Initial clean state for malware analysis"
)

# 停止虚拟机
engine.stop_vm(vm_id)
```

### GUI 启动

```bash
# 启动主界面
python -c "from claw_avm.gui import ClawSecureMainWindow; from claw_avm import ClawSecureVMwareEngine; from PyQt6.QtWidgets import QApplication; import sys; app = QApplication(sys.argv); engine = ClawSecureVMwareEngine(workspace_path='./vm_workspace'); window = ClawSecureMainWindow(engine); window.show(); sys.exit(app.exec())"
```

---

## 🏗️ 项目结构

```
claw_avm/
├── __init__.py              # 包初始化
├── secure/                  # 安全引擎
│   ├── __init__.py
│   └── engine.py            # ClawSecureEngine 抽象基类
├── engine/                  # 虚拟化引擎实现
│   ├── __init__.py
│   └── vmware.py            # VMware 引擎实现
├── gui/                     # PyQt6 界面
│   ├── __init__.py
│   └── components.py        # GUI 组件
├── api/                     # FastAPI 接口
│   └── __init__.py
├── utils/                   # 工具函数
│   └── __init__.py
└── locales/                 # 多语言支持
    └── (translations)

examples/                    # 示例代码
tests/                       # 单元测试
docs/                        # 文档
requirements.txt             # Python 依赖
README.md                    # 本文件
```

---

## 🔧 支持的虚拟化平台

| 平台 | 状态 | 备注 |
|------|------|------|
| VMware Workstation | ✅ 已实现 | 基于 vmrun/VIX API |
| VMware Player | ✅ 支持 | 使用相同 API |
| VirtualBox | ✅ 已实现 | 基于 VBoxManage 命令行 |
| KVM/QEMU | 🚧 开发中 | Linux 原生支持 |
| Hyper-V | 📋 计划中 | Windows 原生支持 |

---

## 🌍 多语言支持

计划支持 15 种语言：
- 🇨🇳 简体中文
- 🇺🇸 English
- 🇯🇵 日本語
- 🇰🇷 한국어
- 🇩🇪 Deutsch
- 🇫🇷 Français
- 🇪🇸 Español
- 🇷🇺 Русский
- 🇮🇹 Italiano
- 🇧🇷 Português
- 🇹🇷 Türkçe
- 🇵🇱 Polski
- 🇳🇱 Nederlands
- 🇸🇪 Svenska
- 🇻🇳 Tiếng Việt

---

## 🤝 贡献

欢迎提交 Issue 和 PR！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

---

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

---

## 🙏 致谢

- 感谢 VMware 提供 VIX API
- PyQt6 团队提供的优秀 GUI 框架
- 开源社区的支持

---

<div align="center">

**🐾 Made with love by Kimi Claw**

</div>
