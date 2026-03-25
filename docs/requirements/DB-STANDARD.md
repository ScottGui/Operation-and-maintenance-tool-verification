# 数据库设计规范

> 确保所有表结构风格统一

---

## 1. 命名规范

| 项目 | 规则 | 示例 |
|------|------|------|
| 表名 | 小写，下划线分隔，复数形式 | `users`, `work_orders`, `attachments` |
| 字段名 | 小写，下划线分隔 | `created_by`, `approved_at`, `is_deleted` |
| 主键 | 一律叫 `id`，自增整数 | `id INTEGER PRIMARY KEY AUTOINCREMENT` |
| 外键 | `{关联表名}_id` | `user_id`, `order_id` |
| 时间字段 | `{动作}_at` | `created_at`, `updated_at`, `approved_at` |
| 布尔字段 | `is_{形容词}` 或 `has_{名词}` | `is_deleted`, `is_active` |

---

## 2. 必备字段（每张表都要有）

```sql
-- 每张表必须包含这5个审计字段
id              INTEGER PRIMARY KEY AUTOINCREMENT,  -- 主键
created_at      DATETIME DEFAULT CURRENT_TIMESTAMP, -- 创建时间
updated_at      DATETIME DEFAULT CURRENT_TIMESTAMP, -- 更新时间
created_by      INTEGER,                            -- 创建人ID（外键，关联users表）
is_deleted      BOOLEAN DEFAULT FALSE               -- 软删除标记
```

---

## 3. 数据类型规范

| 数据类型 | SQLite类型 | 使用场景 | 示例 |
|---------|-----------|---------|------|
| 整数 | INTEGER | ID、状态码、数量 | `id`, `status` |
| 字符串(短) | VARCHAR(255) | 用户名、标题、编号 | `username`, `title` |
| 字符串(长) | TEXT | 描述、内容 | `description` |
| 日期时间 | DATETIME | 时间戳 | `created_at` |
| 布尔 | BOOLEAN | 是/否 | `is_deleted` |
| JSON | TEXT | 数组、对象存储 | `attachments`, `tags` |
| 枚举 | VARCHAR(50) | 固定选项 | `role`, `status` |

---

## 4. 状态字段枚举值（统一定义）

### 用户状态
```python
USER_STATUS = {
    'active': '启用',
    'inactive': '禁用'
}
```

### 需求单状态（10个状态）
```python
WORK_ORDER_STATUS = {
    'pending': '待审批',
    'analyzed': '已梳理',
    'approved': '审批通过',
    'solution_submitted': '方案已提交',
    'in_review': '会审中',
    'in_progress': '实施中',
    'pending_qa': '待质量稽核',
    'pending_trial': '待试运行',
    'pending_monitor': '待监控配置',
    'online': '已上线',
    'rejected': '已驳回',  # 通用驳回状态
    'closed': '已关闭',    # 下线后
}
```

### 角色枚举（7个角色）
```python
USER_ROLE = {
    'data_consumer': '用数方',
    'requirement_manager': '需求经理',
    'operator': '运营方',
    'project_manager': '项目经理',
    'qa_manager': '质量稽核经理',
    'ops_manager': '数据运维经理',
    'team_lead': '四方组长',
    'admin': '管理员'
}
```

---

## 5. 关系设计规范

### 一对多关系
```sql
-- 示例：一个用户创建多个需求单
-- users表（主表）
-- work_orders表（从表）包含 created_by 字段关联 users.id
```

### 多对多关系
```sql
-- 示例：需求单和文档（一个需求多个文档，一个文档可能关联多个需求？不，文档只属于一个需求）
-- 实际上是：需求单 1:N 文档 attachments表
-- attachments表包含 order_id 外键
```

### 审批记录设计
```sql
-- 会审记录表 work_order_reviews
-- 字段：id, order_id, reviewer_id, reviewer_role, result, comment, created_at
-- 说明：记录谁审了什么结果
```

---

## 6. 索引规范

必须加索引的字段：
- 主键（自动有索引）
- 外键（加快关联查询）
- 经常用于搜索的字段（username, status等）
- 经常用于排序的字段（created_at）

```sql
-- 示例
CREATE INDEX idx_work_orders_status ON work_orders(status);
CREATE INDEX idx_work_orders_created_by ON work_orders(created_by);
CREATE INDEX idx_work_orders_created_at ON work_orders(created_at DESC);
```

---

## 7. 示例：users表结构（卡片015用）

```sql
CREATE TABLE users (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    username        VARCHAR(50) UNIQUE NOT NULL,    -- 登录账号
    real_name       VARCHAR(50) NOT NULL,           -- 真实姓名
    password_hash   VARCHAR(255) NOT NULL,          -- 加密后的密码
    role            VARCHAR(50) NOT NULL,           -- 角色（7选1）
    status          VARCHAR(20) DEFAULT 'active',   -- 状态：active/inactive
    last_login_at   DATETIME,                       -- 最后登录时间
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by      INTEGER,                        -- 创建人（自关联，可为空）
    is_deleted      BOOLEAN DEFAULT FALSE
);

-- 索引
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_status ON users(status);
```

---

**每次创建新表时，参考此规范，确保风格统一。**
