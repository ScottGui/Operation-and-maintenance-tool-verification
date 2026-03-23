# AI 原生 Web 应用

> 一个前后端分离的智能化 Web 应用

## 项目架构

本项目采用前后端分离架构：

```
.
├── frontend/          # 前端项目
├── backend/           # 后端项目
├── docs/              # 文档
│   ├── PRD.md         # 产品需求文档
│   └── CHANGELOG.md   # 版本变更记录
└── .trae/             # AI 配置
    └── rules/         # 项目规则
```

## 目录结构

### 前端（frontend/）

```
frontend/
├── src/
│   ├── components/    # 可复用组件
│   ├── pages/         # 页面组件
│   ├── api/           # API 请求封装
│   ├── utils/         # 工具函数
│   └── styles/        # 样式文件
├── package.json
└── ...
```

### 后端（backend/）

```
backend/
├── src/
│   ├── routes/        # 路由定义
│   ├── controllers/   # 控制器（业务逻辑）
│   ├── models/        # 数据模型
│   ├── middleware/    # 中间件
│   └── utils/         # 工具函数
├── package.json
└── ...
```

## 快速开始

### 1. 安装依赖

```bash
# 前端
cd frontend
npm install

# 后端
cd backend
npm install
```

### 2. 启动开发服务器

```bash
# 前端（默认端口 3000）
cd frontend
npm run dev

# 后端（默认端口 3001）
cd backend
npm run dev
```

## 开发规范

- 使用中文注释
- 变量命名使用小驼峰（camelCase）
- 组件/类命名使用大驼峰（PascalCase）
- 每次修改后更新 CHANGELOG.md

## 技术栈

详见 [docs/PRD.md](./docs/PRD.md)

## 版本记录

详见 [docs/CHANGELOG.md](./docs/CHANGELOG.md)

## 协作规则

详见 [.trae/rules/project_rules.md](./.trae/rules/project_rules.md)
