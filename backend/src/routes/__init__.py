# -*- coding: utf-8 -*-
"""
路由模块
MVP阶段：只实现用户管理和认证相关路由
"""

from backend.src.routes import auth, users, dashboard, files

__all__ = ["auth", "users", "dashboard", "files"]
