"""
用户认证路由模块
提供用户注册、登录、获取当前用户信息等接口
"""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.src.database import get_db
from backend.src.models.user import User
from backend.src.models.role import Role
from backend.src.utils.security import hash_password, verify_password
from backend.src.utils.auth import create_access_token, get_current_user


router = APIRouter(prefix="/api/auth", tags=["认证"])
security = HTTPBearer()


# 请求模型
class RegisterRequest(BaseModel):
    """用户注册请求"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    password: str = Field(..., min_length=6, max_length=50, description="密码")
    real_name: str = Field(..., min_length=2, max_length=50, description="真实姓名")
    email: str = Field(None, max_length=100, description="邮箱")
    phone: str = Field(None, max_length=20, description="手机号")
    department_id: int = Field(None, description="部门ID")


class LoginRequest(BaseModel):
    """用户登录请求"""
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


class ChangePasswordRequest(BaseModel):
    """修改密码请求"""
    old_password: str = Field(..., description="原密码")
    new_password: str = Field(..., min_length=6, max_length=50, description="新密码")


class TokenResponse(BaseModel):
    """Token 响应"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class UserInfoResponse(BaseModel):
    """用户信息响应"""
    id: int
    username: str
    real_name: str
    email: str = None
    phone: str = None
    department_id: int = None
    roles: list = []
    created_at: str = None


# 响应模型
class ApiResponse(BaseModel):
    """统一 API 响应格式"""
    code: int
    message: str
    data: dict = None


@router.post("/register", response_model=ApiResponse, summary="用户注册")
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """
    用户注册接口
    
    - 检查用户名是否已存在
    - 创建新用户
    - 分配默认角色（运维需求方）
    """
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
    
    # 创建新用户
    new_user = User(
        username=request.username,
        password_hash=hash_password(request.password),
        real_name=request.real_name,
        email=request.email,
        phone=request.phone,
        department_id=request.department_id,
        is_active=True
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # 分配默认角色（运维需求方）
    default_role = db.query(Role).filter(Role.code == "requester").first()
    if default_role:
        new_user.roles.append(default_role)
        db.commit()
    
    return ApiResponse(
        code=200,
        message="注册成功",
        data={"user_id": new_user.id, "username": new_user.username}
    )


@router.post("/login", response_model=ApiResponse, summary="用户登录")
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    用户登录接口
    
    - 验证用户名和密码
    - 生成 JWT Token
    - 更新最后登录时间
    """
    # 查询用户
    user = db.query(User).filter(
        User.username == request.username,
        User.is_active == True,
        User.is_deleted == False
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    # 验证密码
    if not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    # 更新最后登录时间
    user.last_login_at = datetime.utcnow()
    db.commit()
    
    # 生成 Token
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return ApiResponse(
        code=200,
        message="登录成功",
        data={
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": 60 * 24  # 24小时
        }
    )


@router.get("/me", response_model=ApiResponse, summary="获取当前用户信息")
async def get_me(current_user: User = Depends(get_current_user)):
    """
    获取当前登录用户信息
    
    需要携带有效的 JWT Token
    """
    # 获取用户角色
    roles = [{"id": role.id, "name": role.name, "code": role.code} for role in current_user.roles]
    
    user_info = UserInfoResponse(
        id=current_user.id,
        username=current_user.username,
        real_name=current_user.real_name,
        email=current_user.email,
        phone=current_user.phone,
        department_id=current_user.department_id,
        roles=roles,
        created_at=current_user.created_at.isoformat() if current_user.created_at else None
    )
    
    return ApiResponse(
        code=200,
        message="获取成功",
        data=user_info.dict()
    )


@router.put("/password", response_model=ApiResponse, summary="修改密码")
async def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    修改当前用户密码
    
    需要携带有效的 JWT Token
    """
    # 验证原密码
    if not verify_password(request.old_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="原密码错误"
        )
    
    # 更新密码
    current_user.password_hash = hash_password(request.new_password)
    db.commit()
    
    return ApiResponse(
        code=200,
        message="密码修改成功"
    )


@router.post("/logout", response_model=ApiResponse, summary="用户登出")
async def logout():
    """
    用户登出接口
    
    前端需要清除本地存储的 Token
    """
    return ApiResponse(
        code=200,
        message="登出成功"
    )
