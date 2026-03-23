"""
运维工单模型
定义运维工单的核心数据结构
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, Numeric, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from backend.src.database import Base


class WorkOrderStatus(str, enum.Enum):
    """
    工单状态枚举
    """
    DRAFT = "draft"              # 草稿
    PENDING = "pending"          # 待审批
    APPROVED = "approved"        # 已审批
    PROCESSING = "processing"    # 处理中
    COMPLETED = "completed"      # 已完成
    CLOSED = "closed"            # 已关闭
    REJECTED = "rejected"        # 已驳回


class WorkOrderPriority(str, enum.Enum):
    """
    工单优先级枚举
    """
    URGENT = "urgent"    # 紧急
    HIGH = "high"        # 高
    MEDIUM = "medium"    # 中
    LOW = "low"          # 低


class WorkOrderType(str, enum.Enum):
    """
    工单类型枚举
    """
    PLATFORM_BUILD = "platform_build"        # 平台建设
    PLATFORM_UPDATE = "platform_update"      # 平台迭代
    PLATFORM_OFFLINE = "platform_offline"    # 平台下线
    DATA_SERVICE_BUILD = "data_service_build"    # 数据服务建设
    DATA_SERVICE_UPDATE = "data_service_update"  # 数据服务迭代
    DATA_SERVICE_OFFLINE = "data_service_offline" # 数据服务下线
    SECURITY = "security"                    # 安全加固
    AUDIT = "audit"                          # 审计管理
    RESOURCE = "resource"                    # 资源申请
    OTHER = "other"                          # 其他


class WorkOrder(Base):
    """
    运维工单表
    存储所有运维工单的核心信息
    """
    __tablename__ = "work_order"
    
    # 主键
    id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="工单ID")
    
    # 工单编号（系统自动生成，如：WO-202403230001）
    order_no = Column(String(50), unique=True, nullable=False, index=True, comment="工单编号")
    
    # 基本信息
    title = Column(String(200), nullable=False, comment="工单标题")
    description = Column(Text, nullable=True, comment="工单描述")
    
    # 工单类型和优先级
    work_type = Column(String(50), nullable=False, comment="工单类型")
    priority = Column(String(20), default=WorkOrderPriority.MEDIUM.value, comment="优先级")
    
    # 工单状态
    status = Column(String(20), default=WorkOrderStatus.DRAFT.value, comment="工单状态")
    
    # 关联用户
    created_by = Column(Integer, ForeignKey("user.id"), nullable=False, comment="创建人ID")
    creator = relationship("User", foreign_keys=[created_by], back_populates="created_work_orders")
    
    assignee_id = Column(Integer, ForeignKey("user.id"), nullable=True, comment="处理人ID")
    assignee = relationship("User", foreign_keys=[assignee_id], back_populates="assigned_work_orders")
    
    # 审批信息
    approved_by = Column(Integer, ForeignKey("user.id"), nullable=True, comment="审批人ID")
    approved_at = Column(DateTime, nullable=True, comment="审批时间")
    approval_comment = Column(Text, nullable=True, comment="审批意见")
    
    # 时间信息
    expected_complete_at = Column(DateTime, nullable=True, comment="期望完成时间")
    started_at = Column(DateTime, nullable=True, comment="开始处理时间")
    completed_at = Column(DateTime, nullable=True, comment="实际完成时间")
    closed_at = Column(DateTime, nullable=True, comment="关闭时间")
    
    # 满意度评价（关闭时填写）
    satisfaction_score = Column(Numeric(2, 1), nullable=True, comment="满意度评分（1-5）")
    satisfaction_comment = Column(Text, nullable=True, comment="满意度评价内容")
    
    # 附件（JSON格式存储附件列表）
    attachments = Column(Text, nullable=True, comment="附件列表（JSON）")
    
    # 关联资产/服务（JSON格式）
    related_assets = Column(Text, nullable=True, comment="关联资产（JSON）")
    related_services = Column(Text, nullable=True, comment="关联服务（JSON）")
    
    # 标签（JSON格式）
    tags = Column(Text, nullable=True, comment="标签（JSON）")
    
    # 软删除
    is_deleted = Column(Boolean, default=False, comment="是否删除")
    deleted_at = Column(DateTime, nullable=True, comment="删除时间")
    deleted_by = Column(Integer, ForeignKey("user.id"), nullable=True, comment="删除人ID")
    
    # 时间戳
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关联关系
    flows = relationship("WorkOrderFlow", back_populates="work_order", order_by="WorkOrderFlow.created_at.desc()")
    
    def __repr__(self):
        return f"<WorkOrder(id={self.id}, order_no={self.order_no}, title={self.title})>"
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            "id": self.id,
            "order_no": self.order_no,
            "title": self.title,
            "description": self.description,
            "work_type": self.work_type,
            "priority": self.priority,
            "status": self.status,
            "created_by": self.created_by,
            "assignee_id": self.assignee_id,
            "approved_by": self.approved_by,
            "approved_at": self.approved_at.isoformat() if self.approved_at else None,
            "approval_comment": self.approval_comment,
            "expected_complete_at": self.expected_complete_at.isoformat() if self.expected_complete_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "closed_at": self.closed_at.isoformat() if self.closed_at else None,
            "satisfaction_score": float(self.satisfaction_score) if self.satisfaction_score else None,
            "satisfaction_comment": self.satisfaction_comment,
            "attachments": self.attachments,
            "tags": self.tags,
            "is_deleted": self.is_deleted,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
    
    def get_status_display(self):
        """获取状态显示名称"""
        status_map = {
            WorkOrderStatus.DRAFT.value: "草稿",
            WorkOrderStatus.PENDING.value: "待审批",
            WorkOrderStatus.APPROVED.value: "已审批",
            WorkOrderStatus.PROCESSING.value: "处理中",
            WorkOrderStatus.COMPLETED.value: "已完成",
            WorkOrderStatus.CLOSED.value: "已关闭",
            WorkOrderStatus.REJECTED.value: "已驳回",
        }
        return status_map.get(self.status, self.status)
    
    def get_priority_display(self):
        """获取优先级显示名称"""
        priority_map = {
            WorkOrderPriority.URGENT.value: "紧急",
            WorkOrderPriority.HIGH.value: "高",
            WorkOrderPriority.MEDIUM.value: "中",
            WorkOrderPriority.LOW.value: "低",
        }
        return priority_map.get(self.priority, self.priority)
