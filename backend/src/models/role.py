"""
角色模型
定义系统角色和权限管理
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Table, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.src.database import Base


# 用户角色关联表（多对多）
user_role = Table(
    "user_role",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("user.id"), primary_key=True, comment="用户ID"),
    Column("role_id", Integer, ForeignKey("role.id"), primary_key=True, comment="角色ID"),
    Column("created_at", DateTime, server_default=func.now(), comment="创建时间"),
)


class Role(Base):
    """
    角色表
    定义系统中的角色（运维管理经理、SRE运维工程师、运维需求方）
    """
    __tablename__ = "role"
    
    # 主键
    id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="角色ID")
    
    # 基本信息
    name = Column(String(50), unique=True, nullable=False, comment="角色名称")
    code = Column(String(50), unique=True, nullable=False, comment="角色编码")
    description = Column(Text, nullable=True, comment="角色描述")
    
    # 角色类型：admin-管理经理, sre-SRE工程师, requester-需求方
    role_type = Column(String(20), nullable=False, comment="角色类型")
    
    # 排序
    sort_order = Column(Integer, default=0, comment="排序")
    
    # 状态
    is_active = Column(Boolean, default=True, comment="是否启用")
    is_system = Column(Boolean, default=False, comment="是否系统内置角色")
    
    # 时间戳
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关联关系
    users = relationship("User", secondary=user_role, back_populates="roles")
    permissions = relationship("Permission", secondary="role_permission", back_populates="roles")
    
    def __repr__(self):
        return f"<Role(id={self.id}, name={self.name}, code={self.code})>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "code": self.code,
            "description": self.description,
            "role_type": self.role_type,
            "sort_order": self.sort_order,
            "is_active": self.is_active,
            "is_system": self.is_system,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Permission(Base):
    """
    权限表
    定义系统中的操作权限
    """
    __tablename__ = "permission"
    
    # 主键
    id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="权限ID")
    
    # 基本信息
    name = Column(String(50), nullable=False, comment="权限名称")
    code = Column(String(100), unique=True, nullable=False, comment="权限编码")
    description = Column(Text, nullable=True, comment="权限描述")
    
    # 权限类型：menu-菜单, button-按钮, api-接口, data-数据
    permission_type = Column(String(20), nullable=False, comment="权限类型")
    
    # 资源标识
    resource = Column(String(100), nullable=True, comment="资源标识")
    action = Column(String(50), nullable=True, comment="操作类型")
    
    # 父权限ID（用于菜单层级）
    parent_id = Column(Integer, ForeignKey("permission.id"), nullable=True, comment="父权限ID")
    
    # 排序
    sort_order = Column(Integer, default=0, comment="排序")
    
    # 状态
    is_active = Column(Boolean, default=True, comment="是否启用")
    
    # 时间戳
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关联关系
    roles = relationship("Role", secondary="role_permission", back_populates="permissions")
    children = relationship("Permission", backref="parent", remote_side=[id])
    
    def __repr__(self):
        return f"<Permission(id={self.id}, name={self.name}, code={self.code})>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "code": self.code,
            "description": self.description,
            "permission_type": self.permission_type,
            "resource": self.resource,
            "action": self.action,
            "parent_id": self.parent_id,
            "sort_order": self.sort_order,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


# 角色权限关联表（多对多）
role_permission = Table(
    "role_permission",
    Base.metadata,
    Column("role_id", Integer, ForeignKey("role.id"), primary_key=True, comment="角色ID"),
    Column("permission_id", Integer, ForeignKey("permission.id"), primary_key=True, comment="权限ID"),
    Column("created_at", DateTime, server_default=func.now(), comment="创建时间"),
)
