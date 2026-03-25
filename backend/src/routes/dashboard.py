"""
工作台数据API
根据用户角色返回不同的统计数据和待办事项

作者/日期：AI / 2026-03-25
"""

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from backend.src.database import get_db
from backend.src.models.user import User
from backend.src.models.work_order import WorkOrder

router = APIRouter(prefix="/api/dashboard", tags=["工作台"])


def get_current_user_simple(authorization: str = Header(None), db: Session = Depends(get_db)) -> User:
    """
    简化的用户认证（MVP阶段使用fake_token）
    从Authorization头中提取token，查询对应用户
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未提供认证信息")
    
    token = authorization.replace("Bearer ", "")
    
    # MVP阶段：从fake_token中提取用户ID（格式：fake_token_{user_id}）
    if token.startswith("fake_token_"):
        try:
            user_id = int(token.replace("fake_token_", ""))
            user = db.query(User).filter(User.id == user_id, User.status == 'active').first()
            if user:
                return user
        except:
            pass
    
    raise HTTPException(status_code=401, detail="无效的认证信息")


@router.get("/stats", response_model=dict)
def get_dashboard_stats(
    current_user: User = Depends(get_current_user_simple),
    db: Session = Depends(get_db)
):
    """
    获取工作台统计数据
    根据用户角色返回不同的统计信息
    """
    role = current_user.role
    
    # 用数方：统计自己的需求单
    if role == 'data_consumer':
        # 我的待办：待审批的需求（需要关注处理进度）
        my_todo = db.query(WorkOrder).filter(
            WorkOrder.creator_id == current_user.id,
            WorkOrder.status.in_(['pending_review', 'rejected'])
        ).count()
        
        # 我的需求：创建的所有需求单
        my_orders = db.query(WorkOrder).filter(
            WorkOrder.creator_id == current_user.id
        ).count()
        
        # 已完成：已上线的需求单
        completed = db.query(WorkOrder).filter(
            WorkOrder.creator_id == current_user.id,
            WorkOrder.status == 'online'
        ).count()
        
        stats = {
            'myTodo': my_todo,
            'myOrders': my_orders,
            'completed': completed,
        }
    
    # 需求经理：待梳理统计
    elif role == 'requirement_manager':
        pending_analysis = db.query(WorkOrder).filter(
            WorkOrder.status == 'pending_review'
        ).count()
        
        my_analysis = db.query(WorkOrder).filter(
            WorkOrder.status == 'analyzed'
        ).count()
        
        submitted = db.query(WorkOrder).filter(
            WorkOrder.status.in_(['approved', 'solution_submitted', 'in_review', 'in_progress'])
        ).count()
        
        stats = {
            'pendingAnalysis': pending_analysis,
            'myAnalysis': my_analysis,
            'submitted': submitted,
        }
    
    # 运营方：审批统计
    elif role == 'operator':
        pending_approval = db.query(WorkOrder).filter(
            WorkOrder.status == 'analyzed'
        ).count()
        
        pending_review = db.query(WorkOrder).filter(
            WorkOrder.status == 'solution_submitted'
        ).count()
        
        processed = db.query(WorkOrder).filter(
            WorkOrder.status.in_(['approved', 'rejected'])
        ).count()
        
        today_stats = db.query(WorkOrder).filter(
            WorkOrder.status == 'in_review'
        ).count()
        
        stats = {
            'pendingApproval': pending_approval,
            'pendingReview': pending_review,
            'processed': processed,
            'todayStats': today_stats,
        }
    
    # 项目经理：实施统计
    elif role == 'project_manager':
        pending_claim = db.query(WorkOrder).filter(
            WorkOrder.status == 'in_review'
        ).count()
        
        in_progress = db.query(WorkOrder).filter(
            WorkOrder.status == 'in_progress'
        ).count()
        
        delivered = db.query(WorkOrder).filter(
            WorkOrder.status.in_(['pending_qa', 'pending_trial', 'pending_monitor', 'online'])
        ).count()
        
        stats = {
            'pendingClaim': pending_claim,
            'inProgress': in_progress,
            'delivered': delivered,
        }
    
    # 质量稽核经理：稽核统计
    elif role == 'qa_manager':
        pending_qa = db.query(WorkOrder).filter(
            WorkOrder.status == 'pending_qa'
        ).count()
        
        completed_qa = db.query(WorkOrder).filter(
            WorkOrder.status.in_(['pending_trial', 'pending_monitor', 'online'])
        ).count()
        
        stats = {
            'pendingQA': pending_qa,
            'completedQA': completed_qa,
            'passRate': '92%',
        }
    
    # 数据运维经理：运维统计
    elif role == 'ops_manager':
        pending_trial = db.query(WorkOrder).filter(
            WorkOrder.status == 'pending_trial'
        ).count()
        
        pending_monitor = db.query(WorkOrder).filter(
            WorkOrder.status == 'pending_monitor'
        ).count()
        
        online = db.query(WorkOrder).filter(
            WorkOrder.status == 'online'
        ).count()
        
        overview = db.query(WorkOrder).count()
        
        stats = {
            'pendingTrial': pending_trial,
            'pendingMonitor': pending_monitor,
            'online': online,
            'overview': overview,
        }
    
    # 四方组长：会审统计
    elif role == 'team_lead':
        pending_review = db.query(WorkOrder).filter(
            WorkOrder.status == 'in_review'
        ).count()
        
        completed_review = db.query(WorkOrder).filter(
            WorkOrder.status.in_(['in_progress', 'pending_qa', 'pending_trial', 'pending_monitor', 'online'])
        ).count()
        
        stats = {
            'pendingReview': pending_review,
            'completedReview': completed_review,
        }
    
    # 管理员：系统统计
    elif role == 'admin':
        total_users = db.query(User).filter(User.status == 'active').count()
        total_orders = db.query(WorkOrder).count()
        online_services = db.query(WorkOrder).filter(WorkOrder.status == 'online').count()
        
        stats = {
            'totalUsers': total_users,
            'totalOrders': total_orders,
            'onlineServices': online_services,
            'systemStatus': '正常',
        }
    
    else:
        stats = {}
    
    return {
        "code": 200,
        "message": "查询成功",
        "data": stats
    }


@router.get("/todos", response_model=dict)
def get_dashboard_todos(
    current_user: User = Depends(get_current_user_simple),
    db: Session = Depends(get_db)
):
    """
    获取待办事项列表
    根据用户角色返回不同的待办事项
    """
    role = current_user.role
    
    # MVP阶段：返回mock待办数据
    todos_config = {
        'data_consumer': [
            { "id": 1, "title": "需求WO-20240301已处理完成，请确认关闭", "type": "confirm_close", "createTime": "2026-03-20" },
            { "id": 2, "title": "需求WO-20240305被退回，请修改后重新提交", "type": "reject", "createTime": "2026-03-22" },
        ],
        'requirement_manager': [
            { "id": 3, "title": "有新的需求待梳理：数据查询服务", "type": "pending_analysis", "createTime": "2026-03-23" },
            { "id": 4, "title": "需求WO-20240302规格说明书待完善", "type": "pending_doc", "createTime": "2026-03-24" },
        ],
        'operator': [
            { "id": 5, "title": "需求WO-20240306待审批", "type": "pending_approval", "createTime": "2026-03-24" },
            { "id": 6, "title": "技术方案WO-20240303待会审终审", "type": "pending_final", "createTime": "2026-03-23" },
        ],
        'project_manager': [
            { "id": 7, "title": "有新的实施单待认领：WO-20240307", "type": "pending_claim", "createTime": "2026-03-24" },
            { "id": 8, "title": "实施WO-20240304被退回，请修改", "type": "reject", "createTime": "2026-03-22" },
        ],
        'qa_manager': [
            { "id": 9, "title": "实施WO-20240308待质量稽核", "type": "pending_qa", "createTime": "2026-03-24" },
        ],
        'ops_manager': [
            { "id": 10, "title": "服务WO-20240309待试运行", "type": "pending_trial", "createTime": "2026-03-24" },
        ],
        'team_lead': [
            { "id": 11, "title": "技术方案WO-20240310待会审", "type": "pending_review", "createTime": "2026-03-23" },
        ],
        'admin': [
            { "id": 12, "title": "系统运行正常，无待处理事项", "type": "system_ok", "createTime": "2026-03-25" },
        ],
    }
    
    todos = todos_config.get(role, [])
    
    return {
        "code": 200,
        "message": "查询成功",
        "data": todos[:5]  # 最多返回5条
    }
