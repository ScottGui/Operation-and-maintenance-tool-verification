"""
认证相关API
包含登录、登出接口

安全规范：
- 密码使用bcrypt验证
- 登录失败不提示是用户名错还是密码错（防枚举）
- 记录最后登录时间

作者/日期：AI / 2026-03-24
"""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from backend.src.database import get_db
from backend.src.models.user import User
from backend.src.utils.security import verify_password


router = APIRouter(prefix="/api/auth", tags=["认证"])


# ============== Pydantic模型 ==============

class LoginRequest(BaseModel):
    """登录请求"""
    username: str
    password: str


class LoginResponse(BaseModel):
    """登录响应"""
    code: int
    message: str
    data: dict


# ============== API接口 ==============

@router.post("/login", response_model=dict)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """
    用户登录
    
    输入：username, password
    输出：用户信息（不包含密码）
    
    安全：
    - 用户名或密码错误，统一返回"用户名或密码错误"
    - 账号被禁用，返回"账号已被禁用"
    """
    # 查询用户
    user = db.query(User).filter(
        User.username == login_data.username,
        User.is_deleted == False
    ).first()
    
    # 用户不存在或密码错误，统一提示（防止用户名枚举攻击）
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    
    # 检查账号状态
    if user.status == "inactive":
        raise HTTPException(status_code=403, detail="账号已被禁用，请联系管理员")
    
    # 先获取所有需要的用户信息
    user_id = user.id
    user_name = user.username
    real_name = user.real_name
    role = user.role
    
    # 获取角色显示名称
    role_map = {
        "data_consumer": "用数方",
        "requirement_manager": "需求经理",
        "operator": "运营方",
        "project_manager": "项目经理",
        "qa_manager": "质量稽核经理",
        "ops_manager": "数据运维经理",
        "team_lead": "四方组长",
        "admin": "管理员",
    }
    role_display = role_map.get(role, role)
    
    # 更新最后登录时间
    user.last_login_at = datetime.now()
    db.commit()
    
    return {
        "code": 200,
        "message": "登录成功",
        "data": {
            "user": {
                "id": user_id,
                "username": user_name,
                "real_name": real_name,
                "role": role,
                "role_display": role_display,
            },
            "token": f"fake_token_{user_id}"  # MVP阶段先用假token，后续实现JWT
        }
    }


@router.post("/logout", response_model=dict)
def logout():
    """
    用户登出
    
    MVP阶段：前端清除token即可
    后续：可以实现服务端token黑名单
    """
    return {
        "code": 200,
        "message": "登出成功",
        "data": {}
    }


# ============== 依赖注入函数 ==============

def get_current_user_simple(
    db: Session = Depends(get_db),
    authorization: str = None
):
    """
    获取当前登录用户（简化版）
    MVP阶段：从Authorization头中提取token，解析出用户ID
    
    使用方式：
        current_user: User = Depends(get_current_user_simple)
    """
    # 从Authorization头获取token
    # 格式：Bearer fake_token_{user_id}
    if not authorization:
        raise HTTPException(status_code=401, detail="未提供认证信息")
    
    # 解析token
    if authorization.startswith("Bearer "):
        token = authorization[7:]
    else:
        token = authorization
    
    # MVP阶段：fake_token_{user_id}
    if not token.startswith("fake_token_"):
        raise HTTPException(status_code=401, detail="无效的认证信息")
    
    try:
        user_id = int(token.split("_")[-1])
    except ValueError:
        raise HTTPException(status_code=401, detail="无效的认证信息")
    
    # 查询用户
    user = db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
    if not user:
        raise HTTPException(status_code=401, detail="用户不存在或已被删除")
    
    if user.status == "inactive":
        raise HTTPException(status_code=403, detail="账号已被禁用")
    
    return user
