# 🦞 ClawAVM - OpenClaw 安全隔离空间

> 一键创建「数字沙盒」—— 在隔离空间中安全运行任何软件

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-60%2F60%20Passing-brightgreen.svg)]()

---

## 🎯 这是什么？

**ClawAVM** 是一个「安全隔离空间」管理器。

想象一下：
- 🤔 下载了一个来路不明的软件，不敢直接运行？
- 🔬 需要分析可疑文件，但怕感染主机？
- 🧪 想测试不稳定的程序，不想搞乱系统？
- 🔒 需要完全隔离的环境处理敏感数据？

**ClawAVM 一键帮你创建这样的安全空间。**

```
┌─────────────────────────────────────────────────────────┐
│  你的电脑（主机）                                        │
│  ┌───────────────────────────────────────────────────┐  │
│  │  🔒 安全隔离空间（虚拟机）                          │  │
│  │  • 网络隔离 - 无法连接外网                         │  │
│  │  • 剪贴板禁用 - 无法复制粘贴                       │  │
│  │  • 拖放禁用 - 无法传入传出文件                    │  │
│  │  • USB 禁用 - 无法识别外部设备                    │  │
│  │  • 快照功能 - 随时回到干净状态                    │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## ✨ 核心特性

### 🚀 一键创建隔离空间
```bash
# 5 秒创建一个隔离空间
clawavm create --name " suspicious-app-test" --isolated
```

### 🛡️ 默认安全（不是可选项）
| 安全功能 | ClawAVM | 普通虚拟机 |
|---------|---------|-----------|
| 网络隔离 | ✅ 默认开启 | ❌ 需手动配置 |
| 剪贴板隔离 | ✅ 默认禁用 | ❌ 通常开启 |
| 拖放禁用 | ✅ 默认禁用 | ❌ 通常开启 |
| USB 禁用 | ✅ 默认禁用 | ❌ 需手动配置 |
| 安全快照 | ✅ 一键创建 | ⚠️ 需手动操作 |

### 🖥️ 双引擎支持
- **VMware** - 企业级稳定性，适合重度使用
- **VirtualBox** - 免费开源，适合个人用户

---

## 🚀 30 秒上手

### 安装
```bash
git clone https://github.com/datappt8/clawavm.git
cd clawavm
pip install -r requirements.txt
```

### 创建一个隔离空间
```python
from claw_avm import ClawSecureVirtualBoxEngine
from claw_avm.secure.engine import VMConfig

# 初始化引擎
engine = ClawSecureVirtualBoxEngine(workspace_path="./isolated_space")

# 创建隔离空间（默认开启所有安全选项）
config = VMConfig(
    name="MalwareSandbox",
    memory_mb=4096,
    cpu_cores=2,
    disk_gb=50,
    network_isolated=True,   # 🔒 网络隔离
    clipboard_shared=False,  # 🔒 禁用剪贴板
    drag_drop_enabled=False  # 🔒 禁用拖放
)

space_id = engine.create_secure_vm(config)
print(f"✅ 隔离空间已创建: {space_id}")

# 启动
engine.start_vm(space_id)

# 用完销毁（连同所有数据）
# engine.delete_vm(space_id)
```

### macOS 用户使用 VMware Fusion
```python
from claw_avm import ClawSecureVMwareFusionEngine

# macOS 上使用 VMware Fusion 引擎
engine = ClawSecureVMwareFusionEngine(workspace_path="./isolated_space")

# 其余操作相同
space_id = engine.create_secure_vm(config)
engine.start_vm(space_id)
```

### GUI 版本
```bash
python -m claw_avm.gui
```

---

## 🎬 使用场景

### 场景 1：分析可疑软件
```python
# 创建干净的隔离空间
space = engine.create_secure_vm(config)
engine.start_vm(space)

# 在隔离空间中运行可疑软件...
# 观察行为、抓包、分析...

# 分析完毕，一键恢复干净状态
engine.restore_snapshot(space, "CleanState")
```

### 场景 2：软件兼容性测试
```python
# 测试新版本软件是否稳定
# 搞坏了？恢复快照，重来
engine.restore_snapshot(space, "BeforeTest")
```

### 场景 3：隐私保护浏览
```python
# 在隔离空间中进行敏感操作
# 关闭后虚拟机销毁，不留痕迹
```

---

## 🏗️ 项目结构

```
clawavm/
├── claw_avm/
│   ├── engine/           # 虚拟化引擎
│   │   ├── vmware.py     # VMware 引擎
│   │   └── virtualbox.py # VirtualBox 引擎
│   ├── secure/           # 安全核心
│   │   └── engine.py     # 安全隔离抽象层
│   ├── gui/              # 图形界面 (PyQt6)
│   ├── api/              # REST API (FastAPI)
│   └── locales/          # 15 种语言支持
├── examples/             # 使用示例
├── tests/                # 60 个单元测试
└── README.md
```

---

## 🔧 支持的虚拟化平台

| 平台 | Windows | Linux | macOS | 说明 |
|------|---------|-------|-------|------|
| VMware Workstation | ✅ | ✅ | ❌ | vmrun/VIX API |
| VMware Fusion | ❌ | ❌ | ✅ | macOS 专用版本 |
| VMware Player | ✅ | ✅ | ❌ | 同 Workstation API |
| VirtualBox | ✅ | ✅ | ✅ | VBoxManage CLI，全平台支持 |
| KVM/QEMU | 📋 计划中 | 📋 计划中 | ❌ | Linux 原生 |
| Hyper-V | 📋 计划中 | ❌ | ❌ | Windows 原生 |

---

## 🌍 多语言支持

- 🇨🇳 简体中文 | 🇺🇸 English | 🇯🇵 日本語 | 🇰🇷 한국어
- 🇩🇪 Deutsch | 🇫🇷 Français | 🇪🇸 Español | 🇷🇺 Русский
- 🇮🇹 Italiano | 🇧🇷 Português | 🇹🇷 Türkçe | 🇵🇱 Polski
- 🇳🇱 Nederlands | 🇸🇪 Svenska | 🇻🇳 Tiếng Việt

---

## 🤝 贡献

欢迎提交 Issue 和 PR！

1. Fork 本仓库
2. 创建分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

---

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

---

<div align="center">

**🦞 OpenClaw - 安全隔离，一键可达**

</div>
