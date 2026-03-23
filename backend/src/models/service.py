"""
服务台账模型 (CMDB)
定义系统服务的基本信息和管理
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from backend.src.database import Base


class ServiceType(str, enum.Enum):
    """
    服务类型枚举
    """
    PLATFORM = "platform"          # 平台服务
    DATA_SERVICE = "data_service"  # 数据服务
    SECURITY = "security"          # 安全服务
    MONITOR = "monitor"            # 监控服务
    TOOL = "tool"                  # 工具服务
    OTHER = "other"                # 其他


class ServiceStatus(str, enum.Enum):
    """
    服务状态枚举
    """
    RUNNING = "running"            # 运行中
    STOPPED = "stopped"            # 已停止
    MAINTENANCE = "maintenance"    # 维护中
    DEPRECATED = "deprecated"      # 已弃用


class ServiceLevel(str, enum.Enum):
    """
    服务等级枚举
    """
    P0 = "p0"                      # 核心服务
    P1 = "p1"                      # 重要服务
    P2 = "p2"                      # 一般服务
    P3 = "p3"                      # 低优先级服务


class Service(Base):
    """
    服务台账表
    存储所有服务的信息
    """
    __tablename__ = "service"
    
    # 主键
    id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="服务ID")
    
    # 服务编号（系统自动生成，如：SVC-202403230001）
    service_no = Column(String(50), unique=True, nullable=False, index=True, comment="服务编号")
    
    # 基本信息
    name = Column(String(100), nullable=False, comment="服务名称")
    service_type = Column(String(50), nullable=False, comment="服务类型")
    status = Column(String(20), default=ServiceStatus.RUNNING.value, comment="服务状态")
    service_level = Column(String(10), default=ServiceLevel.P2.value, comment="服务等级")
    
    # 服务描述
    description = Column(Text, nullable=True, comment="服务描述")
    
    # 技术栈
    tech_stack = Column(Text, nullable=True, comment="技术栈（JSON）")
    
    # 访问地址
    access_url = Column(String(500), nullable=True, comment="访问地址")
    
    # 负责人
    owner_id = Column(Integer, ForeignKey("user.id"), nullable=True, comment="负责人ID")
    owner = relationship("User", foreign_keys=[owner_id])
    
    # 依赖服务（JSON格式存储依赖的服务ID列表）
    dependencies = Column(Text, nullable=True, comment="依赖服务（JSON）")
    
    # 部署信息（JSON格式）
    deployment_info = Column(Text, nullable=True, comment="部署信息（JSON）")
    
    # 备注
    remark = Column(Text, nullable=True, comment="备注")
    
    # 软删除
    is_deleted = Column(Boolean, default=False, comment="是否删除")
    deleted_at = Column(DateTime, nullable=True, comment="删除时间")
    
    # 时间戳
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    created_by = Column(Integer, ForeignKey("user.id"), nullable=True, comment="创建人ID")
    updated_by = Column(Integer, ForeignKey("user.id"), nullable=True, comment="更新人ID")
    
    # 关联关系
    assets = relationship("Asset", back_populates="service")
    
    def __repr__(self):
        return f"<Service(id={self.id}, service_no={self.service_no}, name={self.name})>"
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            "id": self.id,
            "service_no": self.service_no,
            "name": self.name,
            "service_type": self.service_type,
            "status": self.status,
            "service_level": self.service_level,
            "description": self.description,
            "tech_stack": self.tech_stack,
            "access_url": self.access_url,
            "owner_id": self.owner_id,
            "dependencies": self.dependencies,
            "deployment_info": self.deployment_info,
            "remark": self.remark,
            "is_deleted": self.is_deleted,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
    
    def get_service_type_display(self):
        """获取服务类型显示名称"""
        type_map = {
            ServiceType.PLATFORM.value: "平台服务",
            ServiceType.DATA_SERVICE.value: "数据服务",
            ServiceType.SECURITY.value: "安全服务",
            ServiceType.MONITOR.value: "监控服务",
            ServiceType.TOOL.value: "工具服务",
            ServiceType.OTHER.value: "其他",
        }
        return type_map.get(self.service_type, self.service_type)
    
    def get_status_display(self):
        """获取状态显示名称"""
        status_map = {
            ServiceStatus.RUNNING.value: "运行中",
            ServiceStatus.STOPPED.value: "已停止",
            ServiceStatus.MAINTENANCE.value: "维护中",
            ServiceStatus.DEPRECATED.value: "已弃用",
        }
        return status_map.get(self.status, self.status)
    
    def get_service_level_display(self):
        """获取服务等级显示名称"""
        level_map = {
            ServiceLevel.P0.value: "P0-核心服务",
            ServiceLevel.P1.value: "P1-重要服务",
            ServiceLevel.P2.value: "P2-一般服务",
            ServiceLevel.P3.value: "P3-低优先级",
        }
        return level_map.get(self.service_level, self.service_level)
