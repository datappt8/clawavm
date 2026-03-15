"""
ClawAVM - Claw Anti-Virus Manager
安全虚拟化管理器

一个基于 Python 的虚拟机安全管理系统，支持 VMware 虚拟化引擎。
提供安全的沙箱环境用于分析可疑文件和恶意软件。
"""

__version__ = "1.0.0"
__author__ = "Kimi Claw"
__license__ = "MIT"

from claw_avm.secure.engine import ClawSecureEngine, VMStatus
from claw_avm.engine.vmware import ClawSecureVMwareEngine
from claw_avm.engine.vmware_fusion import ClawSecureVMwareFusionEngine
from claw_avm.engine.virtualbox import ClawSecureVirtualBoxEngine

__all__ = [
    "ClawSecureEngine",
    "ClawSecureVMwareEngine",
    "ClawSecureVMwareFusionEngine",
    "ClawSecureVirtualBoxEngine",
    "VMStatus",
    "__version__"
]
