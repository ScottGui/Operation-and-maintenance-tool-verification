"""
模型初始化模块
导入所有模型并创建数据库表
"""

from backend.src.database import Base, engine

# 导入所有模型（确保所有模型都被加载到 Base.metadata 中）
from backend.src.models.user import User, Department
from backend.src.models.role import Role, Permission, user_role, role_permission
from backend.src.models.work_order import WorkOrder, WorkOrderStatus, WorkOrderPriority, WorkOrderType
from backend.src.models.work_order_flow import WorkOrderFlow, OperationType
from backend.src.models.asset import Asset, AssetType, AssetStatus
from backend.src.models.service import Service, ServiceType, ServiceStatus, ServiceLevel


# 所有模型列表
__all__ = [
    # 用户相关
    "User",
    "Department",
    
    # 角色权限相关
    "Role",
    "Permission",
    "user_role",
    "role_permission",
    
    # 工单相关
    "WorkOrder",
    "WorkOrderStatus",
    "WorkOrderPriority",
    "WorkOrderType",
    "WorkOrderFlow",
    "OperationType",
    
    # 资产相关
    "Asset",
    "AssetType",
    "AssetStatus",
    
    # 服务相关
    "Service",
    "ServiceType",
    "ServiceStatus",
    "ServiceLevel",
]


def create_tables():
    """
    创建所有数据库表
    在应用启动时调用
    """
    Base.metadata.create_all(bind=engine)
    print("数据库表创建完成")


def drop_tables():
    """
    删除所有数据库表
    谨慎使用，仅用于开发测试
    """
    Base.metadata.drop_all(bind=engine)
    print("数据库表已删除")
