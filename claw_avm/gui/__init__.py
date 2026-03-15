"""GUI components for ClawAVM"""
from .main_window import ClawSecureMainWindow
from .dashboard import SecurityDashboard
from .wizard import CreateVMWizard

def main():
    """GUI 入口点"""
    import sys
    from PyQt6.QtWidgets import QApplication
    from pathlib import Path
    
    app = QApplication(sys.argv)
    app.setApplicationName("ClawAVM")
    app.setApplicationVersion("1.0.0")
    
    from claw_avm import ClawSecureVirtualBoxEngine
    
    # 默认使用 VirtualBox 引擎
    workspace = Path.home() / "ClawAVM" / "workspace"
    engine = ClawSecureVirtualBoxEngine(workspace_path=workspace)
    
    window = ClawSecureMainWindow(engine)
    window.show()
    
    sys.exit(app.exec())

__all__ = ["ClawSecureMainWindow", "SecurityDashboard", "CreateVMWizard", "main"]
