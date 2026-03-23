"""
路由模块
统一管理所有 API 路由
"""

from backend.src.routes import auth, users, work_orders, assets, services, statistics

__all__ = ["auth", "users", "work_orders", "assets", "services", "statistics"]
