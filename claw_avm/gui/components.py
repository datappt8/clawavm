"""
Claw AVM GUI Components - PyQt6 界面组件

核心组件：
- ClawSecureMainWindow: 主窗口
- SecurityDashboard: 安全仪表盘
- CreateVMWizard: 创建VM向导
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QListWidget, QListWidgetItem,
    QProgressBar, QFrame, QGridLayout, QGroupBox,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QDialog, QLineEdit, QSpinBox,
    QCheckBox, QComboBox, QWizard, QWizardPage
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QColor, QFont
from typing import Optional, Callable
import datetime


class SecurityStatusCard(QFrame):
    """安全状态卡片组件"""
    
    def __init__(self, title: str, status: str, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        self.setStyleSheet("""
            SecurityStatusCard {
                background-color: #2d2d2d;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("color: #888; font-size: 12px;")
        layout.addWidget(self.title_label)
        
        self.status_label = QLabel(status)
        self.status_label.setStyleSheet("color: #4CAF50; font-size: 18px; font-weight: bold;")
        layout.addWidget(self.status_label)
        
    def set_status(self, status: str, color: str = "#4CAF50"):
        """更新状态文本和颜色"""
        self.status_label.setText(status)
        self.status_label.setStyleSheet(f"color: {color}; font-size: 18px; font-weight: bold;")


class VMListWidget(QListWidget):
    """虚拟机列表组件"""
    
    vm_selected = pyqtSignal(str)  # 发出选中VM的ID
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            VMListWidget {
                background-color: #1e1e1e;
                border: 1px solid #333;
                border-radius: 4px;
            }
            VMListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #333;
            }
            VMListWidget::item:selected {
                background-color: #0d47a1;
            }
        """)
        self.itemClicked.connect(self._on_item_clicked)
        self._vm_map = {}  # item -> vm_id
    
    def add_vm(self, vm_id: str, name: str, status: str):
        """添加虚拟机到列表"""
        item = QListWidgetItem(f"🖥️ {name}\n   状态: {status}")
        self.addItem(item)
        self._vm_map[item] = vm_id
    
    def _on_item_clicked(self, item):
        vm_id = self._vm_map.get(item)
        if vm_id:
            self.vm_selected.emit(vm_id)


class SecurityDashboard(QWidget):
    """安全仪表盘 - 显示系统安全状态"""
    
    def __init__(self, engine, parent=None):
        super().__init__(parent)
        self.engine = engine
        self._init_ui()
        
        # 定时刷新
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh)
        self.refresh_timer.start(5000)  # 每5秒刷新
    
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # 标题
        title = QLabel("🔒 安全仪表盘")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #fff;")
        layout.addWidget(title)
        
        # 状态卡片区域
        cards_layout = QHBoxLayout()
        
        self.total_vm_card = SecurityStatusCard("虚拟机总数", "0")
        self.active_vm_card = SecurityStatusCard("运行中", "0")
        self.secure_vm_card = SecurityStatusCard("安全隔离", "0")
        self.threats_card = SecurityStatusCard("检测到的威胁", "0")
        
        cards_layout.addWidget(self.total_vm_card)
        cards_layout.addWidget(self.active_vm_card)
        cards_layout.addWidget(self.secure_vm_card)
        cards_layout.addWidget(self.threats_card)
        
        layout.addLayout(cards_layout)
        
        # VM 列表
        list_group = QGroupBox("虚拟机列表")
        list_layout = QVBoxLayout(list_group)
        
        self.vm_list = VMListWidget()
        list_layout.addWidget(self.vm_list)
        
        # 控制按钮
        btn_layout = QHBoxLayout()
        
        self.btn_start = QPushButton("▶️ 启动")
        self.btn_stop = QPushButton("⏹️ 停止")
        self.btn_snapshot = QPushButton("📸 快照")
        self.btn_clone = QPushButton("📋 克隆")
        self.btn_delete = QPushButton("🗑️ 删除")
        
        for btn in [self.btn_start, self.btn_stop, self.btn_snapshot, 
                    self.btn_clone, self.btn_delete]:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #333;
                    color: #fff;
                    padding: 8px 16px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #444;
                }
            """)
            btn_layout.addWidget(btn)
        
        list_layout.addLayout(btn_layout)
        layout.addWidget(list_group)
        
        # 日志区域
        log_group = QGroupBox("系统日志")
        log_layout = QVBoxLayout(log_group)
        
        self.log_widget = QListWidget()
        self.log_widget.setMaximumHeight(150)
        log_layout.addWidget(self.log_widget)
        
        layout.addWidget(log_group)
        
        self.setStyleSheet("""
            SecurityDashboard {
                background-color: #121212;
            }
            QGroupBox {
                color: #fff;
                font-weight: bold;
                border: 1px solid #333;
                border-radius: 4px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
    
    def refresh(self):
        """刷新仪表盘数据"""
        try:
            vms = self.engine.list_vms()
            
            total = len(vms)
            active = sum(1 for v in vms if v.get("status") in ["POWERED_ON", "SECURE_ISOLATED"])
            secure = sum(1 for v in vms if v.get("status") == "SECURE_ISOLATED")
            
            self.total_vm_card.set_status(str(total))
            self.active_vm_card.set_status(str(active), "#FF9800" if active > 0 else "#4CAF50")
            self.secure_vm_card.set_status(str(secure))
            
            # 更新列表
            self.vm_list.clear()
            self.vm_list._vm_map.clear()
            for vm in vms:
                self.vm_list.add_vm(
                    vm.get("id"),
                    vm.get("name"),
                    vm.get("status", "UNKNOWN")
                )
                
        except Exception as e:
            self.add_log(f"刷新失败: {e}")
    
    def add_log(self, message: str):
        """添加日志"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.log_widget.addItem(f"[{timestamp}] {message}")


class CreateVMWizard(QWizard):
    """创建虚拟机向导"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("创建安全虚拟机")
        self.setWizardStyle(QWizard.WizardStyle.ModernStyle)
        
        # 添加页面
        self.addPage(self._create_info_page())
        self.addPage(self._create_config_page())
        self.addPage(self._create_security_page())
        self.addPage(self._create_summary_page())
        
        self.setStyleSheet("""
            QWizard {
                background-color: #1e1e1e;
            }
            QWizardPage {
                background-color: #1e1e1e;
                color: #fff;
            }
            QLabel {
                color: #fff;
            }
            QLineEdit, QSpinBox, QComboBox {
                background-color: #2d2d2d;
                color: #fff;
                border: 1px solid #444;
                padding: 5px;
                border-radius: 3px;
            }
        """)
        
        # 存储配置
        self.vm_config = {}
    
    def _create_info_page(self):
        """基本信息页面"""
        page = QWizardPage()
        page.setTitle("虚拟机基本信息")
        page.setSubTitle("设置虚拟机的名称和描述")
        
        layout = QVBoxLayout(page)
        
        # 名称
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("名称:"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("输入虚拟机名称...")
        name_layout.addWidget(self.name_input)
        layout.addLayout(name_layout)
        
        # 描述
        layout.addWidget(QLabel("描述:"))
        self.desc_input = QLineEdit()
        self.desc_input.setPlaceholderText("可选描述...")
        layout.addWidget(self.desc_input)
        
        layout.addStretch()
        return page
    
    def _create_config_page(self):
        """配置页面"""
        page = QWizardPage()
        page.setTitle("硬件配置")
        page.setSubTitle("分配虚拟机资源")
        
        layout = QGridLayout(page)
        
        # 内存
        layout.addWidget(QLabel("内存 (MB):"), 0, 0)
        self.memory_spin = QSpinBox()
        self.memory_spin.setRange(512, 65536)
        self.memory_spin.setValue(4096)
        self.memory_spin.setSingleStep(512)
        layout.addWidget(self.memory_spin, 0, 1)
        
        # CPU
        layout.addWidget(QLabel("CPU 核心数:"), 1, 0)
        self.cpu_spin = QSpinBox()
        self.cpu_spin.setRange(1, 32)
        self.cpu_spin.setValue(2)
        layout.addWidget(self.cpu_spin, 1, 1)
        
        # 磁盘
        layout.addWidget(QLabel("磁盘大小 (GB):"), 2, 0)
        self.disk_spin = QSpinBox()
        self.disk_spin.setRange(10, 1000)
        self.disk_spin.setValue(50)
        layout.addWidget(self.disk_spin, 2, 1)
        
        return page
    
    def _create_security_page(self):
        """安全设置页面"""
        page = QWizardPage()
        page.setTitle("安全设置")
        page.setSubTitle("配置安全隔离选项")
        
        layout = QVBoxLayout(page)
        
        # 网络隔离
        self.network_isolated = QCheckBox("启用网络隔离（仅主机模式）")
        self.network_isolated.setChecked(True)
        layout.addWidget(self.network_isolated)
        
        # 剪贴板
        self.clipboard_check = QCheckBox("允许剪贴板共享（不安全）")
        self.clipboard_check.setChecked(False)
        layout.addWidget(self.clipboard_check)
        
        # 拖放
        self.dragdrop_check = QCheckBox("允许拖放文件（不安全）")
        self.dragdrop_check.setChecked(False)
        layout.addWidget(self.dragdrop_check)
        
        # USB
        self.usb_check = QCheckBox("启用 USB 设备（不安全）")
        self.usb_check.setChecked(False)
        layout.addWidget(self.usb_check)
        
        layout.addStretch()
        return page
    
    def _create_summary_page(self):
        """摘要页面"""
        page = QWizardPage()
        page.setTitle("配置摘要")
        page.setSubTitle("确认虚拟机配置")
        
        self.summary_label = QLabel()
        page.layout = QVBoxLayout(page)
        page.layout.addWidget(self.summary_label)
        
        return page
    
    def get_config(self):
        """获取最终配置"""
        from ..secure.engine import VMConfig
        
        return VMConfig(
            name=self.name_input.text() or "SecureVM",
            memory_mb=self.memory_spin.value(),
            cpu_cores=self.cpu_spin.value(),
            disk_gb=self.disk_spin.value(),
            network_isolated=self.network_isolated.isChecked(),
            clipboard_shared=self.clipboard_check.isChecked(),
            drag_drop_enabled=self.dragdrop_check.isChecked()
        )


class ClawSecureMainWindow(QWidget):
    """Claw AVM 主窗口"""
    
    def __init__(self, engine, parent=None):
        super().__init__(parent)
        self.engine = engine
        self.setWindowTitle("Claw AVM - 安全虚拟化管理器")
        self.resize(1200, 800)
        
        self._init_ui()
    
    def _init_ui(self):
        main_layout = QHBoxLayout(self)
        
        # 左侧边栏
        sidebar = QFrame()
        sidebar.setFixedWidth(200)
        sidebar.setStyleSheet("background-color: #1a1a2e;")
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setSpacing(10)
        
        # Logo
        logo = QLabel("🐾 Claw AVM")
        logo.setStyleSheet("font-size: 20px; font-weight: bold; color: #fff; padding: 20px;")
        sidebar_layout.addWidget(logo)
        
        # 导航按钮
        self.btn_dashboard = QPushButton("📊 仪表盘")
        self.btn_vms = QPushButton("🖥️ 虚拟机")
        self.btn_snapshots = QPushButton("📸 快照")
        self.btn_settings = QPushButton("⚙️ 设置")
        
        for btn in [self.btn_dashboard, self.btn_vms, self.btn_snapshots, self.btn_settings]:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #888;
                    padding: 12px;
                    text-align: left;
                    border: none;
                    font-size: 14px;
                }
                QPushButton:hover {
                    color: #fff;
                    background-color: #16213e;
                }
            """)
            sidebar_layout.addWidget(btn)
        
        sidebar_layout.addStretch()
        
        # 创建 VM 按钮
        self.btn_create_vm = QPushButton("➕ 创建虚拟机")
        self.btn_create_vm.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: #fff;
                padding: 12px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.btn_create_vm.clicked.connect(self._show_create_wizard)
        sidebar_layout.addWidget(self.btn_create_vm)
        
        main_layout.addWidget(sidebar)
        
        # 主内容区
        self.content_area = QFrame()
        self.content_area.setStyleSheet("background-color: #121212;")
        content_layout = QVBoxLayout(self.content_area)
        
        # 仪表盘
        self.dashboard = SecurityDashboard(self.engine)
        content_layout.addWidget(self.dashboard)
        
        main_layout.addWidget(self.content_area, 1)
        
        # 连接信号
        self.btn_dashboard.clicked.connect(lambda: self._show_page("dashboard"))
        
    def _show_page(self, page: str):
        """切换页面"""
        # 简化实现 - 实际可扩展
        if page == "dashboard":
            self.dashboard.refresh()
    
    def _show_create_wizard(self):
        """显示创建向导"""
        wizard = CreateVMWizard(self)
        if wizard.exec() == QWizard.DialogCode.Accepted:
            config = wizard.get_config()
            try:
                vm_id = self.engine.create_secure_vm(config)
                QMessageBox.information(self, "成功", f"虚拟机创建成功!\nID: {vm_id}")
                self.dashboard.refresh()
            except Exception as e:
                QMessageBox.critical(self, "错误", f"创建失败: {e}")
    
    def closeEvent(self, event):
        """关闭事件处理"""
        reply = QMessageBox.question(
            self, "确认退出",
            "退出前请确保所有虚拟机已安全关闭。确定退出?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()
