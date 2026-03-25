"""
需求单模型
数据库表：work_orders

业务规则：
- 需求单号格式：XQ + 年月日 + 3位序号（如 XQ20260325001）
- 需求类型：接口开发、数据导出、数据同步、其他
- 使用频率：实时、每日、每周、每月、一次性
- 状态流转：pending_review(待审批) -> approved(已通过)/rejected(已驳回)

作者/日期：AI / 2026-03-25
"""

from sqlalchemy import Column, Integer, String, DateTime, Date, ForeignKey, Table
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from backend.src.database import Base


# 需求单与附件的多对多关联表
work_order_attachment = Table(
    "work_order_attachment",
    Base.metadata,
    Column("work_order_id", Integer, ForeignKey("work_orders.id", ondelete="CASCADE"), primary_key=True),
    Column("attachment_id", Integer, ForeignKey("file_attachment.id", ondelete="CASCADE"), primary_key=True),
)


class WorkOrder(Base):
    """
    需求单表
    存储所有需求单信息
    """
    __tablename__ = "work_orders"
    
    # 主键
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # 需求单号（唯一）
    order_no = Column(String(20), unique=True, nullable=False, index=True, comment="需求单号，格式：XQ20260325001")
    
    # 需求基本信息
    title = Column(String(200), nullable=False, comment="需求标题")
    type = Column(String(50), nullable=False, comment="需求类型：interface_dev(接口开发)/data_export(数据导出)/data_sync(数据同步)/other(其他)")
    business_background = Column(String(2000), nullable=True, comment="业务背景")
    data_scope = Column(String(1000), nullable=True, comment="数据范围")
    frequency = Column(String(50), nullable=True, comment="使用频率：realtime(实时)/daily(每日)/weekly(每周)/monthly(每月)/once(一次性)")
    expected_date = Column(Date, nullable=True, comment="期望完成时间")
    
    # 状态
    status = Column(String(50), default="pending_review", nullable=False, index=True, comment="状态：pending_review(待审批)/approved(已通过)/rejected(已驳回)")
    
    # 创建人信息
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="创建人ID，外键关联users.id")
    creator_role = Column(String(50), nullable=True, comment="创建人角色")
    
    # 审计字段
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关联关系
    creator = relationship("User", backref="work_orders")
    attachments = relationship("FileAttachment", secondary=work_order_attachment, backref="work_orders")
    
    def __repr__(self):
        return f"<WorkOrder(id={self.id}, order_no={self.order_no}, title={self.title})>"
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "order_no": self.order_no,
            "title": self.title,
            "type": self.type,
            "type_display": self.get_type_display(),
            "business_background": self.business_background,
            "data_scope": self.data_scope,
            "frequency": self.frequency,
            "frequency_display": self.get_frequency_display(),
            "expected_date": self.expected_date.isoformat() if self.expected_date else None,
            "status": self.status,
            "status_display": self.get_status_display(),
            "creator_id": self.creator_id,
            "creator_role": self.creator_role,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
    
    def get_type_display(self):
        """获取需求类型显示名称"""
        type_map = {
            "interface_dev": "接口开发",
            "data_export": "数据导出",
            "data_sync": "数据同步",
            "other": "其他",
        }
        return type_map.get(self.type, self.type)
    
    def get_frequency_display(self):
        """获取使用频率显示名称"""
        frequency_map = {
            "realtime": "实时",
            "daily": "每日",
            "weekly": "每周",
            "monthly": "每月",
            "once": "一次性",
        }
        return frequency_map.get(self.frequency, self.frequency)
    
    def get_status_display(self):
        """获取状态显示名称"""
        status_map = {
            "draft": "草稿",
            "pending_review": "待审批",
            "analyzed": "已梳理",
            "approved": "审批通过",
            "rejected": "已驳回",
            "solution_submitted": "方案已提交",
            "in_review": "会审中",
            "in_progress": "实施中",
            "pending_qa": "待质量稽核",
            "pending_trial": "待试运行",
            "pending_monitor": "待监控配置",
            "online": "已上线",
        }
        return status_map.get(self.status, self.status)


# 需求类型枚举
WORK_ORDER_TYPES = [
    ("interface_dev", "接口开发"),
    ("data_export", "数据导出"),
    ("data_sync", "数据同步"),
    ("other", "其他"),
]

# 使用频率枚举
WORK_ORDER_FREQUENCIES = [
    ("realtime", "实时"),
    ("daily", "每日"),
    ("weekly", "每周"),
    ("monthly", "每月"),
    ("once", "一次性"),
]

# 状态枚举（对应10个流程节点）
WORK_ORDER_STATUSES = [
    ("draft", "草稿"),
    ("pending_review", "待审批"),
    ("analyzed", "已梳理"),
    ("approved", "审批通过"),
    ("rejected", "已驳回"),
    ("solution_submitted", "方案已提交"),
    ("in_review", "会审中"),
    ("in_progress", "实施中"),
    ("pending_qa", "待质量稽核"),
    ("pending_trial", "待试运行"),
    ("pending_monitor", "待监控配置"),
    ("online", "已上线"),
]
