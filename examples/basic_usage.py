#!/usr/bin/env python3
"""
ClawAVM 基础使用示例

演示如何：
1. 初始化 VMware 引擎
2. 创建安全虚拟机
3. 管理 VM 生命周期
4. 创建和恢复快照
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from claw_avm import ClawSecureVMwareEngine
from claw_avm.secure.engine import VMConfig, VMStatus


def main():
    print("🔒 ClawAVM - 安全虚拟化管理器")
    print("=" * 50)
    
    # 创建工作目录
    workspace = Path("./vm_workspace")
    workspace.mkdir(exist_ok=True)
    
    # 初始化引擎
    print("\n📦 初始化 VMware 引擎...")
    engine = ClawSecureVMwareEngine(workspace_path=workspace)
    print(f"✅ 引擎已初始化: {engine.workspace}")
    
    # 显示工作区信息
    info = engine.get_workspace_info()
    print(f"📁 工作区: {info['path']}")
    
    # 创建安全虚拟机
    print("\n🖥️ 创建安全虚拟机...")
    config = VMConfig(
        name="Sandbox-001",
        memory_mb=4096,
        cpu_cores=2,
        disk_gb=50,
        network_isolated=True,    # 启用网络隔离
        clipboard_shared=False,   # 禁用剪贴板共享
        drag_drop_enabled=False   # 禁用拖放
    )
    
    try:
        vm_id = engine.create_secure_vm(config)
        print(f"✅ 虚拟机创建成功!")
        print(f"   ID: {vm_id}")
        print(f"   名称: {config.name}")
        print(f"   内存: {config.memory_mb} MB")
        print(f"   CPU: {config.cpu_cores} 核")
    except Exception as e:
        print(f"❌ 创建失败: {e}")
        return
    
    # 列出现有虚拟机
    print("\n📋 虚拟机列表:")
    vms = engine.list_vms()
    for vm in vms:
        print(f"   • {vm['name']} ({vm['id']}) - 状态: {vm['status']}")
    
    # 检查 VM 状态
    print(f"\n🔍 VM 状态检查:")
    status = engine.get_vm_status(vm_id)
    print(f"   当前状态: {status.name}")
    print(f"   是否安全隔离: {engine.is_vm_secure(vm_id)}")
    
    # 创建安全快照
    print("\n📸 创建安全快照...")
    try:
        snapshot = engine.create_security_snapshot(
            vm_id=vm_id,
            name="CleanState-v1",
            description="干净的初始状态，用于恶意软件分析前的基准"
        )
        print(f"✅ 快照创建成功!")
        print(f"   ID: {snapshot.id}")
        print(f"   名称: {snapshot.name}")
        print(f"   干净状态: {snapshot.is_clean}")
    except Exception as e:
        print(f"⚠️ 快照创建受限（需要 VMware 安装）: {e}")
    
    # 克隆演示
    print("\n📋 克隆虚拟机...")
    try:
        cloned_id = engine.clone_vm(vm_id, "Sandbox-001-Clone")
        print(f"✅ 克隆成功! 新 VM ID: {cloned_id}")
    except Exception as e:
        print(f"⚠️ 克隆受限（需要 VMware 安装）: {e}")
    
    # 清理演示
    print("\n🧹 演示结束，清理资源...")
    # 实际使用中可以选择保留 VM
    # engine.delete_vm(vm_id)
    # print("✅ 虚拟机已删除")
    
    print("\n" + "=" * 50)
    print("✨ 演示完成!")
    print("\n提示:")
    print("  • 虚拟机文件位于: ./vm_workspace/vmachines/")
    print("  • 快照元数据位于: ./vm_workspace/snapshots/")
    print("  • 要使用完整功能，需要安装 VMware Workstation/Player")


if __name__ == "__main__":
    main()
