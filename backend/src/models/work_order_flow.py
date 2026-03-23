"""
工单流转记录模型
记录工单的所有操作历史，用于审计和追溯
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from backend.src.database import Base


class OperationType(str, enum.Enum):
    """
    操作类型枚举
    """
    CREATE = "create"              # 创建
    UPDATE = "update"              # 更新
    SUBMIT = "submit"              # 提交
    APPROVE = "approve"            # 审批通过
    REJECT = "reject"              # 审批驳回
    ASSIGN = "assign"              # 分配
    ACCEPT = "accept"              # 接受
    PROCESS = "process"            # 处理中
    COMPLETE = "complete"          # 完成
    CLOSE = "close"                # 关闭
    TRANSFER = "transfer"          # 转派
    COMMENT = "comment"            # 评论
    DELETE = "delete"              # 删除
    RESTORE = "restore"            # 恢复


class WorkOrderFlow(Base):
    """
    工单流转记录表
    记录工单的每一次状态变更和操作
    """
    __tablename__ = "work_order_flow"
    
    # 主键
    id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="记录ID")
    
    # 关联工单
    work_order_id = Column(Integer, ForeignKey("work_order.id"), nullable=False, comment="工单ID")
    work_order = relationship("WorkOrder", back_populates="flows")
    
    # 操作人
    operator_id = Column(Integer, ForeignKey("user.id"), nullable=False, comment="操作人ID")
    operator = relationship("User", back_populates="work_order_flows")
    
    # 操作类型
    operation_type = Column(String(50), nullable=False, comment="操作类型")
    
    # 状态变更
    from_status = Column(String(20), nullable=True, comment="操作前状态")
    to_status = Column(String(20), nullable=True, comment="操作后状态")
    
    # 操作内容
    content = Column(Text, nullable=True, comment="操作内容/备注")
    
    # 附件（JSON格式）
    attachments = Column(Text, nullable=True, comment="附件列表（JSON）")
    
    # IP地址（用于审计）
    ip_address = Column(String(50), nullable=True, comment="操作IP地址")
    
    # 用户代理（用于审计）
    user_agent = Column(String(500), nullable=True, comment="用户代理信息")
    
    # 时间戳
    created_at = Column(DateTime, server_default=func.now(), comment="操作时间")
    
    def __repr__(self):
        return f"<WorkOrderFlow(id={self.id}, work_order_id={self.work_order_id}, operation_type={self.operation_type})>"
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            "id": self.id,
            "work_order_id": self.work_order_id,
            "operator_id": self.operator_id,
            "operation_type": self.operation_type,
            "from_status": self.from_status,
            "to_status": self.to_status,
            "content": self.content,
            "attachments": self.attachments,
            "ip_address": self.ip_address,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
    
    def get_operation_type_display(self):
        """获取操作类型显示名称"""
        operation_map = {
            OperationType.CREATE.value: "创建",
            OperationType.UPDATE.value: "更新",
            OperationType.SUBMIT.value: "提交",
            OperationType.APPROVE.value: "审批通过",
            OperationType.REJECT.value: "审批驳回",
            OperationType.ASSIGN.value: "分配",
            OperationType.ACCEPT.value: "接受",
            OperationType.PROCESS.value: "处理中",
            OperationType.COMPLETE.value: "完成",
            OperationType.CLOSE.value: "关闭",
            OperationType.TRANSFER.value: "转派",
            OperationType.COMMENT.value: "评论",
            OperationType.DELETE.value: "删除",
            OperationType.RESTORE.value: "恢复",
        }
        return operation_map.get(self.operation_type, self.operation_type)
