"""
服务台账路由模块
提供服务的增删改查等管理接口
"""

from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.src.database import get_db
from backend.src.models.user import User
from backend.src.models.service import Service, ServiceType, ServiceStatus, ServiceLevel
from backend.src.utils.auth import get_current_user

router = APIRouter(prefix="/api/services", tags=["服务台账"])


# 请求模型
class CreateServiceRequest(BaseModel):
    """创建服务请求"""
    name: str = Field(..., min_length=1, max_length=100, description="服务名称")
    service_type: str = Field(..., description="服务类型")
    status: str = Field("running", description="服务状态")
    service_level: str = Field("p2", description="服务等级")
    description: Optional[str] = Field(None, description="服务描述")
    tech_stack: Optional[str] = Field(None, description="技术栈（JSON）")
    access_url: Optional[str] = Field(None, max_length=500, description="访问地址")
    owner_id: Optional[int] = Field(None, description="负责人ID")
    dependencies: Optional[str] = Field(None, description="依赖服务（JSON）")
    deployment_info: Optional[str] = Field(None, description="部署信息（JSON）")
    remark: Optional[str] = Field(None, description="备注")


class UpdateServiceRequest(BaseModel):
    """更新服务请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="服务名称")
    service_type: Optional[str] = Field(None, description="服务类型")
    status: Optional[str] = Field(None, description="服务状态")
    service_level: Optional[str] = Field(None, description="服务等级")
    description: Optional[str] = Field(None, description="服务描述")
    tech_stack: Optional[str] = Field(None, description="技术栈（JSON）")
    access_url: Optional[str] = Field(None, max_length=500, description="访问地址")
    owner_id: Optional[int] = Field(None, description="负责人ID")
    dependencies: Optional[str] = Field(None, description="依赖服务（JSON）")
    deployment_info: Optional[str] = Field(None, description="部署信息（JSON）")
    remark: Optional[str] = Field(None, description="备注")


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


def generate_service_no(db: Session) -> str:
    """生成服务编号"""
    today = datetime.now()
    date_str = today.strftime("%Y%m%d")
    prefix = f"SVC-{date_str}-"
    
    last_service = db.query(Service).filter(
        Service.service_no.like(f"{prefix}%")
    ).order_by(Service.service_no.desc()).first()
    
    if last_service:
        last_no = int(last_service.service_no.split("-")[-1])
        new_no = last_no + 1
    else:
        new_no = 1
    
    return f"{prefix}{new_no:04d}"


@router.get("", response_model=ListResponse, summary="获取服务列表")
async def get_services(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    service_type: Optional[str] = Query(None, description="类型筛选"),
    status: Optional[str] = Query(None, description="状态筛选"),
    service_level: Optional[str] = Query(None, description="等级筛选"),
    owner_id: Optional[int] = Query(None, description="负责人ID筛选"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取服务列表
    
    支持分页、搜索、筛选
    """
    query = db.query(Service).filter(Service.is_deleted == False)
    
    # 搜索关键词
    if keyword:
        query = query.filter(
            (Service.name.contains(keyword)) |
            (Service.service_no.contains(keyword))
        )
    
    # 类型筛选
    if service_type:
        query = query.filter(Service.service_type == service_type)
    
    # 状态筛选
    if status:
        query = query.filter(Service.status == status)
    
    # 等级筛选
    if service_level:
        query = query.filter(Service.service_level == service_level)
    
    # 负责人筛选
    if owner_id:
        query = query.filter(Service.owner_id == owner_id)
    
    # 统计总数
    total = query.count()
    
    # 分页
    services = query.order_by(Service.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    # 构建响应数据
    service_list = []
    for service in services:
        owner = db.query(User).filter(User.id == service.owner_id).first() if service.owner_id else None
        
        service_list.append({
            "id": service.id,
            "service_no": service.service_no,
            "name": service.name,
            "service_type": service.service_type,
            "service_type_display": service.get_service_type_display(),
            "status": service.status,
            "status_display": service.get_status_display(),
            "service_level": service.service_level,
            "service_level_display": service.get_service_level_display(),
            "access_url": service.access_url,
            "owner_id": service.owner_id,
            "owner_name": owner.real_name if owner else None,
            "created_at": service.created_at.isoformat() if service.created_at else None,
        })
    
    return ListResponse(
        code=200,
        message="获取成功",
        data={
            "list": service_list,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": total,
                "total_pages": (total + page_size - 1) // page_size
            }
        }
    )


@router.get("/{service_id}", response_model=ApiResponse, summary="获取服务详情")
async def get_service(
    service_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取服务详细信息
    """
    service = db.query(Service).filter(
        Service.id == service_id,
        Service.is_deleted == False
    ).first()
    
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="服务不存在"
        )
    
    owner = db.query(User).filter(User.id == service.owner_id).first() if service.owner_id else None
    
    return ApiResponse(
        code=200,
        message="获取成功",
        data={
            "id": service.id,
            "service_no": service.service_no,
            "name": service.name,
            "service_type": service.service_type,
            "service_type_display": service.get_service_type_display(),
            "status": service.status,
            "status_display": service.get_status_display(),
            "service_level": service.service_level,
            "service_level_display": service.get_service_level_display(),
            "description": service.description,
            "tech_stack": service.tech_stack,
            "access_url": service.access_url,
            "owner_id": service.owner_id,
            "owner_name": owner.real_name if owner else None,
            "dependencies": service.dependencies,
            "deployment_info": service.deployment_info,
            "remark": service.remark,
            "created_at": service.created_at.isoformat() if service.created_at else None,
            "updated_at": service.updated_at.isoformat() if service.updated_at else None,
        }
    )


@router.post("", response_model=ApiResponse, summary="创建服务")
async def create_service(
    request: CreateServiceRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    创建新服务
    """
    # 生成服务编号
    service_no = generate_service_no(db)
    
    # 创建服务
    service = Service(
        service_no=service_no,
        name=request.name,
        service_type=request.service_type,
        status=request.status,
        service_level=request.service_level,
        description=request.description,
        tech_stack=request.tech_stack,
        access_url=request.access_url,
        owner_id=request.owner_id,
        dependencies=request.dependencies,
        deployment_info=request.deployment_info,
        remark=request.remark,
        created_by=current_user.id,
        updated_by=current_user.id
    )
    
    db.add(service)
    db.commit()
    db.refresh(service)
    
    return ApiResponse(
        code=200,
        message="创建成功",
        data={"id": service.id, "service_no": service.service_no}
    )


@router.put("/{service_id}", response_model=ApiResponse, summary="更新服务")
async def update_service(
    service_id: int,
    request: UpdateServiceRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新服务信息
    """
    service = db.query(Service).filter(
        Service.id == service_id,
        Service.is_deleted == False
    ).first()
    
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="服务不存在"
        )
    
    # 更新字段
    if request.name is not None:
        service.name = request.name
    if request.service_type is not None:
        service.service_type = request.service_type
    if request.status is not None:
        service.status = request.status
    if request.service_level is not None:
        service.service_level = request.service_level
    if request.description is not None:
        service.description = request.description
    if request.tech_stack is not None:
        service.tech_stack = request.tech_stack
    if request.access_url is not None:
        service.access_url = request.access_url
    if request.owner_id is not None:
        service.owner_id = request.owner_id
    if request.dependencies is not None:
        service.dependencies = request.dependencies
    if request.deployment_info is not None:
        service.deployment_info = request.deployment_info
    if request.remark is not None:
        service.remark = request.remark
    
    service.updated_by = current_user.id
    db.commit()
    db.refresh(service)
    
    return ApiResponse(
        code=200,
        message="更新成功",
        data={"id": service.id, "service_no": service.service_no}
    )


@router.delete("/{service_id}", response_model=ApiResponse, summary="删除服务")
async def delete_service(
    service_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    软删除服务
    """
    service = db.query(Service).filter(
        Service.id == service_id,
        Service.is_deleted == False
    ).first()
    
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="服务不存在"
        )
    
    # 软删除
    service.is_deleted = True
    service.deleted_at = datetime.utcnow()
    db.commit()
    
    return ApiResponse(
        code=200,
        message="删除成功"
    )


@router.get("/types/list", response_model=ApiResponse, summary="获取服务类型列表")
async def get_service_types(
    current_user: User = Depends(get_current_user)
):
    """
    获取所有服务类型
    """
    types = [
        {"value": ServiceType.PLATFORM.value, "label": "平台服务"},
        {"value": ServiceType.DATA_SERVICE.value, "label": "数据服务"},
        {"value": ServiceType.SECURITY.value, "label": "安全服务"},
        {"value": ServiceType.MONITOR.value, "label": "监控服务"},
        {"value": ServiceType.TOOL.value, "label": "工具服务"},
        {"value": ServiceType.OTHER.value, "label": "其他"},
    ]
    
    return ApiResponse(
        code=200,
        message="获取成功",
        data={"types": types}
    )


@router.get("/status/list", response_model=ApiResponse, summary="获取服务状态列表")
async def get_service_status(
    current_user: User = Depends(get_current_user)
):
    """
    获取所有服务状态
    """
    statuses = [
        {"value": ServiceStatus.RUNNING.value, "label": "运行中"},
        {"value": ServiceStatus.STOPPED.value, "label": "已停止"},
        {"value": ServiceStatus.MAINTENANCE.value, "label": "维护中"},
        {"value": ServiceStatus.DEPRECATED.value, "label": "已弃用"},
    ]
    
    return ApiResponse(
        code=200,
        message="获取成功",
        data={"statuses": statuses}
    )


@router.get("/levels/list", response_model=ApiResponse, summary="获取服务等级列表")
async def get_service_levels(
    current_user: User = Depends(get_current_user)
):
    """
    获取所有服务等级
    """
    levels = [
        {"value": ServiceLevel.P0.value, "label": "P0-核心服务"},
        {"value": ServiceLevel.P1.value, "label": "P1-重要服务"},
        {"value": ServiceLevel.P2.value, "label": "P2-一般服务"},
        {"value": ServiceLevel.P3.value, "label": "P3-低优先级"},
    ]
    
    return ApiResponse(
        code=200,
        message="获取成功",
        data={"levels": levels}
    )
