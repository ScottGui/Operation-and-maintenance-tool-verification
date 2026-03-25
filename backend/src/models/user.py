"""
用户模型
数据库表：users
按DB-STANDARD规范设计

业务规则：
- 7个角色：用数方、需求经理、运营方、项目经理、质量稽核经理、数据运维经理、四方组长
- 管理员角色不在前端选择中显示（后台标识）
- 密码使用bcrypt加密存储
- 支持软删除（is_deleted字段）

作者/日期：AI / 2026-03-24
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from backend.src.database import Base


class Department(Base):
    """
    部门表
    保留此表以兼容现有数据库结构，但MVP阶段暂不启用部门功能
    """
    __tablename__ = "department"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, comment="部门名称")
    code = Column(String(50), unique=True, nullable=False, comment="部门编码")
    parent_id = Column(Integer, ForeignKey("department.id"), nullable=True, comment="上级部门ID")
    description = Column(String(255), comment="描述")
    sort_order = Column(Integer, default=0, comment="排序")
    is_active = Column(Boolean, default=True, comment="是否启用")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # 自关联
    parent = relationship("Department", remote_side=[id], backref="children")


class User(Base):
    """
    用户表
    存储系统所有用户信息
    """
    __tablename__ = "users"
    
    # 主键
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # 登录信息
    username = Column(String(50), unique=True, nullable=False, index=True, comment="登录账号，字母数字")
    password_hash = Column(String(255), nullable=False, comment="bcrypt加密后的密码")
    
    # 用户信息
    real_name = Column(String(50), nullable=False, comment="真实姓名，中文")
    
    # 角色（7个角色）
    role = Column(String(50), nullable=False, index=True, comment="角色")
    
    # 账号状态
    status = Column(String(20), default="active", nullable=False, index=True, comment="状态：active启用/inactive禁用")
    
    # 最后登录时间
    last_login_at = Column(DateTime, nullable=True, comment="最后登录时间")
    
    # 审计字段（DB-STANDARD规范）
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    created_by = Column(Integer, nullable=True, comment="创建人ID（自关联，可为空）")
    is_deleted = Column(Boolean, default=False, comment="软删除标记")
    
    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, role={self.role})>"
    
    def to_dict(self):
        """转换为字典（不包含敏感字段）"""
        return {
            "id": self.id,
            "username": self.username,
            "real_name": self.real_name,
            "role": self.role,
            "status": self.status,
            "last_login_at": self.last_login_at.isoformat() if self.last_login_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "created_by": self.created_by,
        }
    
    def get_role_display(self):
        """获取角色显示名称"""
        role_map = {
            "data_consumer": "用数方",
            "requirement_manager": "需求经理",
            "operator": "运营方",
            "project_manager": "项目经理",
            "qa_manager": "质量稽核经理",
            "ops_manager": "数据运维经理",
            "team_lead": "四方组长",
            "admin": "管理员",
        }
        return role_map.get(self.role, self.role)
    
    def get_status_display(self):
        """获取状态显示名称"""
        status_map = {
            "active": "启用",
            "inactive": "禁用",
        }
        return status_map.get(self.status, self.status)
    
    def is_admin(self):
        """是否为管理员"""
        return self.role == "admin"


# 角色枚举（7个业务角色+管理员）
USER_ROLES = [
    ("data_consumer", "用数方"),
    ("requirement_manager", "需求经理"),
    ("operator", "运营方"),
    ("project_manager", "项目经理"),
    ("qa_manager", "质量稽核经理"),
    ("ops_manager", "数据运维经理"),
    ("team_lead", "四方组长"),
]

# 前端显示的角色（不包含管理员）
FRONTEND_ROLES = USER_ROLES

# 所有角色（包含管理员）
ALL_ROLES = USER_ROLES + [("admin", "管理员")]

# 状态枚举
USER_STATUS = [
    ("active", "启用"),
    ("inactive", "禁用"),
]
