# Windows 打包和安装指南

## 📦 打包方式

ClawAVM 提供三种 Windows 分发方式：

### 方式 1: 安装程序 (推荐)
使用 Inno Setup 创建专业的 Windows 安装包。

```bash
# 1. 先构建可执行文件
python build_windows.py

# 2. 使用 Inno Setup 编译安装程序
# 下载安装 Inno Setup: https://jrsoftware.org/isinfo.php
# 然后打开 setup_windows.iss 并编译
```

**特点：**
- 标准 Windows 安装向导
- 自动创建开始菜单和桌面快捷方式
- 支持卸载
- 管理员权限自动请求

---

### 方式 2: 便携版
无需安装，解压即用。

```bash
python build_windows.py
# 输出: dist/ClawAVM-Portable/
```

**特点：**
- 无需管理员权限
- 所有数据保存在程序目录
- 可直接复制到 U 盘使用

---

### 方式 3: 批处理安装
使用 `install_windows.bat` 自动安装。

```bash
# 构建完成后
# 将 ClawAVM.exe + install_windows.bat 放在同一目录
# 运行 install_windows.bat
```

**特点：**
- 轻量级安装
- 适合快速部署
- 可自定义安装路径

---

## 🔨 构建步骤

### 环境要求
- Windows 10/11
- Python 3.9+
- PyInstaller (`pip install pyinstaller`)
- (可选) Inno Setup 6+

### 快速构建

```bash
# 克隆仓库
git clone https://github.com/datappt8/clawavm.git
cd clawavm

# 安装依赖
pip install -r requirements.txt
pip install pyinstaller

# 运行构建脚本
python build_windows.py
```

构建完成后：
- `dist/ClawAVM.exe` - 单文件可执行程序
- `dist/ClawAVM-Portable/` - 便携版文件夹
- `install_windows.bat` - 安装脚本

---

## 📋 安装后配置

### 首次运行

1. **安装虚拟机软件** (选择其一)
   - [VirtualBox](https://www.virtualbox.org/) (免费推荐)
   - [VMware Workstation Player](https://www.vmware.com/products/workstation-player.html) (免费个人版)

2. **启动 ClawAVM**
   - 双击桌面快捷方式，或
   - 从开始菜单启动

3. **创建第一个隔离虚拟机**
   - 点击 "创建虚拟机"
   - 选择引擎 (VirtualBox/VMware)
   - 配置资源 (内存、CPU、磁盘)
   - 点击 "创建"

---

## 🎯 使用场景

### 场景 1: 在隔离环境中运行 OpenClaw

```python
# 创建专用虚拟机
vm_id = engine.create_secure_vm(config)
engine.start_vm(vm_id)

# 在虚拟机中:
# 1. 安装 Python
# 2. pip install openclaw
# 3. 配置并启动 openclaw gateway

# 通过 SSH 隧道从主机访问
# ssh -L 18789:localhost:18789 vm-user@vm-ip
```

### 场景 2: 快照管理

```python
# 测试前创建快照
engine.create_security_snapshot(vm_id, "BeforeTest")

# 进行一些可能搞坏系统的操作...

# 恢复干净状态
engine.restore_snapshot(vm_id, "BeforeTest")
```

---

## 🔧 常见问题

### Q: 无法检测到 VirtualBox/VMware
A: 确保已安装虚拟机软件，并重启 ClawAVM。程序会自动扫描常见安装路径。

### Q: 构建失败，提示缺少依赖
A: 运行 `pip install -r requirements.txt` 安装所有依赖。

### Q: 可执行文件太大
A: PyInstaller 打包会包含 Python 解释器和所有依赖。可以使用 UPX 压缩，或选择不包含调试信息。

### Q: 杀毒软件报毒
A: 这是 PyInstaller 打包的可执行文件的常见问题。可以：
1. 将程序添加到杀毒软件白名单
2. 从源代码运行
3. 提交到杀毒软件厂商进行误报反馈

---

## 📄 文件说明

| 文件 | 说明 |
|------|------|
| `ClawAVM.spec` | PyInstaller 配置文件 |
| `build_windows.py` | Windows 构建脚本 |
| `setup_windows.iss` | Inno Setup 安装程序脚本 |
| `install_windows.bat` | 批处理安装脚本 |
| `dist/ClawAVM.exe` | 生成的可执行文件 |

---

## 🤝 贡献

欢迎改进 Windows 打包方案！
- 优化构建脚本
- 添加代码签名
- 支持更多安装选项

提交 PR 到: https://github.com/datappt8/clawavm
