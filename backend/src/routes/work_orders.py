"""
运维工单路由模块
提供工单的申请、审批、执行、关闭等完整生命周期接口
"""

from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.src.database import get_db
from backend.src.models.user import User
from backend.src.models.work_order import WorkOrder, WorkOrderStatus, WorkOrderPriority, WorkOrderType
from backend.src.models.work_order_flow import WorkOrderFlow, OperationType
from backend.src.utils.auth import get_current_user
from backend.src.utils.work_order_utils import (
    generate_work_order_no,
    can_transition,
    get_work_order_status_display,
    get_work_order_type_display,
    get_priority_display
)

router = APIRouter(prefix="/api/work-orders", tags=["运维工单"])


# 请求模型
class CreateWorkOrderRequest(BaseModel):
    """创建工单请求"""
    title: str = Field(..., min_length=1, max_length=200, description="工单标题")
    description: Optional[str] = Field(None, description="工单描述")
    work_type: str = Field(..., description="工单类型")
    priority: str = Field("medium", description="优先级")
    expected_complete_at: Optional[datetime] = Field(None, description="期望完成时间")
    attachments: Optional[str] = Field(None, description="附件列表（JSON）")
    related_assets: Optional[str] = Field(None, description="关联资产（JSON）")
    related_services: Optional[str] = Field(None, description="关联服务（JSON）")
    tags: Optional[str] = Field(None, description="标签（JSON）")


class UpdateWorkOrderRequest(BaseModel):
    """更新工单请求"""
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="工单标题")
    description: Optional[str] = Field(None, description="工单描述")
    work_type: Optional[str] = Field(None, description="工单类型")
    priority: Optional[str] = Field(None, description="优先级")
    expected_complete_at: Optional[datetime] = Field(None, description="期望完成时间")
    attachments: Optional[str] = Field(None, description="附件列表（JSON）")
    related_assets: Optional[str] = Field(None, description="关联资产（JSON）")
    related_services: Optional[str] = Field(None, description="关联服务（JSON）")
    tags: Optional[str] = Field(None, description="标签（JSON）")


class ApproveWorkOrderRequest(BaseModel):
    """审批工单请求"""
    approved: bool = Field(..., description="是否通过")
    comment: Optional[str] = Field(None, description="审批意见")


class AssignWorkOrderRequest(BaseModel):
    """分配工单请求"""
    assignee_id: int = Field(..., description="处理人ID")


class ProcessWorkOrderRequest(BaseModel):
    """处理工单请求"""
    content: str = Field(..., description="处理内容")
    attachments: Optional[str] = Field(None, description="附件列表（JSON）")


class CompleteWorkOrderRequest(BaseModel):
    """完成工单请求"""
    content: str = Field(..., description="完成说明")
    attachments: Optional[str] = Field(None, description="附件列表（JSON）")


class CloseWorkOrderRequest(BaseModel):
    """关闭工单请求"""
    satisfaction_score: Optional[float] = Field(None, ge=1, le=5, description="满意度评分")
    satisfaction_comment: Optional[str] = Field(None, description="满意度评价")


class CommentWorkOrderRequest(BaseModel):
    """评论工单请求"""
    content: str = Field(..., description="评论内容")
    attachments: Optional[str] = Field(None, description="附件列表（JSON）")


# 响应模型
class ApiResponse(BaseModel):
    """统一 API 响应格式"""
    code: int
    message: str
    data: Optional[dict] = None


class ListResponse(BaseModel):
    """列表响应格式"""
    code: int
    message: str
    data: dict


def get_user_role_codes(user: User) -> List[str]:
    """获取用户的角色编码列表"""
    return [role.code for role in user.roles]


def add_work_order_flow(
    db: Session,
    work_order_id: int,
    operator_id: int,
    operation_type: str,
    from_status: Optional[str] = None,
    to_status: Optional[str] = None,
    content: Optional[str] = None,
    attachments: Optional[str] = None
):
    """添加工单流转记录"""
    flow = WorkOrderFlow(
        work_order_id=work_order_id,
        operator_id=operator_id,
        operation_type=operation_type,
        from_status=from_status,
        to_status=to_status,
        content=content,
        attachments=attachments
    )
    db.add(flow)
    db.commit()


@router.get("", response_model=ListResponse, summary="获取工单列表")
async def get_work_orders(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    status: Optional[str] = Query(None, description="状态筛选"),
    work_type: Optional[str] = Query(None, description="类型筛选"),
    priority: Optional[str] = Query(None, description="优先级筛选"),
    my_orders: bool = Query(False, description="是否只查看我的工单"),
    pending_only: bool = Query(False, description="是否只查看待处理"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取工单列表
    
    支持分页、搜索、筛选
    """
    # 构建查询
    query = db.query(WorkOrder).filter(WorkOrder.is_deleted == False)
    
    # 搜索关键词
    if keyword:
        query = query.filter(
            (WorkOrder.title.contains(keyword)) |
            (WorkOrder.order_no.contains(keyword))
        )
    
    # 状态筛选
    if status:
        query = query.filter(WorkOrder.status == status)
    
    # 类型筛选
    if work_type:
        query = query.filter(WorkOrder.work_type == work_type)
    
    # 优先级筛选
    if priority:
        query = query.filter(WorkOrder.priority == priority)
    
    # 只查看我的工单
    if my_orders:
        query = query.filter(WorkOrder.created_by == current_user.id)
    
    # 只查看待处理（待审批、处理中且分配给当前用户）
    if pending_only:
        role_codes = get_user_role_codes(current_user)
        if "admin" in role_codes:
            # 管理员查看待审批的
            query = query.filter(WorkOrder.status == WorkOrderStatus.PENDING.value)
        elif "sre" in role_codes:
            # SRE查看已审批未分配或分配给自己的
            query = query.filter(
                (WorkOrder.status == WorkOrderStatus.APPROVED.value) |
                ((WorkOrder.status == WorkOrderStatus.PROCESSING.value) &
                 (WorkOrder.assignee_id == current_user.id))
            )
    
    # 统计总数
    total = query.count()
    
    # 分页
    work_orders = query.order_by(WorkOrder.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    # 构建响应数据
    order_list = []
    for order in work_orders:
        creator = db.query(User).filter(User.id == order.created_by).first()
        assignee = db.query(User).filter(User.id == order.assignee_id).first() if order.assignee_id else None
        
        order_list.append({
            "id": order.id,
            "order_no": order.order_no,
            "title": order.title,
            "work_type": order.work_type,
            "work_type_display": get_work_order_type_display(order.work_type),
            "priority": order.priority,
            "priority_display": get_priority_display(order.priority),
            "status": order.status,
            "status_display": get_work_order_status_display(order.status),
            "created_by": order.created_by,
            "creator_name": creator.real_name if creator else None,
            "assignee_id": order.assignee_id,
            "assignee_name": assignee.real_name if assignee else None,
            "expected_complete_at": order.expected_complete_at.isoformat() if order.expected_complete_at else None,
            "created_at": order.created_at.isoformat() if order.created_at else None,
        })
    
    return ListResponse(
        code=200,
        message="获取成功",
        data={
            "list": order_list,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": total,
                "total_pages": (total + page_size - 1) // page_size
            }
        }
    )


@router.get("/{order_id}", response_model=ApiResponse, summary="获取工单详情")
async def get_work_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取工单详细信息
    """
    order = db.query(WorkOrder).filter(
        WorkOrder.id == order_id,
        WorkOrder.is_deleted == False
    ).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="工单不存在"
        )
    
    # 获取关联信息
    creator = db.query(User).filter(User.id == order.created_by).first()
    assignee = db.query(User).filter(User.id == order.assignee_id).first() if order.assignee_id else None
    approver = db.query(User).filter(User.id == order.approved_by).first() if order.approved_by else None
    
    # 获取流转记录
    flows = []
    for flow in order.flows:
        operator = db.query(User).filter(User.id == flow.operator_id).first()
        flows.append({
            "id": flow.id,
            "operation_type": flow.operation_type,
            "operation_type_display": flow.get_operation_type_display(),
            "from_status": flow.from_status,
            "to_status": flow.to_status,
            "content": flow.content,
            "operator_id": flow.operator_id,
            "operator_name": operator.real_name if operator else None,
            "created_at": flow.created_at.isoformat() if flow.created_at else None,
        })
    
    return ApiResponse(
        code=200,
        message="获取成功",
        data={
            "id": order.id,
            "order_no": order.order_no,
            "title": order.title,
            "description": order.description,
            "work_type": order.work_type,
            "work_type_display": get_work_order_type_display(order.work_type),
            "priority": order.priority,
            "priority_display": get_priority_display(order.priority),
            "status": order.status,
            "status_display": get_work_order_status_display(order.status),
            "created_by": order.created_by,
            "creator_name": creator.real_name if creator else None,
            "assignee_id": order.assignee_id,
            "assignee_name": assignee.real_name if assignee else None,
            "approved_by": order.approved_by,
            "approver_name": approver.real_name if approver else None,
            "approved_at": order.approved_at.isoformat() if order.approved_at else None,
            "approval_comment": order.approval_comment,
            "expected_complete_at": order.expected_complete_at.isoformat() if order.expected_complete_at else None,
            "started_at": order.started_at.isoformat() if order.started_at else None,
            "completed_at": order.completed_at.isoformat() if order.completed_at else None,
            "closed_at": order.closed_at.isoformat() if order.closed_at else None,
            "satisfaction_score": float(order.satisfaction_score) if order.satisfaction_score else None,
            "satisfaction_comment": order.satisfaction_comment,
            "attachments": order.attachments,
            "related_assets": order.related_assets,
            "related_services": order.related_services,
            "tags": order.tags,
            "created_at": order.created_at.isoformat() if order.created_at else None,
            "updated_at": order.updated_at.isoformat() if order.updated_at else None,
            "flows": flows
        }
    )


@router.post("", response_model=ApiResponse, summary="创建工单")
async def create_work_order(
    request: CreateWorkOrderRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    创建运维工单（草稿状态）
    """
    # 生成工单编号
    order_no = generate_work_order_no(db)
    
    # 创建工单
    work_order = WorkOrder(
        order_no=order_no,
        title=request.title,
        description=request.description,
        work_type=request.work_type,
        priority=request.priority,
        status=WorkOrderStatus.DRAFT.value,
        created_by=current_user.id,
        expected_complete_at=request.expected_complete_at,
        attachments=request.attachments,
        related_assets=request.related_assets,
        related_services=request.related_services,
        tags=request.tags
    )
    
    db.add(work_order)
    db.commit()
    db.refresh(work_order)
    
    # 添加流转记录
    add_work_order_flow(
        db=db,
        work_order_id=work_order.id,
        operator_id=current_user.id,
        operation_type=OperationType.CREATE.value,
        to_status=WorkOrderStatus.DRAFT.value,
        content=f"创建工单：{request.title}"
    )
    
    return ApiResponse(
        code=200,
        message="创建成功",
        data={"id": work_order.id, "order_no": work_order.order_no}
    )


@router.put("/{order_id}", response_model=ApiResponse, summary="更新工单")
async def update_work_order(
    order_id: int,
    request: UpdateWorkOrderRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新工单信息（仅草稿状态可编辑）
    """
    order = db.query(WorkOrder).filter(
        WorkOrder.id == order_id,
        WorkOrder.is_deleted == False
    ).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="工单不存在"
        )
    
    # 只有草稿状态可以编辑
    if order.status != WorkOrderStatus.DRAFT.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只有草稿状态的工单可以编辑"
        )
    
    # 只能编辑自己创建的工单
    if order.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只能编辑自己创建的工单"
        )
    
    # 更新字段
    if request.title is not None:
        order.title = request.title
    if request.description is not None:
        order.description = request.description
    if request.work_type is not None:
        order.work_type = request.work_type
    if request.priority is not None:
        order.priority = request.priority
    if request.expected_complete_at is not None:
        order.expected_complete_at = request.expected_complete_at
    if request.attachments is not None:
        order.attachments = request.attachments
    if request.related_assets is not None:
        order.related_assets = request.related_assets
    if request.related_services is not None:
        order.related_services = request.related_services
    if request.tags is not None:
        order.tags = request.tags
    
    db.commit()
    db.refresh(order)
    
    # 添加流转记录
    add_work_order_flow(
        db=db,
        work_order_id=order.id,
        operator_id=current_user.id,
        operation_type=OperationType.UPDATE.value,
        content="更新工单信息"
    )
    
    return ApiResponse(
        code=200,
        message="更新成功",
        data={"id": order.id, "order_no": order.order_no}
    )


@router.post("/{order_id}/submit", response_model=ApiResponse, summary="提交工单")
async def submit_work_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    提交工单（草稿 -> 待审批）
    """
    order = db.query(WorkOrder).filter(
        WorkOrder.id == order_id,
        WorkOrder.is_deleted == False
    ).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="工单不存在"
        )
    
    # 只能提交自己创建的工单
    if order.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只能提交自己创建的工单"
        )
    
    # 检查状态
    if order.status != WorkOrderStatus.DRAFT.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只有草稿状态的工单可以提交"
        )
    
    # 更新状态
    old_status = order.status
    order.status = WorkOrderStatus.PENDING.value
    db.commit()
    
    # 添加流转记录
    add_work_order_flow(
        db=db,
        work_order_id=order.id,
        operator_id=current_user.id,
        operation_type=OperationType.SUBMIT.value,
        from_status=old_status,
        to_status=WorkOrderStatus.PENDING.value,
        content="提交工单审批"
    )
    
    return ApiResponse(
        code=200,
        message="提交成功",
        data={"id": order.id, "status": order.status}
    )


@router.post("/{order_id}/approve", response_model=ApiResponse, summary="审批工单")
async def approve_work_order(
    order_id: int,
    request: ApproveWorkOrderRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    审批工单（待审批 -> 已审批/已驳回）
    
    需要管理员权限
    """
    # 检查管理员权限
    role_codes = get_user_role_codes(current_user)
    if "admin" not in role_codes:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限"
        )
    
    order = db.query(WorkOrder).filter(
        WorkOrder.id == order_id,
        WorkOrder.is_deleted == False
    ).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="工单不存在"
        )
    
    # 检查状态
    if order.status != WorkOrderStatus.PENDING.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只有待审批状态的工单可以审批"
        )
    
    # 更新状态
    old_status = order.status
    if request.approved:
        order.status = WorkOrderStatus.APPROVED.value
        order.approved_by = current_user.id
        order.approved_at = datetime.utcnow()
        order.approval_comment = request.comment
        operation_type = OperationType.APPROVE.value
        message = "审批通过"
    else:
        order.status = WorkOrderStatus.REJECTED.value
        order.approved_by = current_user.id
        order.approved_at = datetime.utcnow()
        order.approval_comment = request.comment
        operation_type = OperationType.REJECT.value
        message = "审批驳回"
    
    db.commit()
    
    # 添加流转记录
    add_work_order_flow(
        db=db,
        work_order_id=order.id,
        operator_id=current_user.id,
        operation_type=operation_type,
        from_status=old_status,
        to_status=order.status,
        content=request.comment or message
    )
    
    return ApiResponse(
        code=200,
        message=message,
        data={"id": order.id, "status": order.status}
    )


@router.post("/{order_id}/assign", response_model=ApiResponse, summary="分配工单")
async def assign_work_order(
    order_id: int,
    request: AssignWorkOrderRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    分配工单给 SRE 工程师
    
    需要管理员权限
    """
    # 检查管理员权限
    role_codes = get_user_role_codes(current_user)
    if "admin" not in role_codes:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限"
        )
    
    order = db.query(WorkOrder).filter(
        WorkOrder.id == order_id,
        WorkOrder.is_deleted == False
    ).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="工单不存在"
        )
    
    # 检查状态
    if order.status != WorkOrderStatus.APPROVED.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只有已审批状态的工单可以分配"
        )
    
    # 检查分配的用户是否存在
    assignee = db.query(User).filter(
        User.id == request.assignee_id,
        User.is_active == True,
        User.is_deleted == False
    ).first()
    
    if not assignee:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="分配的用户不存在或已被禁用"
        )
    
    # 更新状态
    old_status = order.status
    order.assignee_id = request.assignee_id
    order.status = WorkOrderStatus.PROCESSING.value
    order.started_at = datetime.utcnow()
    db.commit()
    
    # 添加流转记录
    add_work_order_flow(
        db=db,
        work_order_id=order.id,
        operator_id=current_user.id,
        operation_type=OperationType.ASSIGN.value,
        from_status=old_status,
        to_status=WorkOrderStatus.PROCESSING.value,
        content=f"分配给：{assignee.real_name}"
    )
    
    return ApiResponse(
        code=200,
        message="分配成功",
        data={"id": order.id, "assignee_id": order.assignee_id, "status": order.status}
    )


@router.post("/{order_id}/process", response_model=ApiResponse, summary="处理工单")
async def process_work_order(
    order_id: int,
    request: ProcessWorkOrderRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    处理工单（添加处理记录）
    
    只有分配的处理人可以添加处理记录
    """
    order = db.query(WorkOrder).filter(
        WorkOrder.id == order_id,
        WorkOrder.is_deleted == False
    ).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="工单不存在"
        )
    
    # 检查权限（管理员或分配的处理人）
    role_codes = get_user_role_codes(current_user)
    if "admin" not in role_codes and order.assignee_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有分配的处理人可以添加处理记录"
        )
    
    # 检查状态
    if order.status != WorkOrderStatus.PROCESSING.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只有处理中状态的工单可以添加处理记录"
        )
    
    # 添加流转记录
    add_work_order_flow(
        db=db,
        work_order_id=order.id,
        operator_id=current_user.id,
        operation_type=OperationType.PROCESS.value,
        content=request.content,
        attachments=request.attachments
    )
    
    return ApiResponse(
        code=200,
        message="处理记录已添加",
        data={"id": order.id}
    )


@router.post("/{order_id}/complete", response_model=ApiResponse, summary="完成工单")
async def complete_work_order(
    order_id: int,
    request: CompleteWorkOrderRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    完成工单（处理中 -> 已完成）
    
    只有分配的处理人可以标记完成
    """
    order = db.query(WorkOrder).filter(
        WorkOrder.id == order_id,
        WorkOrder.is_deleted == False
    ).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="工单不存在"
        )
    
    # 检查权限（管理员或分配的处理人）
    role_codes = get_user_role_codes(current_user)
    if "admin" not in role_codes and order.assignee_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有分配的处理人可以标记完成"
        )
    
    # 检查状态
    if order.status != WorkOrderStatus.PROCESSING.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只有处理中状态的工单可以标记完成"
        )
    
    # 更新状态
    old_status = order.status
    order.status = WorkOrderStatus.COMPLETED.value
    order.completed_at = datetime.utcnow()
    db.commit()
    
    # 添加流转记录
    add_work_order_flow(
        db=db,
        work_order_id=order.id,
        operator_id=current_user.id,
        operation_type=OperationType.COMPLETE.value,
        from_status=old_status,
        to_status=WorkOrderStatus.COMPLETED.value,
        content=request.content,
        attachments=request.attachments
    )
    
    return ApiResponse(
        code=200,
        message="工单已完成",
        data={"id": order.id, "status": order.status}
    )


@router.post("/{order_id}/close", response_model=ApiResponse, summary="关闭工单")
async def close_work_order(
    order_id: int,
    request: CloseWorkOrderRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    关闭工单（已完成 -> 已关闭）
    
    只有工单创建人或管理员可以关闭
    """
    order = db.query(WorkOrder).filter(
        WorkOrder.id == order_id,
        WorkOrder.is_deleted == False
    ).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="工单不存在"
        )
    
    # 检查权限（管理员或工单创建人）
    role_codes = get_user_role_codes(current_user)
    if "admin" not in role_codes and order.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有工单创建人或管理员可以关闭工单"
        )
    
    # 检查状态
    if order.status != WorkOrderStatus.COMPLETED.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只有已完成状态的工单可以关闭"
        )
    
    # 更新状态
    old_status = order.status
    order.status = WorkOrderStatus.CLOSED.value
    order.closed_at = datetime.utcnow()
    order.satisfaction_score = request.satisfaction_score
    order.satisfaction_comment = request.satisfaction_comment
    db.commit()
    
    # 添加流转记录
    add_work_order_flow(
        db=db,
        work_order_id=order.id,
        operator_id=current_user.id,
        operation_type=OperationType.CLOSE.value,
        from_status=old_status,
        to_status=WorkOrderStatus.CLOSED.value,
        content=f"满意度评分：{request.satisfaction_score}" if request.satisfaction_score else "关闭工单"
    )
    
    return ApiResponse(
        code=200,
        message="工单已关闭",
        data={"id": order.id, "status": order.status}
    )


@router.post("/{order_id}/comment", response_model=ApiResponse, summary="评论工单")
async def comment_work_order(
    order_id: int,
    request: CommentWorkOrderRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    对工单添加评论
    """
    order = db.query(WorkOrder).filter(
        WorkOrder.id == order_id,
        WorkOrder.is_deleted == False
    ).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="工单不存在"
        )
    
    # 添加流转记录（评论类型）
    add_work_order_flow(
        db=db,
        work_order_id=order.id,
        operator_id=current_user.id,
        operation_type=OperationType.COMMENT.value,
        content=request.content,
        attachments=request.attachments
    )
    
    return ApiResponse(
        code=200,
        message="评论已添加",
        data={"id": order.id}
    )


@router.delete("/{order_id}", response_model=ApiResponse, summary="删除工单")
async def delete_work_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    软删除工单
    
    只有工单创建人或管理员可以删除
    """
    order = db.query(WorkOrder).filter(
        WorkOrder.id == order_id,
        WorkOrder.is_deleted == False
    ).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="工单不存在"
        )
    
    # 检查权限（管理员或工单创建人）
    role_codes = get_user_role_codes(current_user)
    if "admin" not in role_codes and order.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有工单创建人或管理员可以删除工单"
        )
    
    # 软删除
    order.is_deleted = True
    order.deleted_at = datetime.utcnow()
    order.deleted_by = current_user.id
    db.commit()
    
    # 添加流转记录
    add_work_order_flow(
        db=db,
        work_order_id=order.id,
        operator_id=current_user.id,
        operation_type=OperationType.DELETE.value,
        content="删除工单"
    )
    
    return ApiResponse(
        code=200,
        message="删除成功"
    )
