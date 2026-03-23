# 项目规则

## 项目概述
- 项目名称：AI 原生 Web 应用
- 架构：前后端分离
- 前端技术栈：**React 19 + Vite**
- 后端技术栈：**FastAPI + SQLite**
- 目标：构建一个智能化的 Web 应用

## 开发规范

### 代码风格
- 使用中文注释
- 变量命名使用小驼峰（camelCase）
- 组件/类命名使用大驼峰（PascalCase）

### 前端文件组织（frontend/ 目录）
- 组件放在 `frontend/src/components/` 目录
- 页面放在 `frontend/src/pages/` 目录
- 工具函数放在 `frontend/src/utils/` 目录
- 样式文件放在 `frontend/src/styles/` 目录
- API 调用放在 `frontend/src/api/` 目录

### 后端文件组织（backend/ 目录）
- 路由放在 `backend/src/routes/` 目录
- 控制器放在 `backend/src/controllers/` 目录
- 数据模型放在 `backend/src/models/` 目录
- 中间件放在 `backend/src/middleware/` 目录
- 工具函数放在 `backend/src/utils/` 目录

### AI 协作规则
1. 每次修改前先阅读相关文件
2. 修改后必须更新 CHANGELOG.md
3. 重要决策需要记录在 PRD.md 中
4. 使用 TodoWrite 工具跟踪任务进度

## 版本管理
- 使用 Git 进行版本控制
- 提交信息使用中文
- 每次迭代创建一个新的分支
