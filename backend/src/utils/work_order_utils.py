"""
运维需求单工具模块
提供需求单号生成、状态流转等工具函数
"""

from datetime import datetime
from sqlalchemy.orm import Session

from backend.src.models.work_order import WorkOrder


def generate_work_order_no(db: Session) -> str:
    """
    生成需求单号
    格式：WO-YYYYMMDD-XXXX（如：WO-20240323-0001）
    
    Args:
        db: 数据库会话
        
    Returns:
        需求单号字符串
    """
    today = datetime.now()
    date_str = today.strftime("%Y%m%d")
    prefix = f"WO-{date_str}-"
    
    # 查询当天最后一个需求单号
    last_order = db.query(WorkOrder).filter(
        WorkOrder.order_no.like(f"{prefix}%")
    ).order_by(WorkOrder.order_no.desc()).first()
    
    if last_order:
        # 提取序号并加1
        last_no = int(last_order.order_no.split("-")[-1])
        new_no = last_no + 1
    else:
        new_no = 1
    
    return f"{prefix}{new_no:04d}"


def can_transition(from_status: str, to_status: str, user_role: str) -> bool:
    """
    检查状态流转是否合法
    
    状态流转规则：
    - 草稿 -> 待审批：需求方提交
    - 待审批 -> 已审批：管理员审批通过
    - 待审批 -> 已驳回：管理员审批驳回
    - 已审批 -> 处理中：SRE接单/开始处理
    - 处理中 -> 已完成：SRE完成处理
    - 已完成 -> 已关闭：需求方确认关闭
    
    Args:
        from_status: 当前状态
        to_status: 目标状态
        user_role: 用户角色（admin/requester/sre）
        
    Returns:
        是否允许流转
    """
    # 定义合法的状态流转
    valid_transitions = {
        "draft": {
            "pending": ["requester", "admin"],  # 需求方或管理员可以提交
        },
        "pending": {
            "approved": ["admin"],  # 只有管理员可以审批通过
            "rejected": ["admin"],  # 只有管理员可以驳回
        },
        "approved": {
            "processing": ["sre", "admin"],  # SRE或管理员可以开始处理
        },
        "processing": {
            "completed": ["sre", "admin"],  # SRE或管理员可以标记完成
        },
        "completed": {
            "closed": ["requester", "admin"],  # 需求方或管理员可以关闭
        },
    }
    
    if from_status not in valid_transitions:
        return False
    
    if to_status not in valid_transitions[from_status]:
        return False
    
    allowed_roles = valid_transitions[from_status][to_status]
    return user_role in allowed_roles


def get_work_order_status_display(status: str) -> str:
    """
    获取需求单状态的中文显示名称
    
    Args:
        status: 状态代码
        
    Returns:
        中文状态名称
    """
    status_map = {
        "draft": "草稿",
        "pending": "待审批",
        "approved": "已审批",
        "processing": "处理中",
        "completed": "已完成",
        "closed": "已关闭",
        "rejected": "已驳回",
    }
    return status_map.get(status, status)


def get_work_order_type_display(work_type: str) -> str:
    """
    获取需求单类型的中文显示名称
    
    Args:
        work_type: 类型代码
        
    Returns:
        中文类型名称
    """
    type_map = {
        "platform_build": "平台建设",
        "platform_update": "平台迭代",
        "platform_offline": "平台下线",
        "data_service_build": "数据服务建设",
        "data_service_update": "数据服务迭代",
        "data_service_offline": "数据服务下线",
        "security": "安全加固",
        "audit": "审计管理",
        "resource": "资源申请",
        "other": "其他",
    }
    return type_map.get(work_type, work_type)


def get_priority_display(priority: str) -> str:
    """
    获取优先级的中文显示名称
    
    Args:
        priority: 优先级代码
        
    Returns:
        中文优先级名称
    """
    priority_map = {
        "urgent": "紧急",
        "high": "高",
        "medium": "中",
        "low": "低",
    }
    return priority_map.get(priority, priority)
