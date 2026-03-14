"""
Claw VMware Engine - VMware 虚拟化引擎实现

基于 VMware Workstation/Player 的虚拟化管理实现
支持 VIX API 和 vmrun 命令行工具
"""

import subprocess
import json
import uuid
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
import logging

from ..secure.engine import (
    ClawSecureEngine, VMStatus, SecuritySnapshot, VMConfig
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ClawSecureVMwareEngine(ClawSecureEngine):
    """
    VMware 安全虚拟化引擎
    
    功能特性：
    - 创建隔离的虚拟机环境
    - 管理 VM 生命周期（启动/停止/暂停）
    - 安全快照管理
    - 虚拟机克隆
    - 网络隔离控制
    """
    
    def __init__(self, workspace_path: Path, vmrun_path: Optional[str] = None):
        super().__init__(workspace_path)
        
        # vmrun 工具路径
        self.vmrun = vmrun_path or self._find_vmrun()
        
        # VMware 虚拟机目录
        self.vm_dir = self.workspace / "vmachines"
        self.vm_dir.mkdir(exist_ok=True)
        
        # 快照存储目录
        self.snapshot_dir = self.workspace / "snapshots"
        self.snapshot_dir.mkdir(exist_ok=True)
        
        # 虚拟机注册表
        self._registry_file = self.workspace / "vm_registry.json"
        self._registry = self._load_registry()
        
        logger.info(f"VMware Engine initialized at {self.workspace}")
    
    def _find_vmrun(self) -> str:
        """查找 vmrun 可执行文件"""
        # 常见 VMware 安装路径
        possible_paths = [
            "/usr/bin/vmrun",
            "/usr/local/bin/vmrun",
            r"C:\Program Files (x86)\VMware\VMware Workstation\vmrun.exe",
            r"C:\Program Files\VMware\VMware Workstation\vmrun.exe",
        ]
        
        for path in possible_paths:
            if shutil.which(path) or Path(path).exists():
                return path
        
        # 尝试系统 PATH
        vmrun = shutil.which("vmrun")
        if vmrun:
            return vmrun
            
        logger.warning("vmrun not found, some features may be limited")
        return "vmrun"  # 默认尝试命令
    
    def _load_registry(self) -> Dict[str, Any]:
        """加载虚拟机注册表"""
        if self._registry_file.exists():
            with open(self._registry_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_registry(self):
        """保存虚拟机注册表"""
        with open(self._registry_file, 'w') as f:
            json.dump(self._registry, f, indent=2)
    
    def _run_vmrun(self, args: List[str]) -> tuple[bool, str]:
        """
        执行 vmrun 命令
        
        Args:
            args: vmrun 参数列表
            
        Returns:
            (success, output): 执行结果和输出
        """
        cmd = [self.vmrun] + args
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=60
            )
            if result.returncode == 0:
                return True, result.stdout
            else:
                logger.error(f"vmrun error: {result.stderr}")
                return False, result.stderr
        except subprocess.TimeoutExpired:
            return False, "Command timed out"
        except Exception as e:
            return False, str(e)
    
    def _get_vmx_path(self, vm_id: str) -> Optional[Path]:
        """获取虚拟机 VMX 文件路径"""
        vm_info = self._registry.get(vm_id)
        if vm_info:
            return Path(vm_info.get("vmx_path"))
        return None
    
    # ============ 核心方法实现 ============
    
    def create_secure_vm(self, config: VMConfig) -> str:
        """
        创建安全虚拟机
        
        Args:
            config: VM 配置
            
        Returns:
            vm_id: 虚拟机唯一ID
        """
        vm_id = str(uuid.uuid4())[:8]
        vm_path = self.vm_dir / f"{config.name}_{vm_id}"
        vm_path.mkdir(exist_ok=True)
        
        vmx_path = vm_path / f"{config.name}.vmx"
        
        # 生成 VMX 配置文件
        vmx_content = self._generate_secure_vmx(config, vm_path)
        with open(vmx_path, 'w') as f:
            f.write(vmx_content)
        
        # 注册虚拟机
        self._registry[vm_id] = {
            "id": vm_id,
            "name": config.name,
            "vmx_path": str(vmx_path),
            "config": {
                "memory_mb": config.memory_mb,
                "cpu_cores": config.cpu_cores,
                "disk_gb": config.disk_gb,
                "network_isolated": config.network_isolated,
            },
            "created_at": datetime.now().isoformat(),
            "status": "created"
        }
        self._save_registry()
        
        logger.info(f"Created secure VM: {config.name} (ID: {vm_id})")
        return vm_id
    
    def _generate_secure_vmx(self, config: VMConfig, vm_path: Path) -> str:
        """生成安全隔离的 VMX 配置"""
        
        # 基础配置
        vmx_lines = [
            '# ClawAVM Secure VM Configuration',
            f'displayName = "{config.name}"',
            f'guestOS = "ubuntu-64"',
            f'memsize = "{config.memory_mb}"',
            f'numvcpus = "{config.cpu_cores}"',
            '',
            '# Security Isolation Settings',
            'isolation.tools.hgfs.disable = "TRUE"',  # 禁用共享文件夹
            'isolation.tools.dnd.disable = "TRUE"',   # 禁用拖放
            'isolation.tools.copy.disable = "TRUE"',  # 禁用复制粘贴
            'isolation.tools.paste.disable = "TRUE"',
            '',
            '# Network Settings',
        ]
        
        # 网络隔离
        if config.network_isolated:
            vmx_lines.extend([
                'ethernet0.connectionType = "hostonly"',  # 仅主机模式
                'ethernet0.present = "TRUE"',
            ])
        
        # USB 禁用
        vmx_lines.extend([
            '',
            '# USB Security',
            'usb.present = "FALSE"',
            'usb.generic.autoconnect = "FALSE"',
        ])
        
        # 磁盘配置
        vmdk_path = vm_path / f"{config.name}.vmdk"
        vmx_lines.extend([
            '',
            '# Disk Configuration',
            f'scsi0.present = "TRUE"',
            f'scsi0:0.fileName = "{vmdk_path.name}"',
            f'scsi0:0.present = "TRUE"',
        ])
        
        return '\n'.join(vmx_lines)
    
    def start_vm(self, vm_id: str) -> bool:
        """启动虚拟机"""
        vmx_path = self._get_vmx_path(vm_id)
        if not vmx_path or not vmx_path.exists():
            logger.error(f"VM not found: {vm_id}")
            return False
        
        success, output = self._run_vmrun(["start", str(vmx_path), "nogui"])
        
        if success:
            self._registry[vm_id]["status"] = "running"
            self._save_registry()
            self._active_vms[vm_id] = {"started_at": datetime.now()}
            logger.info(f"Started VM: {vm_id}")
        else:
            logger.error(f"Failed to start VM {vm_id}: {output}")
        
        return success
    
    def stop_vm(self, vm_id: str, force: bool = False) -> bool:
        """停止虚拟机"""
        vmx_path = self._get_vmx_path(vm_id)
        if not vmx_path:
            return False
        
        if force:
            success, output = self._run_vmrun(["stop", str(vmx_path), "hard"])
        else:
            success, output = self._run_vmrun(["stop", str(vmx_path)])
        
        if success:
            self._registry[vm_id]["status"] = "stopped"
            self._save_registry()
            self._active_vms.pop(vm_id, None)
            logger.info(f"Stopped VM: {vm_id}")
        
        return success
    
    def get_vm_status(self, vm_id: str) -> VMStatus:
        """获取虚拟机状态"""
        vmx_path = self._get_vmx_path(vm_id)
        if not vmx_path:
            return VMStatus.ERROR
        
        success, output = self._run_vmrun(["list"])
        
        if not success:
            return VMStatus.ERROR
        
        # 检查 vmx 是否在运行列表中
        if str(vmx_path) in output:
            # 检查是否安全隔离
            vm_info = self._registry.get(vm_id, {})
            config = vm_info.get("config", {})
            if config.get("network_isolated", True):
                return VMStatus.SECURE_ISOLATED
            return VMStatus.POWERED_ON
        
        # 检查注册表状态
        status = self._registry.get(vm_id, {}).get("status", "unknown")
        if status == "suspended":
            return VMStatus.SUSPENDED
        
        return VMStatus.POWERED_OFF
    
    def create_security_snapshot(self, vm_id: str, name: str, 
                                  description: str = "") -> SecuritySnapshot:
        """创建安全快照"""
        vmx_path = self._get_vmx_path(vm_id)
        if not vmx_path:
            raise ValueError(f"VM not found: {vm_id}")
        
        snapshot_id = str(uuid.uuid4())[:8]
        
        # 创建快照（使用 VMware snapshot 功能）
        success, output = self._run_vmrun([
            "snapshot", str(vmx_path), name
        ])
        
        if not success:
            raise RuntimeError(f"Failed to create snapshot: {output}")
        
        snapshot = SecuritySnapshot(
            id=snapshot_id,
            name=name,
            created_at=datetime.now(),
            description=description,
            is_clean=True  # 默认认为是干净快照
        )
        
        # 保存快照元数据
        snapshot_file = self.snapshot_dir / f"{vm_id}_{snapshot_id}.json"
        with open(snapshot_file, 'w') as f:
            json.dump({
                "id": snapshot_id,
                "name": name,
                "description": description,
                "created_at": snapshot.created_at.isoformat(),
                "is_clean": snapshot.is_clean,
                "vm_id": vm_id
            }, f, indent=2)
        
        logger.info(f"Created snapshot '{name}' for VM {vm_id}")
        return snapshot
    
    def restore_snapshot(self, vm_id: str, snapshot_id: str) -> bool:
        """恢复快照"""
        vmx_path = self._get_vmx_path(vm_id)
        if not vmx_path:
            return False
        
        # 加载快照元数据获取名称
        snapshot_file = self.snapshot_dir / f"{vm_id}_{snapshot_id}.json"
        if not snapshot_file.exists():
            logger.error(f"Snapshot metadata not found: {snapshot_id}")
            return False
        
        with open(snapshot_file, 'r') as f:
            metadata = json.load(f)
        
        snapshot_name = metadata.get("name", "")
        
        success, output = self._run_vmrun([
            "revertToSnapshot", str(vmx_path), snapshot_name
        ])
        
        if success:
            logger.info(f"Restored snapshot '{snapshot_name}' for VM {vm_id}")
        else:
            logger.error(f"Failed to restore snapshot: {output}")
        
        return success
    
    def clone_vm(self, source_vm_id: str, new_name: str) -> str:
        """克隆虚拟机"""
        source_vmx = self._get_vmx_path(source_vm_id)
        if not source_vmx or not source_vmx.exists():
            raise ValueError(f"Source VM not found: {source_vm_id}")
        
        # 创建新的 VM ID
        new_vm_id = str(uuid.uuid4())[:8]
        new_vm_path = self.vm_dir / f"{new_name}_{new_vm_id}"
        new_vm_path.mkdir(exist_ok=True)
        
        new_vmx_path = new_vm_path / f"{new_name}.vmx"
        
        # 使用 vmrun clone 功能
        success, output = self._run_vmrun([
            "clone", str(source_vmx), str(new_vmx_path), "full"
        ])
        
        if not success:
            # 如果 vmrun clone 失败，尝试手动复制配置
            logger.warning("vmrun clone failed, falling back to manual copy")
            self._manual_clone(source_vmx, new_vmx_path, new_vm_path, new_name)
        
        # 注册新 VM
        source_config = self._registry.get(source_vm_id, {}).get("config", {})
        self._registry[new_vm_id] = {
            "id": new_vm_id,
            "name": new_name,
            "vmx_path": str(new_vmx_path),
            "config": source_config.copy(),
            "created_at": datetime.now().isoformat(),
            "status": "created",
            "cloned_from": source_vm_id
        }
        self._save_registry()
        
        logger.info(f"Cloned VM {source_vm_id} -> {new_name} (ID: {new_vm_id})")
        return new_vm_id
    
    def _manual_clone(self, source_vmx: Path, new_vmx: Path, 
                      new_vm_path: Path, new_name: str):
        """手动克隆 VMX 配置"""
        with open(source_vmx, 'r') as f:
            content = f.read()
        
        # 替换虚拟机名称
        content = content.replace(
            f'displayName = "', 
            f'displayName = "{new_name} (Clone) '
        )
        
        with open(new_vmx, 'w') as f:
            f.write(content)
    
    def delete_vm(self, vm_id: str) -> bool:
        """删除虚拟机"""
        vmx_path = self._get_vmx_path(vm_id)
        if not vmx_path:
            return False
        
        # 先停止 VM
        self.stop_vm(vm_id, force=True)
        
        # 删除 VM 文件
        vm_path = vmx_path.parent
        try:
            import shutil as sh
            sh.rmtree(vm_path)
        except Exception as e:
            logger.error(f"Failed to delete VM files: {e}")
            return False
        
        # 从注册表移除
        del self._registry[vm_id]
        self._save_registry()
        
        # 清理相关快照
        for snapshot_file in self.snapshot_dir.glob(f"{vm_id}_*.json"):
            snapshot_file.unlink()
        
        logger.info(f"Deleted VM: {vm_id}")
        return True
    
    def list_vms(self) -> List[Dict[str, Any]]:
        """列出所有虚拟机"""
        vms = []
        for vm_id, info in self._registry.items():
            status = self.get_vm_status(vm_id)
            vms.append({
                "id": vm_id,
                "name": info.get("name"),
                "status": status.name,
                "created_at": info.get("created_at"),
                "vmx_path": info.get("vmx_path")
            })
        return vms
    
    # ============ 额外安全功能 ============
    
    def isolate_vm_network(self, vm_id: str) -> bool:
        """将虚拟机网络完全隔离"""
        vmx_path = self._get_vmx_path(vm_id)
        if not vmx_path:
            return False
        
        # 修改 VMX 配置禁用网络
        with open(vmx_path, 'r') as f:
            lines = f.readlines()
        
        # 添加网络隔离配置
        network_config = [
            '\n# Emergency Network Isolation\n',
            'ethernet0.present = "FALSE"\n',
            'ethernet0.startConnected = "FALSE"\n'
        ]
        
        with open(vmx_path, 'a') as f:
            f.writelines(network_config)
        
        logger.info(f"Network isolated for VM: {vm_id}")
        return True
    
    def scan_vm_for_malware(self, vm_id: str) -> Dict[str, Any]:
        """
        扫描虚拟机文件系统（占位实现）
        
        实际实现需要集成杀毒引擎或文件扫描工具
        """
        return {
            "vm_id": vm_id,
            "scan_time": datetime.now().isoformat(),
            "status": "not_implemented",
            "message": "Malware scanning requires integration with AV engine"
        }
