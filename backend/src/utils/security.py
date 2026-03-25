"""
安全工具函数
包含密码加密、验证等功能

安全规范：
- 使用bcrypt加密密码（不可逆）
- 禁止明文存储密码
- 禁止日志打印密码

作者/日期：AI / 2026-03-24
"""

from passlib.context import CryptContext

# 创建密码上下文，使用bcrypt算法
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    加密密码
    
    输入：明文密码
    输出：加密后的哈希字符串
    
    示例：
        hash = hash_password("123456")
        # 返回：$2b$12$xxxxxxxx...
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码
    
    输入：
        plain_password: 用户输入的明文密码
        hashed_password: 数据库存储的加密密码
    输出：
        bool: 是否匹配
    
    示例：
        is_valid = verify_password("123456", "$2b$12$xxxxxxxx...")
    """
    return pwd_context.verify(plain_password, hashed_password)
