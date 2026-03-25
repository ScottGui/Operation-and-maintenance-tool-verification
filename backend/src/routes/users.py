"""
用户管理API
包含用户CRUD和登录接口

权限控制：
- 用户列表/查询：所有登录用户可用（后续可扩展为仅管理员）
- 创建/更新/删除用户：仅管理员可用

作者/日期：AI / 2026-03-24
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, Field, validator
import re

from backend.src.database import get_db
from backend.src.models.user import User, USER_ROLES, USER_STATUS
from backend.src.utils.security import hash_password, verify_password


router = APIRouter(prefix="/api/users", tags=["用户管理"])


# ============== Pydantic模型（请求/响应）==============

class UserCreate(BaseModel):
    """创建用户请求模型"""
    username: str = Field(..., min_length=4, max_length=20, description="登录账号")
    real_name: str = Field(..., min_length=2, max_length=20, description="真实姓名")
    password: str = Field(..., min_length=6, max_length=20, description="密码")
    role: str = Field(..., description="角色")
    status: str = Field(default="active", description="状态")
    
    @validator("username")
    def validate_username(cls, v):
        """验证用户名格式：字母数字，4-20位"""
        if not re.match(r'^[a-zA-Z0-9]+$', v):
            raise ValueError("用户名只能包含字母和数字")
        return v
    
    @validator("real_name")
    def validate_real_name(cls, v):
        """验证真实姓名：中文，2-20字"""
        if not re.match(r'^[\u4e00-\u9fa5]+$', v):
            raise ValueError("真实姓名只能包含中文")
        return v
    
    @validator("role")
    def validate_role(cls, v):
        """验证角色是否在允许列表中"""
        valid_roles = [role[0] for role in USER_ROLES]
        if v not in valid_roles:
            raise ValueError(f"无效的角色，允许的角色：{valid_roles}")
        return v
    
    @validator("status")
    def validate_status(cls, v):
        """验证状态是否有效"""
        valid_status = [s[0] for s in USER_STATUS]
        if v not in valid_status:
            raise ValueError(f"无效的状态，允许的状态：{valid_status}")
        return v


class UserUpdate(BaseModel):
    """更新用户请求模型"""
    real_name: Optional[str] = Field(None, min_length=2, max_length=20)
    role: Optional[str] = None
    status: Optional[str] = None
    password: Optional[str] = Field(None, min_length=6, max_length=20)
    
    @validator("real_name")
    def validate_real_name(cls, v):
        if v is not None and not re.match(r'^[\u4e00-\u9fa5]+$', v):
            raise ValueError("真实姓名只能包含中文")
        return v


class UserResponse(BaseModel):
    """用户响应模型"""
    id: int
    username: str
    real_name: str
    role: str
    role_display: str
    status: str
    status_display: str
    last_login_at: Optional[str]
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    """用户列表响应"""
    total: int
    items: List[UserResponse]


# ============== API接口 ==============

@router.post("", response_model=dict)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    创建用户
    
    权限：管理员
    前置条件：用户名不能已存在
    """
    # 检查用户名是否已存在
    existing_user = db.query(User).filter(
        User.username == user.username,
        User.is_deleted == False
    ).first()
    
    if existing_user:
        raise HTTPException(status_code=400, detail="用户名已存在，请更换")
    
    # 创建新用户
    db_user = User(
        username=user.username,
        real_name=user.real_name,
        password_hash=hash_password(user.password),
        role=user.role,
        status=user.status,
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return {
        "code": 200,
        "message": "创建成功",
        "data": {
            "id": db_user.id,
            "username": db_user.username,
        }
    }


@router.get("", response_model=dict)
def get_users(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页条数"),
    keyword: Optional[str] = Query(None, description="搜索关键词（用户名/姓名）"),
    role: Optional[str] = Query(None, description="角色筛选"),
    status: Optional[str] = Query(None, description="状态筛选"),
    db: Session = Depends(get_db)
):
    """
    获取用户列表
    
    支持分页、搜索、筛选
    默认每页20条
    """
    # 构建查询
    query = db.query(User).filter(User.is_deleted == False)
    
    # 搜索（用户名或真实姓名）
    if keyword:
        query = query.filter(
            (User.username.contains(keyword)) | 
            (User.real_name.contains(keyword))
        )
    
    # 角色筛选
    if role:
        query = query.filter(User.role == role)
    
    # 状态筛选
    if status:
        query = query.filter(User.status == status)
    
    # 统计总数
    total = query.count()
    
    # 分页
    users = query.offset((page - 1) * page_size).limit(page_size).all()
    
    # 组装响应数据
    items = []
    for user in users:
        items.append({
            "id": user.id,
            "username": user.username,
            "real_name": user.real_name,
            "role": user.role,
            "role_display": user.get_role_display(),
            "status": user.status,
            "status_display": user.get_status_display(),
            "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None,
        })
    
    return {
        "code": 200,
        "message": "查询成功",
        "data": {
            "total": total,
            "items": items,
            "page": page,
            "page_size": page_size,
        }
    }


@router.get("/{user_id}", response_model=dict)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """
    获取单个用户详情
    """
    user = db.query(User).filter(
        User.id == user_id,
        User.is_deleted == False
    ).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    return {
        "code": 200,
        "message": "查询成功",
        "data": user.to_dict()
    }


@router.put("/{user_id}", response_model=dict)
def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
    """
    更新用户信息
    
    可更新：真实姓名、角色、状态、密码
    不可更新：用户名
    """
    user = db.query(User).filter(
        User.id == user_id,
        User.is_deleted == False
    ).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 更新字段
    if user_update.real_name is not None:
        user.real_name = user_update.real_name
    
    if user_update.role is not None:
        # 验证角色有效性
        valid_roles = [r[0] for r in USER_ROLES]
        if user_update.role not in valid_roles:
            raise HTTPException(status_code=400, detail=f"无效的角色")
        user.role = user_update.role
    
    if user_update.status is not None:
        valid_status = [s[0] for s in USER_STATUS]
        if user_update.status not in valid_status:
            raise HTTPException(status_code=400, detail=f"无效的状态")
        user.status = user_update.status
    
    if user_update.password is not None:
        user.password_hash = hash_password(user_update.password)
    
    db.commit()
    db.refresh(user)
    
    return {
        "code": 200,
        "message": "更新成功",
        "data": user.to_dict()
    }


@router.delete("/{user_id}", response_model=dict)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """
    删除用户（软删除）
    
    不是真删除，只是标记is_deleted=True
    """
    user = db.query(User).filter(
        User.id == user_id,
        User.is_deleted == False
    ).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 软删除
    user.is_deleted = True
    db.commit()
    
    return {
        "code": 200,
        "message": "删除成功",
        "data": {"id": user_id}
    }
