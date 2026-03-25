"""
数据初始化脚本
创建系统初始数据：角色、权限、管理员账号、部门等
"""

from sqlalchemy.orm import Session
from backend.src.database import SessionLocal, engine
from backend.src.models import Base
from backend.src.models.role import Role, Permission, role_permission
from backend.src.models.user import User, Department
from backend.src.utils.security import hash_password


def init_permissions(db: Session):
    """初始化权限数据"""
    permissions = [
        # 用户管理权限
        {"name": "用户查看", "code": "user:view", "permission_type": "api", "resource": "users", "action": "view"},
        {"name": "用户创建", "code": "user:create", "permission_type": "api", "resource": "users", "action": "create"},
        {"name": "用户编辑", "code": "user:edit", "permission_type": "api", "resource": "users", "action": "edit"},
        {"name": "用户删除", "code": "user:delete", "permission_type": "api", "resource": "users", "action": "delete"},
        
        # 需求单管理权限
        {"name": "需求单查看", "code": "work_order:view", "permission_type": "api", "resource": "work_orders", "action": "view"},
        {"name": "需求单创建", "code": "work_order:create", "permission_type": "api", "resource": "work_orders", "action": "create"},
        {"name": "需求单编辑", "code": "work_order:edit", "permission_type": "api", "resource": "work_orders", "action": "edit"},
        {"name": "需求单删除", "code": "work_order:delete", "permission_type": "api", "resource": "work_orders", "action": "delete"},
        {"name": "需求单审批", "code": "work_order:approve", "permission_type": "api", "resource": "work_orders", "action": "approve"},
        {"name": "需求单分配", "code": "work_order:assign", "permission_type": "api", "resource": "work_orders", "action": "assign"},
        
        # 资产管理权限
        {"name": "资产查看", "code": "asset:view", "permission_type": "api", "resource": "assets", "action": "view"},
        {"name": "资产创建", "code": "asset:create", "permission_type": "api", "resource": "assets", "action": "create"},
        {"name": "资产编辑", "code": "asset:edit", "permission_type": "api", "resource": "assets", "action": "edit"},
        {"name": "资产删除", "code": "asset:delete", "permission_type": "api", "resource": "assets", "action": "delete"},
        
        # 服务管理权限
        {"name": "服务查看", "code": "service:view", "permission_type": "api", "resource": "services", "action": "view"},
        {"name": "服务创建", "code": "service:create", "permission_type": "api", "resource": "services", "action": "create"},
        {"name": "服务编辑", "code": "service:edit", "permission_type": "api", "resource": "services", "action": "edit"},
        {"name": "服务删除", "code": "service:delete", "permission_type": "api", "resource": "services", "action": "delete"},
        
        # 统计报表权限
        {"name": "统计查看", "code": "statistics:view", "permission_type": "api", "resource": "statistics", "action": "view"},
    ]
    
    created_permissions = []
    for perm_data in permissions:
        # 检查是否已存在
        existing = db.query(Permission).filter(Permission.code == perm_data["code"]).first()
        if not existing:
            perm = Permission(**perm_data)
            db.add(perm)
            created_permissions.append(perm)
    
    db.commit()
    print(f"✅ 权限数据初始化完成，共创建 {len(created_permissions)} 个权限")
    return created_permissions


def init_roles(db: Session):
    """初始化角色数据"""
    roles = [
        {
            "name": "运维管理经理",
            "code": "admin",
            "description": "系统管理员，拥有所有权限",
            "role_type": "admin",
            "is_system": True
        },
        {
            "name": "SRE运维工程师",
            "code": "sre",
            "description": "负责需求单处理和系统维护",
            "role_type": "sre",
            "is_system": True
        },
        {
            "name": "运维需求方",
            "code": "requester",
            "description": "发起运维申请的用户",
            "role_type": "requester",
            "is_system": True
        },
    ]
    
    created_roles = []
    for role_data in roles:
        # 检查是否已存在
        existing = db.query(Role).filter(Role.code == role_data["code"]).first()
        if not existing:
            role = Role(**role_data)
            db.add(role)
            created_roles.append(role)
    
    db.commit()
    print(f"✅ 角色数据初始化完成，共创建 {len(created_roles)} 个角色")
    return created_roles


def init_role_permissions(db: Session):
    """初始化角色权限关联"""
    # 获取所有角色和权限
    admin_role = db.query(Role).filter(Role.code == "admin").first()
    sre_role = db.query(Role).filter(Role.code == "sre").first()
    requester_role = db.query(Role).filter(Role.code == "requester").first()
    
    all_permissions = db.query(Permission).all()
    
    # 管理员拥有所有权限
    if admin_role and not admin_role.permissions:
        admin_role.permissions = all_permissions
        print(f"✅ 管理员角色已分配 {len(all_permissions)} 个权限")
    
    # SRE权限：需求单查看、处理、资产查看、服务查看、统计查看
    if sre_role and not sre_role.permissions:
        sre_permissions = db.query(Permission).filter(
            Permission.code.in_([
                "work_order:view", "work_order:edit",
                "asset:view", "service:view", "statistics:view"
            ])
        ).all()
        sre_role.permissions = sre_permissions
        print(f"✅ SRE角色已分配 {len(sre_permissions)} 个权限")
    
    # 需求方权限：需求单查看、创建、编辑自己的需求单
    if requester_role and not requester_role.permissions:
        requester_permissions = db.query(Permission).filter(
            Permission.code.in_([
                "work_order:view", "work_order:create", "work_order:edit"
            ])
        ).all()
        requester_role.permissions = requester_permissions
        print(f"✅ 需求方角色已分配 {len(requester_permissions)} 个权限")
    
    db.commit()


def init_departments(db: Session):
    """初始化部门数据"""
    departments = [
        {"name": "数据业务组", "code": "data_business", "sort_order": 1},
        {"name": "数据治理组", "code": "data_governance", "sort_order": 2},
        {"name": "平台建设组", "code": "platform_build", "sort_order": 3},
        {"name": "安全组", "code": "security", "sort_order": 4},
        {"name": "运维组", "code": "ops", "sort_order": 5},
        {"name": "数据运营组", "code": "data_ops", "sort_order": 6},
    ]
    
    created_departments = []
    for dept_data in departments:
        # 检查是否已存在
        existing = db.query(Department).filter(Department.code == dept_data["code"]).first()
        if not existing:
            dept = Department(**dept_data)
            db.add(dept)
            created_departments.append(dept)
    
    db.commit()
    print(f"✅ 部门数据初始化完成，共创建 {len(created_departments)} 个部门")
    return created_departments


def init_admin_user(db: Session):
    """初始化管理员账号"""
    # 检查是否已存在管理员
    existing_admin = db.query(User).filter(User.username == "admin").first()
    if existing_admin:
        print("✅ 管理员账号已存在")
        return existing_admin
    
    # 获取管理员角色
    admin_role = db.query(Role).filter(Role.code == "admin").first()
    if not admin_role:
        print("❌ 管理员角色不存在，请先初始化角色")
        return None
    
    # 创建管理员
    admin = User(
        username="admin",
        password_hash=hash_password("admin123"),
        real_name="系统管理员",
        email="admin@example.com",
        is_active=True
    )
    
    db.add(admin)
    db.commit()
    db.refresh(admin)
    
    # 分配管理员角色
    admin.roles.append(admin_role)
    db.commit()
    
    print("✅ 管理员账号创建成功")
    print("   用户名: admin")
    print("   密码: admin123")
    return admin


def init_sample_users(db: Session):
    """初始化示例用户"""
    sample_users = [
        {
            "username": "sre01",
            "password": "sre123",
            "real_name": "SRE工程师1",
            "email": "sre01@example.com",
            "role_code": "sre"
        },
        {
            "username": "requester01",
            "password": "req123",
            "real_name": "需求方1",
            "email": "req01@example.com",
            "role_code": "requester"
        },
    ]
    
    created_count = 0
    for user_data in sample_users:
        # 检查是否已存在
        existing = db.query(User).filter(User.username == user_data["username"]).first()
        if existing:
            continue
        
        # 获取角色
        role = db.query(Role).filter(Role.code == user_data["role_code"]).first()
        if not role:
            continue
        
        # 创建用户
        user = User(
            username=user_data["username"],
            password_hash=hash_password(user_data["password"]),
            real_name=user_data["real_name"],
            email=user_data["email"],
            is_active=True
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # 分配角色
        user.roles.append(role)
        db.commit()
        
        created_count += 1
        print(f"✅ 示例用户创建成功: {user_data['username']}")
    
    print(f"✅ 示例用户初始化完成，共创建 {created_count} 个用户")


def init_all_data():
    """初始化所有数据"""
    print("🚀 开始初始化系统数据...")
    print("-" * 50)
    
    # 先创建数据库表
    print("📦 创建数据库表...")
    Base.metadata.create_all(bind=engine)
    print("✅ 数据库表创建完成")
    print("-" * 50)
    
    db = SessionLocal()
    try:
        # 1. 初始化权限
        init_permissions(db)
        
        # 2. 初始化角色
        init_roles(db)
        
        # 3. 初始化角色权限关联
        init_role_permissions(db)
        
        # 4. 初始化部门
        init_departments(db)
        
        # 5. 初始化管理员账号
        init_admin_user(db)
        
        # 6. 初始化示例用户
        init_sample_users(db)
        
        print("-" * 50)
        print("✅ 数据初始化完成！")
        print("\n默认账号信息：")
        print("  管理员: admin / admin123")
        print("  SRE: sre01 / sre123")
        print("  需求方: requester01 / req123")
        
    except Exception as e:
        print(f"❌ 数据初始化失败: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    init_all_data()