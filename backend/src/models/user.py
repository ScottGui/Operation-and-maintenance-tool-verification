"""
用户模型
定义系统用户的基本信息和认证相关字段
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.src.database import Base


class User(Base):
    """
    用户表
    存储系统所有用户的基本信息
    """
    __tablename__ = "user"
    
    # 主键
    id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="用户ID")
    
    # 基本信息
    username = Column(String(50), unique=True, nullable=False, index=True, comment="用户名")
    password_hash = Column(String(255), nullable=False, comment="密码哈希")
    real_name = Column(String(50), nullable=False, comment="真实姓名")
    email = Column(String(100), unique=True, nullable=True, comment="邮箱")
    phone = Column(String(20), nullable=True, comment="手机号")
    
    # 组织架构
    department_id = Column(Integer, ForeignKey("department.id"), nullable=True, comment="部门ID")
    department = relationship("Department", back_populates="users")
    
    # 状态管理
    is_active = Column(Boolean, default=True, comment="是否启用")
    is_deleted = Column(Boolean, default=False, comment="是否删除（软删除）")
    
    # 时间戳
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    deleted_at = Column(DateTime, nullable=True, comment="删除时间")
    
    # 最后登录信息
    last_login_at = Column(DateTime, nullable=True, comment="最后登录时间")
    last_login_ip = Column(String(50), nullable=True, comment="最后登录IP")
    
    # 关联关系
    roles = relationship("Role", secondary="user_role", back_populates="users")
    created_work_orders = relationship("WorkOrder", foreign_keys="WorkOrder.created_by", back_populates="creator")
    assigned_work_orders = relationship("WorkOrder", foreign_keys="WorkOrder.assignee_id", back_populates="assignee")
    work_order_flows = relationship("WorkOrderFlow", back_populates="operator")
    
    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, real_name={self.real_name})>"
    
    def to_dict(self):
        """转换为字典格式（不包含敏感信息）"""
        return {
            "id": self.id,
            "username": self.username,
            "real_name": self.real_name,
            "email": self.email,
            "phone": self.phone,
            "department_id": self.department_id,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_login_at": self.last_login_at.isoformat() if self.last_login_at else None,
        }


class Department(Base):
    """
    部门表
    组织架构信息
    """
    __tablename__ = "department"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="部门ID")
    name = Column(String(100), nullable=False, comment="部门名称")
    code = Column(String(50), unique=True, nullable=False, comment="部门编码")
    parent_id = Column(Integer, ForeignKey("department.id"), nullable=True, comment="上级部门ID")
    description = Column(Text, nullable=True, comment="部门描述")
    sort_order = Column(Integer, default=0, comment="排序")
    
    # 状态
    is_active = Column(Boolean, default=True, comment="是否启用")
    
    # 时间戳
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关联关系
    users = relationship("User", back_populates="department")
    children = relationship("Department", backref="parent", remote_side=[id])
    
    def __repr__(self):
        return f"<Department(id={self.id}, name={self.name}, code={self.code})>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "code": self.code,
            "parent_id": self.parent_id,
            "description": self.description,
            "sort_order": self.sort_order,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
