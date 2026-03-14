"""
Claw VirtualBox Engine - VirtualBox 虚拟化引擎实现

基于 VirtualBox VBoxManage 命令行工具的虚拟化管理实现
支持 Windows/Linux/Mac
"""

import subprocess
import json
import uuid
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
import logging
import re

from ..secure.engine import (
    ClawSecureEngine, VMStatus, SecuritySnapshot, VMConfig
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ClawSecureVirtualBoxEngine(ClawSecureEngine):
    """
    VirtualBox 安全虚拟化引擎
    
    功能特性：
    - 创建隔离的虚拟机环境
    - 管理 VM 生命周期（启动/停止/暂停）
    - 安全快照管理
    - 虚拟机克隆
    - 网络隔离控制
    """
    
    def __init__(self, workspace_path: Path, vboxmanage_path: Optional[str] = None):
        super().__init__(workspace_path)
        
        # VBoxManage 工具路径
        self.vboxmanage = vboxmanage_path or self._find_vboxmanage()
        
        # VirtualBox 虚拟机目录
        self.vm_dir = self.workspace / "vmachines"
        self.vm_dir.mkdir(exist_ok=True)
        
        # 快照存储目录（VBoxManage 自带快照，这里存元数据）
        self.snapshot_dir = self.workspace / "snapshots"
        self.snapshot_dir.mkdir(exist_ok=True)
        
        # 虚拟机注册表
        self._registry_file = self.workspace / "vm_registry.json"
        self._registry = self._load_registry()
        
        logger.info(f"VirtualBox Engine initialized at {self.workspace}")
    
    def _find_vboxmanage(self) -> str:
        """查找 VBoxManage 可执行文件"""
        # 常见 VirtualBox 安装路径
        possible_paths = [
            "/usr/bin/VBoxManage",
            "/usr/local/bin/VBoxManage",
            r"C:\Program Files\Oracle\VirtualBox\VBoxManage.exe",
            r"C:\Program Files (x86)\Oracle\VirtualBox\VBoxManage.exe",
        ]
        
        for path in possible_paths:
            if shutil.which(path) or Path(path).exists():
                return path
        
        # 尝试系统 PATH
        vboxmanage = shutil.which("VBoxManage")
        if vboxmanage:
            return vboxmanage
            
        logger.warning("VBoxManage not found, some features may be limited")
        return "VBoxManage"  # 默认尝试命令
    
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
    
    def _run_vboxmanage(self, args: List[str], timeout: int = 120) -> tuple[bool, str]:
        """
        执行 VBoxManage 命令
        
        Args:
            args: VBoxManage 参数列表
            timeout: 超时时间（秒）
            
        Returns:
            (success, output): 执行结果和输出
        """
        cmd = [self.vboxmanage] + args
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=timeout
            )
            # VBoxManage 某些成功操作也会输出到 stderr
            output = result.stdout if result.stdout else result.stderr
            if result.returncode == 0:
                return True, output
            else:
                logger.error(f"VBoxManage error: {result.stderr}")
                return False, result.stderr
        except subprocess.TimeoutExpired:
            return False, "Command timed out"
        except Exception as e:
            return False, str(e)
    
    def _get_vm_name(self, vm_id: str) -> Optional[str]:
        """获取虚拟机 VirtualBox 名称"""
        vm_info = self._registry.get(vm_id)
        if vm_info:
            return vm_info.get("vbox_name")
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
        vbox_name = f"{config.name}_{vm_id}"
        
        # VM 文件路径
        vm_path = self.vm_dir / vbox_name
        vm_path.mkdir(exist_ok=True)
        
        vdi_path = vm_path / f"{config.name}.vdi"
        
        # 1. 创建虚拟机
        success, output = self._run_vboxmanage([
            "createvm", "--name", vbox_name,
            "--ostype", "Ubuntu_64",
            "--register"
        ])
        
        if not success:
            raise RuntimeError(f"Failed to create VM: {output}")
        
        # 2. 设置基础配置（内存、CPU）
        success, output = self._run_vboxmanage([
            "modifyvm", vbox_name,
            "--memory", str(config.memory_mb),
            "--cpus", str(config.cpu_cores),
            "--vram", "16",
            "--acpi", "on",
            "--ioapic", "on"
        ])
        
        if not success:
            # 清理失败的 VM
            self._run_vboxmanage(["unregistervm", vbox_name, "--delete"])
            raise RuntimeError(f"Failed to configure VM: {output}")
        
        # 3. 创建虚拟硬盘
        success, output = self._run_vboxmanage([
            "createhd", "--filename", str(vdi_path),
            "--size", str(config.disk_gb * 1024)  # MB
        ])
        
        if not success:
            self._run_vboxmanage(["unregistervm", vbox_name, "--delete"])
            raise RuntimeError(f"Failed to create disk: {output}")
        
        # 4. 添加 SATA 控制器和硬盘
        success, output = self._run_vboxmanage([
            "storagectl", vbox_name,
            "--name", "SATA",
            "--add", "sata",
            "--controller", "IntelAhci"
        ])
        
        if not success:
            self._run_vboxmanage(["unregistervm", vbox_name, "--delete"])
            raise RuntimeError(f"Failed to add storage controller: {output}")
        
        success, output = self._run_vboxmanage([
            "storageattach", vbox_name,
            "--storagectl", "SATA",
            "--port", "0",
            "--device", "0",
            "--type", "hdd",
            "--medium", str(vdi_path)
        ])
        
        if not success:
            self._run_vboxmanage(["unregistervm", vbox_name, "--delete"])
            raise RuntimeError(f"Failed to attach disk: {output}")
        
        # 5. 应用安全隔离配置
        self._apply_security_config(vbox_name, config)
        
        # 注册虚拟机
        self._registry[vm_id] = {
            "id": vm_id,
            "name": config.name,
            "vbox_name": vbox_name,
            "vm_path": str(vm_path),
            "vdi_path": str(vdi_path),
            "config": {
                "memory_mb": config.memory_mb,
                "cpu_cores": config.cpu_cores,
                "disk_gb": config.disk_gb,
                "network_isolated": config.network_isolated,
                "clipboard_shared": config.clipboard_shared,
                "drag_drop_enabled": config.drag_drop_enabled
            },
            "created_at": datetime.now().isoformat(),
            "status": "created"
        }
        self._save_registry()
        
        logger.info(f"Created secure VM: {config.name} (ID: {vm_id})")
        return vm_id
    
    def _apply_security_config(self, vbox_name: str, config: VMConfig):
        """应用安全隔离配置"""
        
        # 网络隔离配置
        if config.network_isolated:
            # 仅主机网络模式（Host-Only）
            success, output = self._run_vboxmanage([
                "modifyvm", vbox_name,
                "--nic1", "hostonly",
                "--hostonlyadapter1", "vboxnet0"
            ])
            if not success:
                # 如果没有 host-only 适配器，使用内部网络
                self._run_vboxmanage([
                    "modifyvm", vbox_name,
                    "--nic1", "intnet",
                    "--intnet1", "isolated"
                ])
        
        # 禁用剪贴板共享
        clipboard_mode = "bidirectional" if config.clipboard_shared else "disabled"
        self._run_vboxmanage([
            "modifyvm", vbox_name,
            "--clipboard", clipboard_mode
        ])
        
        # 禁用拖放
        dnd_mode = "bidirectional" if config.drag_drop_enabled else "disabled"
        self._run_vboxmanage([
            "modifyvm", vbox_name,
            "--draganddrop", dnd_mode
        ])
        
        # 禁用 USB
        self._run_vboxmanage([
            "modifyvm", vbox_name,
            "--usb", "off",
            "--usbehci", "off",
            "--usbxhci", "off"
        ])
        
        # 禁用音频（减少攻击面）
        self._run_vboxmanage([
            "modifyvm", vbox_name,
            "--audio", "none"
        ])
    
    def start_vm(self, vm_id: str) -> bool:
        """启动虚拟机"""
        vbox_name = self._get_vm_name(vm_id)
        if not vbox_name:
            logger.error(f"VM not found in registry: {vm_id}")
            return False
        
        # 检查 VM 是否存在
        success, output = self._run_vboxmanage(["showvminfo", vbox_name])
        if not success:
            logger.error(f"VM not found in VirtualBox: {vbox_name}")
            return False
        
        # 启动 VM（无界面模式）
        success, output = self._run_vboxmanage([
            "startvm", vbox_name,
            "--type", "headless"
        ])
        
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
        vbox_name = self._get_vm_name(vm_id)
        if not vbox_name:
            return False
        
        if force:
            success, output = self._run_vboxmanage([
                "controlvm", vbox_name, "poweroff"
            ])
        else:
            success, output = self._run_vboxmanage([
                "controlvm", vbox_name, "acpipowerbutton"
            ])
        
        if success:
            self._registry[vm_id]["status"] = "stopped"
            self._save_registry()
            self._active_vms.pop(vm_id, None)
            logger.info(f"Stopped VM: {vm_id}")
        
        return success
    
    def get_vm_status(self, vm_id: str) -> VMStatus:
        """获取虚拟机状态"""
        vbox_name = self._get_vm_name(vm_id)
        if not vbox_name:
            return VMStatus.ERROR
        
        success, output = self._run_vboxmanage(["showvminfo", vbox_name])
        
        if not success:
            return VMStatus.ERROR
        
        # 解析状态
        state_match = re.search(r'State:\s+(\S.+)', output)
        if state_match:
            state_str = state_match.group(1).lower()
            
            if "running" in state_str:
                # 检查是否安全隔离
                vm_info = self._registry.get(vm_id, {})
                config = vm_info.get("config", {})
                if config.get("network_isolated", True):
                    return VMStatus.SECURE_ISOLATED
                return VMStatus.POWERED_ON
            elif "powered off" in state_str or "aborted" in state_str:
                return VMStatus.POWERED_OFF
            elif "paused" in state_str or "saved" in state_str:
                return VMStatus.SUSPENDED
        
        return VMStatus.ERROR
    
    def create_security_snapshot(self, vm_id: str, name: str, 
                                  description: str = "") -> SecuritySnapshot:
        """创建安全快照"""
        vbox_name = self._get_vm_name(vm_id)
        if not vbox_name:
            raise ValueError(f"VM not found: {vm_id}")
        
        snapshot_id = str(uuid.uuid4())[:8]
        
        # 创建 VirtualBox 快照
        success, output = self._run_vboxmanage([
            "snapshot", vbox_name, "take", name,
            "--description", description or f"ClawAVM snapshot {snapshot_id}"
        ])
        
        if not success:
            raise RuntimeError(f"Failed to create snapshot: {output}")
        
        # 获取 VirtualBox 生成的快照 UUID
        vbox_snapshot_uuid = None
        snap_match = re.search(r'UUID:\s+([0-9a-f-]{36})', output)
        if snap_match:
            vbox_snapshot_uuid = snap_match.group(1)
        
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
                "vbox_snapshot_uuid": vbox_snapshot_uuid,
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
        vbox_name = self._get_vm_name(vm_id)
        if not vbox_name:
            return False
        
        # 加载快照元数据
        snapshot_file = self.snapshot_dir / f"{vm_id}_{snapshot_id}.json"
        if not snapshot_file.exists():
            logger.error(f"Snapshot metadata not found: {snapshot_id}")
            # 尝试直接用名称恢复
            return self._restore_by_name(vbox_name, snapshot_id)
        
        with open(snapshot_file, 'r') as f:
            metadata = json.load(f)
        
        snapshot_name = metadata.get("name", "")
        return self._restore_by_name(vbox_name, snapshot_name)
    
    def _restore_by_name(self, vbox_name: str, snapshot_name: str) -> bool:
        """通过名称恢复快照"""
        success, output = self._run_vboxmanage([
            "snapshot", vbox_name, "restore", snapshot_name
        ])
        
        if success:
            logger.info(f"Restored snapshot '{snapshot_name}' for VM {vbox_name}")
        else:
            logger.error(f"Failed to restore snapshot: {output}")
        
        return success
    
    def clone_vm(self, source_vm_id: str, new_name: str) -> str:
        """克隆虚拟机"""
        source_vbox_name = self._get_vm_name(source_vm_id)
        if not source_vbox_name:
            raise ValueError(f"Source VM not found: {source_vm_id}")
        
        # 创建新的 VM ID
        new_vm_id = str(uuid.uuid4())[:8]
        new_vbox_name = f"{new_name}_{new_vm_id}"
        
        # 使用 VBoxManage clonevm
        success, output = self._run_vboxmanage([
            "clonevm", source_vbox_name,
            "--name", new_vbox_name,
            "--register"
        ])
        
        if not success:
            raise RuntimeError(f"Failed to clone VM: {output}")
        
        # 注册新 VM
        source_config = self._registry.get(source_vm_id, {}).get("config", {})
        self._registry[new_vm_id] = {
            "id": new_vm_id,
            "name": new_name,
            "vbox_name": new_vbox_name,
            "vm_path": str(self.vm_dir / new_vbox_name),
            "config": source_config.copy(),
            "created_at": datetime.now().isoformat(),
            "status": "created",
            "cloned_from": source_vm_id
        }
        self._save_registry()
        
        logger.info(f"Cloned VM {source_vm_id} -> {new_name} (ID: {new_vm_id})")
        return new_vm_id
    
    def delete_vm(self, vm_id: str) -> bool:
        """删除虚拟机"""
        vbox_name = self._get_vm_name(vm_id)
        if not vbox_name:
            return False
        
        # 先停止 VM
        self.stop_vm(vm_id, force=True)
        
        # 注销并删除 VM
        success, output = self._run_vboxmanage([
            "unregistervm", vbox_name, "--delete"
        ])
        
        if success:
            # 从注册表移除
            if vm_id in self._registry:
                del self._registry[vm_id]
                self._save_registry()
            
            # 清理相关快照元数据
            for snapshot_file in self.snapshot_dir.glob(f"{vm_id}_*.json"):
                snapshot_file.unlink()
            
            logger.info(f"Deleted VM: {vm_id}")
        else:
            logger.error(f"Failed to delete VM {vm_id}: {output}")
        
        return success
    
    def list_vms(self) -> List[Dict[str, Any]]:
        """列出所有虚拟机"""
        vms = []
        for vm_id, info in self._registry.items():
            status = self.get_vm_status(vm_id)
            vms.append({
                "id": vm_id,
                "name": info.get("name"),
                "vbox_name": info.get("vbox_name"),
                "status": status.name,
                "created_at": info.get("created_at"),
                "vm_path": info.get("vm_path")
            })
        return vms
    
    # ============ 额外安全功能 ============
    
    def isolate_vm_network(self, vm_id: str) -> bool:
        """将虚拟机网络完全隔离"""
        vbox_name = self._get_vm_name(vm_id)
        if not vbox_name:
            return False
        
        # 禁用所有网络适配器
        for nic in range(1, 9):  # VirtualBox 支持 8 个网卡
            self._run_vboxmanage([
                "modifyvm", vbox_name,
                f"--nic{nic}", "none"
            ])
        
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
