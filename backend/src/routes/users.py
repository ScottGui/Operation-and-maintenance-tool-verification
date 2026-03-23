"""
用户管理路由模块
提供用户的增删改查等管理接口
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.src.database import get_db
from backend.src.models.user import User, Department
from backend.src.models.role import Role
from backend.src.utils.security import hash_password
from backend.src.utils.auth import get_current_user


router = APIRouter(prefix="/api/users", tags=["用户管理"])


# 请求模型
class CreateUserRequest(BaseModel):
    """创建用户请求"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    password: str = Field(..., min_length=6, max_length=50, description="密码")
    real_name: str = Field(..., min_length=2, max_length=50, description="真实姓名")
    email: Optional[str] = Field(None, max_length=100, description="邮箱")
    phone: Optional[str] = Field(None, max_length=20, description="手机号")
    department_id: Optional[int] = Field(None, description="部门ID")
    role_ids: Optional[List[int]] = Field([], description="角色ID列表")
    is_active: bool = Field(True, description="是否启用")


class UpdateUserRequest(BaseModel):
    """更新用户请求"""
    real_name: Optional[str] = Field(None, min_length=2, max_length=50, description="真实姓名")
    email: Optional[str] = Field(None, max_length=100, description="邮箱")
    phone: Optional[str] = Field(None, max_length=20, description="手机号")
    department_id: Optional[int] = Field(None, description="部门ID")
    role_ids: Optional[List[int]] = Field(None, description="角色ID列表")
    is_active: Optional[bool] = Field(None, description="是否启用")


class ResetPasswordRequest(BaseModel):
    """重置密码请求"""
    new_password: str = Field(..., min_length=6, max_length=50, description="新密码")


# 响应模型
class UserResponse(BaseModel):
    """用户响应"""
    id: int
    username: str
    real_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    department_id: Optional[int] = None
    department_name: Optional[str] = None
    roles: List[dict] = []
    is_active: bool
    created_at: Optional[str] = None
    last_login_at: Optional[str] = None


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


def check_admin_permission(current_user: User):
    """检查当前用户是否有管理员权限"""
    role_codes = [role.code for role in current_user.roles]
    if "admin" not in role_codes:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，需要管理员权限"
        )


@router.get("", response_model=ListResponse, summary="获取用户列表")
async def get_users(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    keyword: Optional[str] = Query(None, description="搜索关键词（用户名/真实姓名）"),
    department_id: Optional[int] = Query(None, description="部门ID筛选"),
    is_active: Optional[bool] = Query(None, description="状态筛选"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取用户列表
    
    支持分页、搜索、筛选
    """
    # 构建查询
    query = db.query(User).filter(User.is_deleted == False)
    
    # 搜索关键词
    if keyword:
        query = query.filter(
            (User.username.contains(keyword)) | 
            (User.real_name.contains(keyword))
        )
    
    # 部门筛选
    if department_id:
        query = query.filter(User.department_id == department_id)
    
    # 状态筛选
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    
    # 统计总数
    total = query.count()
    
    # 分页
    users = query.offset((page - 1) * page_size).limit(page_size).all()
    
    # 构建响应数据
    user_list = []
    for user in users:
        department = db.query(Department).filter(Department.id == user.department_id).first()
        roles = [{"id": role.id, "name": role.name, "code": role.code} for role in user.roles]
        
        user_list.append({
            "id": user.id,
            "username": user.username,
            "real_name": user.real_name,
            "email": user.email,
            "phone": user.phone,
            "department_id": user.department_id,
            "department_name": department.name if department else None,
            "roles": roles,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None
        })
    
    return ListResponse(
        code=200,
        message="获取成功",
        data={
            "list": user_list,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": total,
                "total_pages": (total + page_size - 1) // page_size
            }
        }
    )


@router.get("/{user_id}", response_model=ApiResponse, summary="获取用户详情")
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取指定用户的详细信息
    """
    user = db.query(User).filter(
        User.id == user_id,
        User.is_deleted == False
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    department = db.query(Department).filter(Department.id == user.department_id).first()
    roles = [{"id": role.id, "name": role.name, "code": role.code} for role in user.roles]
    
    return ApiResponse(
        code=200,
        message="获取成功",
        data={
            "id": user.id,
            "username": user.username,
            "real_name": user.real_name,
            "email": user.email,
            "phone": user.phone,
            "department_id": user.department_id,
            "department_name": department.name if department else None,
            "roles": roles,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None,
            "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None
        }
    )


@router.post("", response_model=ApiResponse, summary="创建用户")
async def create_user(
    request: CreateUserRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    创建新用户（管理员权限）
    """
    # 检查管理员权限
    check_admin_permission(current_user)
    
    # 检查用户名是否已存在
    existing_user = db.query(User).filter(User.username == request.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    # 检查邮箱是否已存在
    if request.email:
        existing_email = db.query(User).filter(User.email == request.email).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已被使用"
            )
    
    # 创建用户
    new_user = User(
        username=request.username,
        password_hash=hash_password(request.password),
        real_name=request.real_name,
        email=request.email,
        phone=request.phone,
        department_id=request.department_id,
        is_active=request.is_active
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # 分配角色
    if request.role_ids:
        roles = db.query(Role).filter(Role.id.in_(request.role_ids)).all()
        new_user.roles = roles
        db.commit()
    
    return ApiResponse(
        code=200,
        message="创建成功",
        data={"id": new_user.id, "username": new_user.username}
    )


@router.put("/{user_id}", response_model=ApiResponse, summary="更新用户")
async def update_user(
    user_id: int,
    request: UpdateUserRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新用户信息（管理员权限）
    """
    # 检查管理员权限
    check_admin_permission(current_user)
    
    # 查询用户
    user = db.query(User).filter(
        User.id == user_id,
        User.is_deleted == False
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 更新字段
    if request.real_name is not None:
        user.real_name = request.real_name
    if request.email is not None:
        # 检查邮箱是否被其他用户使用
        if request.email != user.email:
            existing_email = db.query(User).filter(
                User.email == request.email,
                User.id != user_id
            ).first()
            if existing_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="邮箱已被使用"
                )
        user.email = request.email
    if request.phone is not None:
        user.phone = request.phone
    if request.department_id is not None:
        user.department_id = request.department_id
    if request.is_active is not None:
        user.is_active = request.is_active
    
    # 更新角色
    if request.role_ids is not None:
        roles = db.query(Role).filter(Role.id.in_(request.role_ids)).all()
        user.roles = roles
    
    db.commit()
    db.refresh(user)
    
    return ApiResponse(
        code=200,
        message="更新成功",
        data={"id": user.id, "username": user.username}
    )


@router.delete("/{user_id}", response_model=ApiResponse, summary="删除用户")
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    软删除用户（管理员权限）
    """
    # 检查管理员权限
    check_admin_permission(current_user)
    
    # 不能删除自己
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能删除当前登录用户"
        )
    
    # 查询用户
    user = db.query(User).filter(
        User.id == user_id,
        User.is_deleted == False
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 软删除
    user.is_deleted = True
    user.is_active = False
    db.commit()
    
    return ApiResponse(
        code=200,
        message="删除成功"
    )


@router.post("/{user_id}/reset-password", response_model=ApiResponse, summary="重置用户密码")
async def reset_password(
    user_id: int,
    request: ResetPasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    重置指定用户的密码（管理员权限）
    """
    # 检查管理员权限
    check_admin_permission(current_user)
    
    # 查询用户
    user = db.query(User).filter(
        User.id == user_id,
        User.is_deleted == False
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 重置密码
    user.password_hash = hash_password(request.new_password)
    db.commit()
    
    return ApiResponse(
        code=200,
        message="密码重置成功"
    )
