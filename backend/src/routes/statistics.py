"""
统计报表路由模块
提供工单统计、个人统计等数据报表接口
"""

from typing import Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from backend.src.database import get_db
from backend.src.models.user import User
from backend.src.models.work_order import WorkOrder, WorkOrderStatus, WorkOrderType, WorkOrderPriority
from backend.src.models.asset import Asset, AssetType, AssetStatus
from backend.src.models.service import Service, ServiceType, ServiceStatus
from backend.src.utils.auth import get_current_user

router = APIRouter(prefix="/api/statistics", tags=["统计报表"])


# 响应模型
class ApiResponse(BaseModel):
    """统一 API 响应格式"""
    code: int
    message: str
    data: Optional[dict] = None


@router.get("/work-orders", response_model=ApiResponse, summary="工单统计")
async def get_work_order_statistics(
    start_date: Optional[str] = Query(None, description="开始日期（YYYY-MM-DD）"),
    end_date: Optional[str] = Query(None, description="结束日期（YYYY-MM-DD）"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取工单统计数据
    
    包括：
    - 工单总数
    - 各状态工单数量
    - 各类型工单数量
    - 各优先级工单数量
    - 趋势数据（按天）
    """
    # 默认查询最近30天
    if not start_date:
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    if not end_date:
        end_date = datetime.now().strftime("%Y-%m-%d")
    
    start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
    end_datetime = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
    
    # 基础查询条件
    base_query = db.query(WorkOrder).filter(
        WorkOrder.is_deleted == False,
        WorkOrder.created_at >= start_datetime,
        WorkOrder.created_at < end_datetime
    )
    
    # 工单总数
    total_count = base_query.count()
    
    # 各状态工单数量
    status_counts = {}
    for status in WorkOrderStatus:
        count = base_query.filter(WorkOrder.status == status.value).count()
        status_counts[status.value] = {
            "label": status.value,
            "count": count
        }
    
    # 各类型工单数量
    type_counts = {}
    for work_type in WorkOrderType:
        count = base_query.filter(WorkOrder.work_type == work_type.value).count()
        type_counts[work_type.value] = {
            "label": work_type.value,
            "count": count
        }
    
    # 各优先级工单数量
    priority_counts = {}
    for priority in WorkOrderPriority:
        count = base_query.filter(WorkOrder.priority == priority.value).count()
        priority_counts[priority.value] = {
            "label": priority.value,
            "count": count
        }
    
    # 趋势数据（按天统计）
    trend_data = []
    current_date = start_datetime
    while current_date < end_datetime:
        day_start = current_date
        day_end = current_date + timedelta(days=1)
        
        day_count = db.query(WorkOrder).filter(
            WorkOrder.is_deleted == False,
            WorkOrder.created_at >= day_start,
            WorkOrder.created_at < day_end
        ).count()
        
        trend_data.append({
            "date": current_date.strftime("%Y-%m-%d"),
            "count": day_count
        })
        
        current_date += timedelta(days=1)
    
    return ApiResponse(
        code=200,
        message="获取成功",
        data={
            "total_count": total_count,
            "status_counts": status_counts,
            "type_counts": type_counts,
            "priority_counts": priority_counts,
            "trend": trend_data,
            "date_range": {
                "start": start_date,
                "end": end_date
            }
        }
    )


@router.get("/personal", response_model=ApiResponse, summary="个人统计")
async def get_personal_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取当前用户的个人统计数据
    
    包括：
    - 我创建的工单
    - 我处理的工单
    - 待我处理的工单
    """
    # 我创建的工单
    my_created = db.query(WorkOrder).filter(
        WorkOrder.created_by == current_user.id,
        WorkOrder.is_deleted == False
    )
    
    my_created_count = my_created.count()
    my_created_pending = my_created.filter(WorkOrder.status == WorkOrderStatus.PENDING.value).count()
    my_created_processing = my_created.filter(WorkOrder.status == WorkOrderStatus.PROCESSING.value).count()
    my_created_completed = my_created.filter(WorkOrder.status == WorkOrderStatus.CLOSED.value).count()
    
    # 我处理的工单（作为 assignee）
    my_assigned = db.query(WorkOrder).filter(
        WorkOrder.assignee_id == current_user.id,
        WorkOrder.is_deleted == False
    )
    
    my_assigned_count = my_assigned.count()
    my_assigned_processing = my_assigned.filter(WorkOrder.status == WorkOrderStatus.PROCESSING.value).count()
    my_assigned_completed = my_assigned.filter(
        WorkOrder.status.in_([WorkOrderStatus.COMPLETED.value, WorkOrderStatus.CLOSED.value])
    ).count()
    
    # 待我处理的工单
    pending_for_me = db.query(WorkOrder).filter(
        WorkOrder.assignee_id == current_user.id,
        WorkOrder.status == WorkOrderStatus.PROCESSING.value,
        WorkOrder.is_deleted == False
    ).count()
    
    return ApiResponse(
        code=200,
        message="获取成功",
        data={
            "created": {
                "total": my_created_count,
                "pending": my_created_pending,
                "processing": my_created_processing,
                "completed": my_created_completed
            },
            "assigned": {
                "total": my_assigned_count,
                "processing": my_assigned_processing,
                "completed": my_assigned_completed
            },
            "pending_for_me": pending_for_me
        }
    )


@router.get("/dashboard", response_model=ApiResponse, summary="仪表盘数据")
async def get_dashboard_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取仪表盘统计数据
    
    包括：
    - 工单概览
    - 资产概览
    - 服务概览
    - 最近工单
    """
    # 工单概览
    work_order_total = db.query(WorkOrder).filter(WorkOrder.is_deleted == False).count()
    work_order_pending = db.query(WorkOrder).filter(
        WorkOrder.status == WorkOrderStatus.PENDING.value,
        WorkOrder.is_deleted == False
    ).count()
    work_order_processing = db.query(WorkOrder).filter(
        WorkOrder.status == WorkOrderStatus.PROCESSING.value,
        WorkOrder.is_deleted == False
    ).count()
    work_order_closed_today = db.query(WorkOrder).filter(
        WorkOrder.status == WorkOrderStatus.CLOSED.value,
        WorkOrder.closed_at >= datetime.now().replace(hour=0, minute=0, second=0),
        WorkOrder.is_deleted == False
    ).count()
    
    # 资产概览
    asset_total = db.query(Asset).filter(Asset.is_deleted == False).count()
    asset_in_use = db.query(Asset).filter(
        Asset.status == AssetStatus.IN_USE.value,
        Asset.is_deleted == False
    ).count()
    asset_maintenance = db.query(Asset).filter(
        Asset.status == AssetStatus.MAINTENANCE.value,
        Asset.is_deleted == False
    ).count()
    
    # 服务概览
    service_total = db.query(Service).filter(Service.is_deleted == False).count()
    service_running = db.query(Service).filter(
        Service.status == ServiceStatus.RUNNING.value,
        Service.is_deleted == False
    ).count()
    service_maintenance = db.query(Service).filter(
        Service.status == ServiceStatus.MAINTENANCE.value,
        Service.is_deleted == False
    ).count()
    
    # 最近工单（最近5条）
    recent_orders = db.query(WorkOrder).filter(
        WorkOrder.is_deleted == False
    ).order_by(WorkOrder.created_at.desc()).limit(5).all()
    
    recent_list = []
    for order in recent_orders:
        creator = db.query(User).filter(User.id == order.created_by).first()
        recent_list.append({
            "id": order.id,
            "order_no": order.order_no,
            "title": order.title,
            "status": order.status,
            "creator_name": creator.real_name if creator else None,
            "created_at": order.created_at.isoformat() if order.created_at else None
        })
    
    return ApiResponse(
        code=200,
        message="获取成功",
        data={
            "work_orders": {
                "total": work_order_total,
                "pending": work_order_pending,
                "processing": work_order_processing,
                "closed_today": work_order_closed_today
            },
            "assets": {
                "total": asset_total,
                "in_use": asset_in_use,
                "maintenance": asset_maintenance
            },
            "services": {
                "total": service_total,
                "running": service_running,
                "maintenance": service_maintenance
            },
            "recent_work_orders": recent_list
        }
    )
