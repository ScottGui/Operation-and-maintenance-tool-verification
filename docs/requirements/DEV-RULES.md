# AI开发规范（完整定制版v1.0）

> **适用范围**：公共数据服务全生命周期管理平台（P0阶段）  
> **版本**：v1.0  
> **创建日期**：2026-03-24  
> **核心原则**：文档驱动、技术栈约束、业务规则强制遵守

---

## 一、核心原则（8条）

1. **文档驱动** — 开发前必须读需求卡片，理解业务逻辑
2. **技术栈约束** — 严禁使用规定以外的技术（见第二章）
3. **业务规则强制** — 角色权限、状态流转必须按第三章实现
4. **小步快跑** — 一次只开发一张卡片，验收通过再下一张
5. **验收前置** — 没有自测报告 = 没完成
6. **禁止擅自改需求** — 有问题必须问用户
7. **数据安全** — 政务系统，安全红线不能碰（见第七章）
8. **可回退** — 小步开发，出问题能快速回退

---

## 二、技术栈约束（强制）

### 2.1 必须使用

| 层级 | 技术 | 版本 | 用途 |
|------|------|------|------|
| 前端框架 | React | 19.x | 页面渲染 |
| 前端UI库 | Ant Design | 5.x | 组件样式 |
| 构建工具 | Vite | 6.x | 打包构建 |
| 路由管理 | React Router | 7.x | 页面跳转 |
| HTTP客户端 | Axios | 1.x | 接口调用 |
| 后端框架 | FastAPI | 0.115+ | API接口 |
| ORM框架 | SQLAlchemy | 2.0+ | 数据库操作 |
| 数据库 | SQLite | 3.x | 数据存储 |
| 数据验证 | Pydantic | 2.9+ | 参数校验 |

### 2.2 禁止擅自引入（除非用户批准）

| 类型 | 禁止项 | 原因 |
|------|--------|------|
| 前端框架 | Vue、Angular、Svelte | 技术栈不统一 |
| 数据库 | MySQL、PostgreSQL、MongoDB | P0阶段SQLite足够 |
| 缓存 | Redis、Memcached | P0阶段不需要 |
| 消息队列 | RabbitMQ、Kafka | P0阶段不需要 |
| 搜索引擎 | Elasticsearch | P0阶段不需要 |
| 前端组件库 | Element UI、Vuetify | 统一用Ant Design |
| CSS框架 | Tailwind CSS、Bootstrap | 统一用Ant Design样式 |

### 2.3 代码组织规范

```
frontend/                          # 前端项目
├── src/
│   ├── pages/                     # 页面组件（每个卡片一个文件夹）
│   │   ├── Login/                 # 登录页面
│   │   ├── UserManagement/        # 用户管理（卡片015）
│   │   ├── WorkOrderCreate/       # 需求发起（卡片001）
│   │   └── ...
│   ├── components/                # 公共组件
│   ├── api/                       # API封装（按模块分文件）
│   ├── router/                    # 路由配置
│   └── utils/                     # 工具函数

backend/                           # 后端项目
├── src/
│   ├── models/                    # 数据库模型（每个实体一个文件）
│   │   ├── user.py                # 用户模型
│   │   ├── work_order.py          # 需求单模型
│   │   └── ...
│   ├── routes/                    # 路由/接口（按模块分文件）
│   │   ├── auth.py                # 登录相关
│   │   ├── users.py               # 用户管理
│   │   ├── work_orders.py         # 需求单相关
│   │   └── ...
│   ├── utils/                     # 工具函数
│   └── main.py                    # 应用入口
```

---

## 三、业务规则约束（强制）

### 3.1 7个角色权限矩阵（必须严格执行）

| 角色 | 核心权限 | 特殊权限 | 禁止事项 |
|------|---------|---------|---------|
| **用数方** | 发起需求、查看自己的需求、查看审批进度、查看历史申请记录 | 无 | 不能看别人的需求、不能审批 |
| **需求经理** | 发起需求（需上传授权函件）、查看自己的需求、认领待梳理需求、查看历史申请记录 | 查看自己的需求 | 不能看所有需求、不能审批 |
| **运营方** | 需求审批、方案会审终审（汇总四方意见） | 查看所有需求（审批需要） | 不能实施交付、不能试运行 |
| **项目经理** | 认领需求、上传交付物（3个文档） | 查看自己认领的需求 | 不能审批、不能稽核 |
| **质量稽核经理** | 稽核待稽核的需求、查看所有稽核结果汇总 | 查看稽核相关报表 | 不能发起需求、不能审批 |
| **数据运维经理** | 试运行、监控配置、查看所有需求的流转状态和明细 | 全局视图（运维视角） | 不能发起需求、不能审批 |
| **四方组长** | 参与方案会审、查看所有需求的流转状态和明细 | 独立审批权（4人并行） | 不能发起需求、不能实施 |

**权限实现要点**：
- 前端：根据角色显示/隐藏菜单和按钮
- 后端：每个接口必须校验用户角色，不能只靠前端控制
- 数据：查询时带`created_by`或`assignee_id`过滤，确保只能看自己的

### 3.2 需求单状态流转（10个状态，必须按顺序）

```
【起点】待审批（需求发起后）
   ↓ 需求经理梳理后
已梳理（上传规格说明书）
   ↓ 运营方审批通过后
审批通过（可进入方案阶段）
   ↓ 项目经理上传技术方案后
方案已提交（等待会审）
   ↓ 会审启动后
会审中（5方独立审批中）
   ↓ 5方全部通过后
实施中（已生成实施单）
   ↓ 项目经理上传3个交付物后
待质量稽核
   ↓ 稽核经理通过后
待试运行
   ↓ 运维经理试运行通过后
待监控配置
   ↓ 运维经理上传监控截图后
【终点】已上线（服务正式运行）
```

**特殊流转：驳回**
- 任何审批节点都可以驳回
- 驳回后状态回退到上一个可编辑状态
- 驳回必须填写驳回原因，通知相关人员

**状态实现要点**：
- 数据库字段：`status`，字符串枚举
- 状态变更必须记录操作日志（谁、什么时候、从什么变为什么）
- 接口必须校验当前状态是否允许目标操作（比如"已上线"不能再审批）

### 3.3 5方会审特殊规则

**参与角色**：
1. 运维组长（四方组长之一）
2. 安全组长（四方组长之一）
3. 平台组长（四方组长之一）
4. 数据组长（四方组长之一）
5. 运营方（终审角色）

**审批逻辑**：
```
四方组长审批（并行，互不影响）
   ↓ 四方全部通过后
运营方终审（查看四方意见后决定）
   ↓ 通过 → 状态变"实施中"
   ↓ 驳回 → 返回项目经理修改
```

**关键规则**：
- 四方是**独立审批**，不需要等其他人
- 任一方驳回 → **整体驳回**，其他未审批的不用再审
- 四方全部通过后 → **自动通知运营方**进行终审
- 运营方可以看到四方的审批意见汇总

**数据表设计建议**：
- 单独一张表记录会审意见：`work_order_review`
- 字段：`order_id`, `reviewer_role`, `reviewer_id`, `result`（通过/驳回）, `comment`, `review_time`

---

## 四、开发流程（5步）

| 步骤 | 时长 | 做什么 | 交付物 |
|------|------|--------|--------|
| Step 1: 读需求 | 5分钟 | 读卡片+本章DEV-RULES，理解业务规则 | 疑问清单 |
| Step 2: 做计划 | 5分钟 | 告诉用户今天做什么，等确认 | 开发计划 |
| Step 3: 开发 | 30-60分钟 | 写代码，按技术栈和业务规则实现 | 代码文件 |
| Step 4: 自测 | 10-15分钟 | 按验收标准测试，重点测权限和状态流转 | 自测报告 |
| Step 5: 交付 | 5分钟 | 展示成果，提交报告，等验收 | 交付物包 |

**总时长控制在1-2小时内**

---

## 五、代码规范（3条）

### 5.1 命名规范

| 类型 | 规则 | 示例 |
|------|------|------|
| 文件/文件夹 | 小写，单词间用连字符 | `user-management.jsx`、`work_orders.py` |
| 变量/函数 | 小写驼峰式 | `getUserList`、`createWorkOrder` |
| 组件/类 | 大写驼峰式 | `UserListPage`、`WorkOrderService` |
| 常量 | 全大写下划线 | `MAX_PAGE_SIZE = 100` |
| 数据库表 | 小写下划线 | `user`、`work_order`、`work_order_flow` |
| 数据库字段 | 小写下划线 | `created_by`、`approved_at` |

### 5.2 注释规范

每个函数/组件上面写注释：

```python
"""
需求审批
业务规则：只有运营方角色可以审批，其他角色返回403
前置条件：需求状态必须是"已梳理"
状态流转：已梳理 → 审批通过/已驳回
输入：order_id, approval_result（approve/reject）, comment
输出：更新后的需求单
作者/日期：AI / 2026-03-24
"""
def approve_work_order(order_id: int, approval_result: str, comment: str):
    pass
```

```javascript
/**
 * 用户管理页面
 * 角色权限：仅管理员可见
 * 主要功能：增删改查用户、分配7个角色之一
 * 路由：/admin/users
 * 作者/日期：AI / 2026-03-24
 */
function UserManagementPage() {
  // ...
}
```

### 5.3 错误处理规范

**后端统一返回格式**：
```python
# 成功
{
    "code": 200,
    "message": "审批成功",
    "data": {
        "order_id": 123,
        "status": "审批通过"
    }
}

# 失败（客户端错误）
{
    "code": 4001,  # 4xxx表示客户端错误
    "message": "当前状态不可审批",  # 给用户看的
    "data": {
        "current_status": "待审批",  # 当前状态
        "required_status": "已梳理"   # 需要什么状态
    }
}

# 失败（权限错误）
{
    "code": 4030,
    "message": "无权操作，仅运营方可审批",
    "data": {
        "current_role": "项目经理",
        "required_role": "运营方"
    }
}
```

**前端错误处理**：
```javascript
// 使用antd的message组件提示
try {
  await approveWorkOrder(orderId, 'approve', '同意');
  message.success('审批成功');
  // 刷新列表
  loadOrderList();
} catch (error) {
  // 显示后端返回的错误信息
  message.error(error.response?.data?.message || '操作失败，请稍后重试');
}
```

---

## 六、文档管理规则（本项目特定）

### 6.1 支持的文件类型

| 文件类型 | 用途 | 上传环节 |
|---------|------|---------|
| PDF | 需求规格说明书、技术方案、应急预案、自测报告、试运行报告、质量稽核报告 | 多个环节 |
| Word (.doc/.docx) | 自测报告、试运行报告、质量稽核报告、应急预案 | 实施交付、试运行、稽核 |
| Excel (.xls/.xlsx) | 数据交维清单 | 实施交付 |

### 6.2 文件处理规范

```python
# 后端必须做的校验
ALLOWED_EXTENSIONS = {'.pdf', '.doc', '.docx', '.xls', '.xlsx'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

def upload_file(file, order_id):
    # 1. 校验文件类型
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"不支持的文件类型：{ext}")
    
    # 2. 校验文件大小
    if len(file.content) > MAX_FILE_SIZE:
        raise ValueError(f"文件大小超过50MB限制")
    
    # 3. 安全文件名（防止路径遍历攻击）
    safe_filename = secure_filename(file.filename)
    
    # 4. 存储路径按日期+需求单号组织
    storage_path = f"uploads/{order_id}/{datetime.now().strftime('%Y%m%d')}/{safe_filename}"
    
    # 5. 保存文件
    save_file(file, storage_path)
    
    # 6. 记录到数据库
    create_attachment(order_id, safe_filename, storage_path, uploader_id)
```

### 6.3 前端上传组件

```javascript
// 使用Ant Design的Upload组件
<Upload
  accept=".pdf,.doc,.docx,.xls,.xlsx"  // 限制可选文件类型
  maxFileSize={50 * 1024 * 1024}        // 50MB
  beforeUpload={(file) => {
    // 前端预校验
    const isValidType = ['pdf', 'doc', 'docx', 'xls', 'xlsx'].includes(file.type);
    if (!isValidType) {
      message.error('只支持PDF、Word、Excel文件');
      return Upload.LIST_IGNORE;
    }
    return true;
  }}
  onChange={handleUpload}
>
  <Button icon={<UploadOutlined />}>上传文档</Button>
</Upload>
```

---

## 七、数据安全规则（政务系统强制）

### 7.1 密码安全

```python
from passlib.context import CryptContext

# 使用bcrypt加密
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 创建用户时加密密码
hashed_password = pwd_context.hash(plain_password)

# 验证密码时
is_valid = pwd_context.verify(plain_password, hashed_password)

# 禁止：
# ❌ 明文存储密码
# ❌ 使用MD5、SHA1等弱加密
# ❌ 密码传输不使用HTTPS
```

### 7.2 审计日志（必须记录）

**哪些操作必须记录**：
- 登录/登出（成功和失败都要记）
- 创建/修改/删除需求单
- 审批操作（通过/驳回）
- 上传/下载文档
- 状态变更（从X状态变为Y状态）

**日志内容**：
```python
{
    "log_id": 1,
    "user_id": 123,
    "username": "opn1",
    "real_name": "运营组-王五",
    "role": "运营方",
    "action": "审批需求单",
    "target_type": "work_order",
    "target_id": 456,
    "old_value": {"status": "已梳理"},
    "new_value": {"status": "审批通过"},
    "ip_address": "192.168.1.100",
    "user_agent": "Mozilla/5.0...",
    "created_at": "2026-03-24 15:30:00"
}
```

### 7.3 敏感信息处理

**禁止打印到日志**：
- 用户密码（明文）
- 身份证号、手机号
- 数据库连接字符串
- API密钥

**错误信息规范**：
```python
# ✅ 给用户的（安全的）
raise HTTPException(status_code=400, detail="用户名或密码错误")

# ❌ 给用户的（泄露信息的）
raise HTTPException(status_code=400, detail=f"数据库连接失败：{DB_PASSWORD}")

# ✅ 给开发者的（详细的，但只在服务端日志）
logger.error(f"数据库连接失败：{str(e)}", exc_info=True)
```

### 7.4 接口鉴权

**每个接口都必须鉴权**：
```python
from fastapi import Depends, HTTPException
from utils.auth import get_current_user

@app.post("/api/work-orders/{order_id}/approve")
def approve_order(
    order_id: int,
    approval_data: ApprovalSchema,
    current_user: User = Depends(get_current_user)  # 获取当前登录用户
):
    # 1. 检查是否登录
    if not current_user:
        raise HTTPException(status_code=401, detail="未登录")
    
    # 2. 检查角色权限
    if current_user.role != "运营方":
        raise HTTPException(status_code=403, detail="无权操作，仅运营方可审批")
    
    # 3. 执行业务逻辑
    # ...
```

---

## 八、交付物清单（必须全部提供）

完成一张卡片时，必须在对话中提供：

### 8.1 代码文件清单
```markdown
## 修改的文件

### 后端
- `backend/src/models/user.py`（新建）- 用户数据模型
- `backend/src/routes/users.py`（新建）- 用户管理接口
- `backend/src/utils/auth.py`（修改）- 增加密码加密

### 前端
- `frontend/src/pages/UserManagement/index.jsx`（新建）- 用户管理页面
- `frontend/src/pages/UserManagement/style.css`（新建）- 页面样式
- `frontend/src/api/user.js`（新建）- 用户相关API封装
- `frontend/src/router/index.jsx`（修改）- 增加用户管理路由
```

### 8.2 自测报告（按卡片验收标准逐项检查）
```markdown
## 自测报告：卡片015-用户与权限管理

### 基础功能
- [x] 页面能正常打开，显示用户列表
- [x] 搜索框能按用户名/姓名模糊搜索
- [x] 角色筛选能正常过滤
- [x] 分页功能正常

### 新增用户
- [x] 能成功创建11个测试账号（dat1、req1...）
- [x] 用户名重复时提示"用户名已存在"
- [x] 必填项未填时有红框提示

### 权限验证
- [x] 禁用后的账号登录提示"账号已禁用"
- [x] 用创建的账号能正常登录

### 边界测试
- [x] 用户名4位、20位边界值测试通过
- [x] 密码6位、20位边界值测试通过

**结论：✅ 自测通过，可交付验收**
```

### 8.3 更新记录
```markdown
## 更新CHANGELOG.md

### v0.2.0 - 用户管理功能
**日期**：2026-03-24

#### 新增
- 实现用户与权限管理功能（卡片015）
- 支持创建11个测试账号
- 实现角色差异化权限控制

#### 技术细节
- 后端：使用bcrypt加密存储密码
- 前端：使用Ant Design的Form、Table、Modal组件
- 数据库：新增user表，包含username、real_name、role、status字段

#### 测试账号
| 用户名 | 角色 | 用途 |
|--------|------|------|
| dat1 | 用数方 | 测试需求发起 |
| req1 | 需求经理 | 测试需求梳理 |
| ... | ... | ... |
```

---

## 九、紧急情况处理

### 9.1 如果改坏了系统

```bash
# Step 1: 立即停，告知用户"正在修复"

# Step 2: 查看改了哪些文件
git status

# Step 3: 选择修复方案
# 方案A：回退单个文件（推荐）
git checkout -- backend/src/routes/users.py

# 方案B：回退到上次提交（慎重）
git reset --hard HEAD~1

# Step 4: 记录到CHANGELOG.md
```

### 9.2 如果需求理解错了

立即停止开发，告诉用户：
> "我发现对需求的理解和卡片描述有出入，请确认：
> 卡片说'运营方可以审批'，我理解是只有运营方能点审批按钮，对吗？
> 但我在实现时发现，项目经理也想审批，这个需求需要调整吗？"

**等用户确认后再继续，不要自己猜。**

---

## 十、快速参考

### 常用命令
```bash
# 启动开发环境
cd frontend && npm run dev          # 前端 http://localhost:5173
cd backend && python -m backend.src.main  # 后端 http://localhost:8000

# 查看API文档（启动后端后）
http://localhost:8000/docs

# 数据库重置（谨慎）
rm app.db && python -c "from backend.src.models import create_tables; create_tables()"

# 初始化测试数据
python -c "from backend.src.utils.init_data import init_test_data; init_test_data()"
```

### 文件定位速查
| 要找什么 | 去哪里 |
|---------|--------|
| 需求卡片 | `docs/requirements/cards/` |
| 开发路线图 | `docs/requirements/P0-ROADMAP.md` |
| 本规范 | `docs/requirements/DEV-RULES.md` |
| 前端页面 | `frontend/src/pages/` |
| 后端接口 | `backend/src/routes/` |
| 数据库模型 | `backend/src/models/` |
| 测试账号 | 卡片015的"测试数据"章节 |

### 业务规则速查
| 规则 | 内容 |
|------|------|
| 7个角色 | 用数方、需求经理、运营方、项目经理、质量稽核经理、数据运维经理、四方组长 |
| 10个状态 | 待审批→已梳理→审批通过→方案已提交→会审中→实施中→待质量稽核→待试运行→待监控配置→已上线 |
| 5方会审 | 4个组长并行审批，全部通过后运营方终审 |
| 文档类型 | PDF（规格书、方案）、Word（报告）、Excel（清单） |

---

**每次开发前，先读此规范，再读需求卡片，然后开始。**
