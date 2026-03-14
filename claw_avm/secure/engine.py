"""
Claw Secure Engine - 安全引擎抽象基类

定义虚拟机安全管理的标准接口，所有虚拟化引擎必须继承此类。
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum, auto
from typing import Optional, List, Dict, Any
from pathlib import Path


class VMStatus(Enum):
    """虚拟机状态枚举"""
    POWERED_OFF = auto()
    POWERED_ON = auto()
    SUSPENDED = auto()
    CREATING = auto()
    ERROR = auto()
    SECURE_ISOLATED = auto()  # 安全隔离模式


@dataclass
class SecuritySnapshot:
    """安全快照数据类"""
    id: str
    name: str
    created_at: datetime
    description: str
    is_clean: bool = True  # 是否为干净状态（无恶意软件）
    

@dataclass  
class VMConfig:
    """虚拟机配置"""
    name: str
    memory_mb: int = 4096
    cpu_cores: int = 2
    disk_gb: int = 50
    network_isolated: bool = True  # 网络隔离
    clipboard_shared: bool = False  # 剪贴板共享关闭
    drag_drop_enabled: bool = False  # 拖放禁用
    

class ClawSecureEngine(ABC):
    """
    安全虚拟化引擎抽象基类
    
    所有虚拟化实现（VMware/VirtualBox/Hyper-V）必须继承此类
    并提供具体实现。
    """
    
    def __init__(self, workspace_path: Path):
        self.workspace = Path(workspace_path)
        self.workspace.mkdir(parents=True, exist_ok=True)
        self._active_vms: Dict[str, Any] = {}
        
    @abstractmethod
    def create_secure_vm(self, config: VMConfig) -> str:
        """
        创建一个安全的虚拟机
        
        Args:
            config: 虚拟机配置
            
        Returns:
            vm_id: 虚拟机唯一标识符
        """
        pass
    
    @abstractmethod
    def start_vm(self, vm_id: str) -> bool:
        """
        启动虚拟机
        
        Args:
            vm_id: 虚拟机ID
            
        Returns:
            bool: 是否成功启动
        """
        pass
    
    @abstractmethod
    def stop_vm(self, vm_id: str, force: bool = False) -> bool:
        """
        停止虚拟机
        
        Args:
            vm_id: 虚拟机ID
            force: 是否强制关机
            
        Returns:
            bool: 是否成功停止
        """
        pass
    
    @abstractmethod
    def get_vm_status(self, vm_id: str) -> VMStatus:
        """
        获取虚拟机状态
        
        Args:
            vm_id: 虚拟机ID
            
        Returns:
            VMStatus: 当前状态
        """
        pass
    
    @abstractmethod
    def create_security_snapshot(self, vm_id: str, name: str, 
                                  description: str = "") -> SecuritySnapshot:
        """
        创建安全快照
        
        Args:
            vm_id: 虚拟机ID
            name: 快照名称
            description: 快照描述
            
        Returns:
            SecuritySnapshot: 快照对象
        """
        pass
    
    @abstractmethod
    def restore_snapshot(self, vm_id: str, snapshot_id: str) -> bool:
        """
        恢复快照
        
        Args:
            vm_id: 虚拟机ID
            snapshot_id: 快照ID
            
        Returns:
            bool: 是否成功恢复
        """
        pass
    
    @abstractmethod
    def clone_vm(self, source_vm_id: str, new_name: str) -> str:
        """
        克隆虚拟机
        
        Args:
            source_vm_id: 源虚拟机ID
            new_name: 新虚拟机名称
            
        Returns:
            str: 新虚拟机ID
        """
        pass
    
    @abstractmethod
    def delete_vm(self, vm_id: str) -> bool:
        """
        删除虚拟机
        
        Args:
            vm_id: 虚拟机ID
            
        Returns:
            bool: 是否成功删除
        """
        pass
    
    @abstractmethod
    def list_vms(self) -> List[Dict[str, Any]]:
        """
        列出所有虚拟机
        
        Returns:
            List[Dict]: 虚拟机列表
        """
        pass
    
    def is_vm_secure(self, vm_id: str) -> bool:
        """
        检查虚拟机是否处于安全隔离状态
        
        Args:
            vm_id: 虚拟机ID
            
        Returns:
            bool: 是否安全隔离
        """
        status = self.get_vm_status(vm_id)
        return status == VMStatus.SECURE_ISOLATED
    
    def get_workspace_info(self) -> Dict[str, Any]:
        """获取工作区信息"""
        return {
            "path": str(self.workspace),
            "exists": self.workspace.exists(),
            "active_vms": len(self._active_vms)
        }
