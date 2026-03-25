"""
需求单相关API
包含需求单的创建、查询、更新等功能

作者/日期：AI / 2026-03-25
"""

from datetime import datetime, date
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, Header
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from backend.src.database import get_db
from backend.src.models.work_order import WorkOrder, work_order_attachment, WORK_ORDER_TYPES, WORK_ORDER_FREQUENCIES, WORK_ORDER_STATUSES
from backend.src.models.file_attachment import FileAttachment
from backend.src.models.user import User
from backend.src.routes.auth import get_current_user_simple


router = APIRouter(prefix="/api/work-orders", tags=["需求单"])


# ============== Pydantic模型 ==============

class WorkOrderCreate(BaseModel):
    """创建需求单请求"""
    title: str = Field(..., min_length=1, max_length=200, description="需求标题")
    type: str = Field(..., description="需求类型")
    business_background: Optional[str] = Field(None, max_length=2000, description="业务背景")
    data_scope: Optional[str] = Field(None, max_length=1000, description="数据范围")
    frequency: Optional[str] = Field(None, description="使用频率")
    expected_date: Optional[date] = Field(None, description="期望完成时间")
    file_ids: Optional[List[int]] = Field([], description="关联附件ID列表")
    is_draft: bool = Field(False, description="是否为草稿")


class WorkOrderResponse(BaseModel):
    """需求单响应"""
    id: int
    order_no: str
    title: str
    type: str
    type_display: str
    status: str
    status_display: str
    creator_id: int
    creator_name: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class WorkOrderDetail(WorkOrderResponse):
    """需求单详情"""
    business_background: Optional[str]
    data_scope: Optional[str]
    frequency: Optional[str]
    frequency_display: Optional[str]
    expected_date: Optional[date]
    updated_at: datetime


class WorkOrderList(BaseModel):
    """需求单列表响应"""
    total: int
    items: List[WorkOrderResponse]


# ============== 辅助函数 ==============

def generate_order_no(db: Session) -> str:
    """生成需求单号，格式：XQ + 年月日 + 3位序号"""
    today = datetime.now()
    date_prefix = f"XQ{today.strftime('%Y%m%d')}"
    
    # 查询当天最后一个单号
    last_order = db.query(WorkOrder).filter(
        WorkOrder.order_no.like(f"{date_prefix}%")
    ).order_by(WorkOrder.order_no.desc()).first()
    
    if last_order:
        # 提取序号并加1
        last_seq = int(last_order.order_no[-3:])
        new_seq = last_seq + 1
    else:
        new_seq = 1
    
    return f"{date_prefix}{new_seq:03d}"


# ============== API接口 ==============

@router.post("", response_model=dict)
def create_work_order(
    data: WorkOrderCreate,
    db: Session = Depends(get_db),
    authorization: str = Header(None),
):
    current_user = get_current_user_simple(db, authorization)
    """
    创建需求单
    
    权限：仅用数方可创建
    """
    # 权限检查
    if current_user.role != "data_consumer":
        raise HTTPException(status_code=403, detail="仅用数方可以创建需求单")
    
    # 生成需求单号
    order_no = generate_order_no(db)
    
    # 确定状态
    status = "draft" if data.is_draft else "pending_review"
    
    # 创建需求单
    work_order = WorkOrder(
        order_no=order_no,
        title=data.title,
        type=data.type,
        business_background=data.business_background,
        data_scope=data.data_scope,
        frequency=data.frequency,
        expected_date=data.expected_date,
        status=status,
        creator_id=current_user.id,
        creator_role=current_user.role,
    )
    
    db.add(work_order)
    db.commit()
    db.refresh(work_order)
    
    # 关联附件
    if data.file_ids:
        for file_id in data.file_ids:
            file = db.query(FileAttachment).filter(FileAttachment.id == file_id).first()
            if file:
                work_order.attachments.append(file)
        db.commit()
    
    return {
        "code": 200,
        "message": "保存成功" if data.is_draft else "提交成功",
        "data": {
            "id": work_order.id,
            "order_no": work_order.order_no,
            "status": work_order.status,
        }
    }


@router.get("", response_model=dict)
def list_work_orders(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    status: Optional[str] = Query(None, description="状态筛选"),
    type: Optional[str] = Query(None, description="类型筛选"),
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    db: Session = Depends(get_db),
    authorization: str = Header(None),
):
    current_user = get_current_user_simple(db, authorization)
    """
    获取需求单列表
    
    权限：
    - 用数方：只看自己创建的
    - 其他角色：根据业务规则查看（先实现看全部）
    """
    query = db.query(WorkOrder)
    
    # 用数方只能看自己创建的
    if current_user.role == "data_consumer":
        query = query.filter(WorkOrder.creator_id == current_user.id)
    
    # 状态筛选
    if status:
        query = query.filter(WorkOrder.status == status)
    
    # 类型筛选
    if type:
        query = query.filter(WorkOrder.type == type)
    
    # 关键词搜索
    if keyword:
        query = query.filter(WorkOrder.title.contains(keyword))
    
    # 排序：最新的在前
    query = query.order_by(WorkOrder.created_at.desc())
    
    # 分页
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    
    return {
        "code": 200,
        "message": "success",
        "data": {
            "total": total,
            "items": [item.to_dict() for item in items],
        }
    }


@router.get("/{order_id}", response_model=dict)
def get_work_order_detail(
    order_id: int,
    db: Session = Depends(get_db),
    authorization: str = Header(None),
):
    current_user = get_current_user_simple(db, authorization)
    """
    获取需求单详情
    """
    work_order = db.query(WorkOrder).filter(WorkOrder.id == order_id).first()
    if not work_order:
        raise HTTPException(status_code=404, detail="需求单不存在")
    
    # 权限检查：用数方只能看自己创建的
    if current_user.role == "data_consumer" and work_order.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权查看此需求单")
    
    return {
        "code": 200,
        "message": "success",
        "data": work_order.to_dict()
    }
