"""
资产台账路由模块
提供资产的增删改查等管理接口
"""

from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.src.database import get_db
from backend.src.models.user import User
from backend.src.models.asset import Asset, AssetType, AssetStatus
from backend.src.models.service import Service
from backend.src.utils.auth import get_current_user

router = APIRouter(prefix="/api/assets", tags=["资产台账"])


# 请求模型
class CreateAssetRequest(BaseModel):
    """创建资产请求"""
    name: str = Field(..., min_length=1, max_length=100, description="资产名称")
    asset_type: str = Field(..., description="资产类型")
    status: str = Field("in_use", description="资产状态")
    vendor: Optional[str] = Field(None, max_length=100, description="厂商")
    model: Optional[str] = Field(None, max_length=100, description="型号")
    serial_number: Optional[str] = Field(None, max_length=100, description="序列号")
    configuration: Optional[str] = Field(None, description="配置信息（JSON）")
    location: Optional[str] = Field(None, max_length=200, description="存放位置")
    service_id: Optional[int] = Field(None, description="所属服务ID")
    owner_id: Optional[int] = Field(None, description="负责人ID")
    purchase_date: Optional[datetime] = Field(None, description="购买日期")
    warranty_expire_date: Optional[datetime] = Field(None, description="保修到期日")
    purchase_price: Optional[float] = Field(None, description="购买价格")
    ip_address: Optional[str] = Field(None, max_length=50, description="IP地址")
    remark: Optional[str] = Field(None, description="备注")


class UpdateAssetRequest(BaseModel):
    """更新资产请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="资产名称")
    asset_type: Optional[str] = Field(None, description="资产类型")
    status: Optional[str] = Field(None, description="资产状态")
    vendor: Optional[str] = Field(None, max_length=100, description="厂商")
    model: Optional[str] = Field(None, max_length=100, description="型号")
    serial_number: Optional[str] = Field(None, max_length=100, description="序列号")
    configuration: Optional[str] = Field(None, description="配置信息（JSON）")
    location: Optional[str] = Field(None, max_length=200, description="存放位置")
    service_id: Optional[int] = Field(None, description="所属服务ID")
    owner_id: Optional[int] = Field(None, description="负责人ID")
    purchase_date: Optional[datetime] = Field(None, description="购买日期")
    warranty_expire_date: Optional[datetime] = Field(None, description="保修到期日")
    purchase_price: Optional[float] = Field(None, description="购买价格")
    ip_address: Optional[str] = Field(None, max_length=50, description="IP地址")
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


def generate_asset_no(db: Session) -> str:
    """生成资产编号"""
    today = datetime.now()
    date_str = today.strftime("%Y%m%d")
    prefix = f"AST-{date_str}-"
    
    last_asset = db.query(Asset).filter(
        Asset.asset_no.like(f"{prefix}%")
    ).order_by(Asset.asset_no.desc()).first()
    
    if last_asset:
        last_no = int(last_asset.asset_no.split("-")[-1])
        new_no = last_no + 1
    else:
        new_no = 1
    
    return f"{prefix}{new_no:04d}"


@router.get("", response_model=ListResponse, summary="获取资产列表")
async def get_assets(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    asset_type: Optional[str] = Query(None, description="类型筛选"),
    status: Optional[str] = Query(None, description="状态筛选"),
    service_id: Optional[int] = Query(None, description="服务ID筛选"),
    owner_id: Optional[int] = Query(None, description="负责人ID筛选"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取资产列表
    
    支持分页、搜索、筛选
    """
    query = db.query(Asset).filter(Asset.is_deleted == False)
    
    # 搜索关键词
    if keyword:
        query = query.filter(
            (Asset.name.contains(keyword)) |
            (Asset.asset_no.contains(keyword)) |
            (Asset.ip_address.contains(keyword))
        )
    
    # 类型筛选
    if asset_type:
        query = query.filter(Asset.asset_type == asset_type)
    
    # 状态筛选
    if status:
        query = query.filter(Asset.status == status)
    
    # 服务筛选
    if service_id:
        query = query.filter(Asset.service_id == service_id)
    
    # 负责人筛选
    if owner_id:
        query = query.filter(Asset.owner_id == owner_id)
    
    # 统计总数
    total = query.count()
    
    # 分页
    assets = query.order_by(Asset.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    # 构建响应数据
    asset_list = []
    for asset in assets:
        service = db.query(Service).filter(Service.id == asset.service_id).first() if asset.service_id else None
        owner = db.query(User).filter(User.id == asset.owner_id).first() if asset.owner_id else None
        
        asset_list.append({
            "id": asset.id,
            "asset_no": asset.asset_no,
            "name": asset.name,
            "asset_type": asset.asset_type,
            "asset_type_display": asset.get_asset_type_display(),
            "status": asset.status,
            "status_display": asset.get_status_display(),
            "vendor": asset.vendor,
            "model": asset.model,
            "ip_address": asset.ip_address,
            "location": asset.location,
            "service_id": asset.service_id,
            "service_name": service.name if service else None,
            "owner_id": asset.owner_id,
            "owner_name": owner.real_name if owner else None,
            "purchase_date": asset.purchase_date.isoformat() if asset.purchase_date else None,
            "warranty_expire_date": asset.warranty_expire_date.isoformat() if asset.warranty_expire_date else None,
            "created_at": asset.created_at.isoformat() if asset.created_at else None,
        })
    
    return ListResponse(
        code=200,
        message="获取成功",
        data={
            "list": asset_list,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": total,
                "total_pages": (total + page_size - 1) // page_size
            }
        }
    )


@router.get("/{asset_id}", response_model=ApiResponse, summary="获取资产详情")
async def get_asset(
    asset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取资产详细信息
    """
    asset = db.query(Asset).filter(
        Asset.id == asset_id,
        Asset.is_deleted == False
    ).first()
    
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="资产不存在"
        )
    
    service = db.query(Service).filter(Service.id == asset.service_id).first() if asset.service_id else None
    owner = db.query(User).filter(User.id == asset.owner_id).first() if asset.owner_id else None
    
    return ApiResponse(
        code=200,
        message="获取成功",
        data={
            "id": asset.id,
            "asset_no": asset.asset_no,
            "name": asset.name,
            "asset_type": asset.asset_type,
            "asset_type_display": asset.get_asset_type_display(),
            "status": asset.status,
            "status_display": asset.get_status_display(),
            "vendor": asset.vendor,
            "model": asset.model,
            "serial_number": asset.serial_number,
            "configuration": asset.configuration,
            "location": asset.location,
            "service_id": asset.service_id,
            "service_name": service.name if service else None,
            "owner_id": asset.owner_id,
            "owner_name": owner.real_name if owner else None,
            "purchase_date": asset.purchase_date.isoformat() if asset.purchase_date else None,
            "warranty_expire_date": asset.warranty_expire_date.isoformat() if asset.warranty_expire_date else None,
            "purchase_price": float(asset.purchase_price) if asset.purchase_price else None,
            "ip_address": asset.ip_address,
            "remark": asset.remark,
            "created_at": asset.created_at.isoformat() if asset.created_at else None,
            "updated_at": asset.updated_at.isoformat() if asset.updated_at else None,
        }
    )


@router.post("", response_model=ApiResponse, summary="创建资产")
async def create_asset(
    request: CreateAssetRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    创建新资产
    """
    # 生成资产编号
    asset_no = generate_asset_no(db)
    
    # 创建资产
    asset = Asset(
        asset_no=asset_no,
        name=request.name,
        asset_type=request.asset_type,
        status=request.status,
        vendor=request.vendor,
        model=request.model,
        serial_number=request.serial_number,
        configuration=request.configuration,
        location=request.location,
        service_id=request.service_id,
        owner_id=request.owner_id,
        purchase_date=request.purchase_date,
        warranty_expire_date=request.warranty_expire_date,
        purchase_price=request.purchase_price,
        ip_address=request.ip_address,
        remark=request.remark,
        created_by=current_user.id,
        updated_by=current_user.id
    )
    
    db.add(asset)
    db.commit()
    db.refresh(asset)
    
    return ApiResponse(
        code=200,
        message="创建成功",
        data={"id": asset.id, "asset_no": asset.asset_no}
    )


@router.put("/{asset_id}", response_model=ApiResponse, summary="更新资产")
async def update_asset(
    asset_id: int,
    request: UpdateAssetRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新资产信息
    """
    asset = db.query(Asset).filter(
        Asset.id == asset_id,
        Asset.is_deleted == False
    ).first()
    
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="资产不存在"
        )
    
    # 更新字段
    if request.name is not None:
        asset.name = request.name
    if request.asset_type is not None:
        asset.asset_type = request.asset_type
    if request.status is not None:
        asset.status = request.status
    if request.vendor is not None:
        asset.vendor = request.vendor
    if request.model is not None:
        asset.model = request.model
    if request.serial_number is not None:
        asset.serial_number = request.serial_number
    if request.configuration is not None:
        asset.configuration = request.configuration
    if request.location is not None:
        asset.location = request.location
    if request.service_id is not None:
        asset.service_id = request.service_id
    if request.owner_id is not None:
        asset.owner_id = request.owner_id
    if request.purchase_date is not None:
        asset.purchase_date = request.purchase_date
    if request.warranty_expire_date is not None:
        asset.warranty_expire_date = request.warranty_expire_date
    if request.purchase_price is not None:
        asset.purchase_price = request.purchase_price
    if request.ip_address is not None:
        asset.ip_address = request.ip_address
    if request.remark is not None:
        asset.remark = request.remark
    
    asset.updated_by = current_user.id
    db.commit()
    db.refresh(asset)
    
    return ApiResponse(
        code=200,
        message="更新成功",
        data={"id": asset.id, "asset_no": asset.asset_no}
    )


@router.delete("/{asset_id}", response_model=ApiResponse, summary="删除资产")
async def delete_asset(
    asset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    软删除资产
    """
    asset = db.query(Asset).filter(
        Asset.id == asset_id,
        Asset.is_deleted == False
    ).first()
    
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="资产不存在"
        )
    
    # 软删除
    asset.is_deleted = True
    asset.deleted_at = datetime.utcnow()
    db.commit()
    
    return ApiResponse(
        code=200,
        message="删除成功"
    )


@router.get("/types/list", response_model=ApiResponse, summary="获取资产类型列表")
async def get_asset_types(
    current_user: User = Depends(get_current_user)
):
    """
    获取所有资产类型
    """
    types = [
        {"value": AssetType.SERVER.value, "label": "服务器"},
        {"value": AssetType.DATABASE.value, "label": "数据库"},
        {"value": AssetType.MIDDLEWARE.value, "label": "中间件"},
        {"value": AssetType.NETWORK.value, "label": "网络设备"},
        {"value": AssetType.STORAGE.value, "label": "存储设备"},
        {"value": AssetType.SECURITY.value, "label": "安全设备"},
        {"value": AssetType.SOFTWARE.value, "label": "软件"},
        {"value": AssetType.OTHER.value, "label": "其他"},
    ]
    
    return ApiResponse(
        code=200,
        message="获取成功",
        data={"types": types}
    )


@router.get("/status/list", response_model=ApiResponse, summary="获取资产状态列表")
async def get_asset_status(
    current_user: User = Depends(get_current_user)
):
    """
    获取所有资产状态
    """
    statuses = [
        {"value": AssetStatus.IN_USE.value, "label": "在用"},
        {"value": AssetStatus.IDLE.value, "label": "闲置"},
        {"value": AssetStatus.MAINTENANCE.value, "label": "维护中"},
        {"value": AssetStatus.RETIRED.value, "label": "已下线"},
        {"value": AssetStatus.RESERVED.value, "label": "预留"},
    ]
    
    return ApiResponse(
        code=200,
        message="获取成功",
        data={"statuses": statuses}
    )
