"""
模型初始化模块
导入所有模型并创建数据库表

MVP阶段：先只导入用户相关模型，其他模型后续按需导入
"""

from backend.src.database import Base, engine

# MVP阶段：先只导入用户相关模型（卡片015）
from backend.src.models.user import User, Department
from backend.src.models.file_attachment import FileAttachment
from backend.src.models.work_order import WorkOrder, work_order_attachment

# 所有模型列表
__all__ = [
    "User",
    "Department",
    "FileAttachment",
    "WorkOrder",
    "work_order_attachment",
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
