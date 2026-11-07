# 智能实验室预约系统 · Lab Agent

一个面向高校实验室的预约管理系统，包含 **学生 / 管理员** 两端 Web 界面，并接入基于 **LangGraph + RAG** 的 AI 助手。用户可以用自然语言查询实验室、设备和规章制度，并在对话中完成真实预约。

![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)
![Vue](https://img.shields.io/badge/Vue-3.5-42B883?logo=vue.js&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-1.x-1C3C3C)
![Ollama](https://img.shields.io/badge/Ollama-qwen2.5%20%7C%20qwen3--embedding-000000)

## 功能特性

### 业务功能

- **账号与权限**：JWT 登录鉴权，密码 bcrypt 加密，区分学生 / 管理员角色
- **实验室管理**：实验室增删改查、封面图上传、开放 / 关闭状态、开放时段
- **设备管理**：实验室下的设备维护，支持型号、数量、维修状态
- **预约流程**：创建预约 → 管理员审核 → 通过 / 拒绝；本人可取消待审核预约
- **冲突校验**：校验日期时间、实验室开放时段、设备维修状态，并阻止同一时段重复预约
- **超时自动取消**：后台异步任务每分钟扫描一次，自动取消已过期的待审核预约
- **个人中心**：资料修改、头像上传、修改密码；管理员可维护用户

### AI 助手（核心亮点）

- **Agent 工作流**：基于 LangGraph `StateGraph` 构建 `agent ↔ tools` 循环，模型自主决定调用哪个工具
- **真实业务工具**：
  | 工具 | 作用 |
  | --- | --- |
  | `search_lab_docs` | 检索实验室规章制度知识库 |
  | `list_open_labs` | 按关键字查询开放中的实验室 |
  | `list_lab_equipments` | 查询指定实验室的设备 |
  | `create_lab_reservation` | 校验并落库真实预约单 |
  | `get_today` | 获取服务器当前日期，用于“明天 / 后天”换算 |
- **RAG 知识库**：Chroma 持久化向量库 + Ollama 嵌入模型，文本按 800 字切块、100 字重叠
- **流式事件输出**：通过 NDJSON 逐行推送 `token / tool_call / tool_result / node` 事件，前端实时展示 Agent 的“执行过程”
- **预约确认机制**：System Prompt 约束 Agent 必须先复述实验室、日期、时段并得到用户确认，才允许调用预约工具
- **工具调用兜底**：修复部分小模型把 `tool_call` 当普通文本输出的问题，避免流程中断

## 技术栈

| 层次 | 技术 |
| --- | --- |
| 后端框架 | FastAPI、Uvicorn |
| ORM / 数据库 | SQLAlchemy 2.0、MySQL、PyMySQL |
| 鉴权 | PyJWT、OAuth2PasswordBearer、bcrypt |
| Agent | LangGraph、LangChain、Ollama（qwen2.5:7b） |
| RAG | Chroma、qwen3-embedding:4b、RecursiveCharacterTextSplitter |
| 前端 | Vue 3、Vite、Vue Router、Pinia、Element Plus、Axios |
| 前端渲染 | marked + DOMPurify（Markdown 渲染与 XSS 过滤） |

## 系统架构

```mermaid
flowchart LR
    U[浏览器] -->|Vue 3 + Element Plus| F[前端 :5173]
    F -->|/api 代理| B[FastAPI :8000]
    B --> A[业务 Service 层]
    A --> DB[(MySQL)]
    B --> AG[LangGraph Agent]
    AG -->|工具调用| T[实验室 / 设备 / 预约 Service]
    AG -->|检索| KB[(Chroma 向量库)]
    KB -->|Embedding| O[Ollama]
    AG -->|对话| O
    AG -->|NDJSON 流| F
    T --> DB
```

Agent 内部结构：

```mermaid
flowchart LR
    S((START)) --> N[agent 节点<br/>qwen2.5:7b]
    N -->|有 tool_calls| TL[tools 节点<br/>ToolNode]
    TL --> N
    N -->|无 tool_calls| E((END))
```

## 目录结构

```
lab-agent/
├── backend/
│   ├── api/               # 路由层：auth / user / lab / equipment / reservation / ai / file
│   ├── models/            # SQLAlchemy 模型：用户、实验室、设备、预约
│   ├── schemas/           # Pydantic 请求 / 响应模型
│   ├── services/          # 业务逻辑；agent_service 为 LangGraph 编排，agent_tools 为工具定义
│   ├── dependencies/      # JWT 鉴权依赖
│   ├── common/            # 统一响应体与全局异常处理
│   ├── utils/             # JWT 工具
│   ├── data/
│   │   ├── kb/            # 知识库 txt 文档
│   │   └── chroma/        # Chroma 持久化目录（运行时生成）
│   ├── uploads/           # 上传文件目录（运行时生成）
│   ├── main.py            # 应用入口、CORS、路由注册、生命周期任务
│   ├── config.py          # 环境变量与上传配置
│   ├── database.py        # 引擎、会话、ORM 基类
│   └── requirement.txt
└── frontend/
    ├── src/
    │   ├── api/           # Axios 接口封装
    │   ├── views/         # 登录、实验室、设备、预约、审核、AI 助手等页面
    │   ├── layouts/       # 后台整体布局
    │   ├── router/        # 路由与登录守卫
    │   └── utils/         # 请求封装、Token 管理
    ├── vite.config.js     # /api、/uploads 代理
    └── package.json
```

## 快速开始

### 环境要求

- Python 3.11+（开发环境使用 3.14）
- Node.js `^22.18.0 || >=24.12.0`
- MySQL 8.x
- [Ollama](https://ollama.com/)

### 1. 克隆项目

```bash
git clone <your-repo-url>
cd lab-agent
```

### 2. 准备后端

```bash
cd backend

# 创建并激活虚拟环境
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
# source .venv/bin/activate

# 安装 Web 基础依赖
pip install -r requirement.txt

# 安装 AI / Agent 依赖（requirement.txt 未包含，需单独安装）
pip install langchain langchain-ollama langchain-text-splitters langgraph chromadb rich python-multipart
```

创建数据库（表由 SQLAlchemy 在启动时自动创建）：

```sql
CREATE DATABASE lab_agent DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

在 `backend/` 下新建 `.env` 文件：

```ini
DATABASE_URL=mysql+pymysql://root:your_password@127.0.0.1:3306/lab_agent?charset=utf8mb4
JWT_SECRET_KEY=please-change-this-to-a-random-string
JWT_EXPIRE_HOURS=24
JWT_ALGORITHM=HS256
```

启动后端：

```bash
uvicorn main:app --reload --port 8000
```

- 健康检查：<http://127.0.0.1:8000/>
- 接口文档：<http://127.0.0.1:8000/docs>

> 注册接口默认创建 `student` 角色。需要管理员账号时，先正常注册，再执行：
>
> ```sql
> UPDATE users SET role = 'admin' WHERE username = 'your_username';
> ```

### 3. 准备 AI 能力

先启动 Ollama，并拉取对话模型与嵌入模型：

```bash
ollama pull qwen2.5:7b
ollama pull qwen3-embedding:4b
```

导入知识库（读取 `backend/data/kb/*.txt`，切分后写入 Chroma）：

```bash
cd backend
python services/kb_service.py
```

> 知识库文件可直接在 `backend/data/kb/` 下新增 txt，重新执行导入脚本即可。向量库数据保存在 `data/chroma/`。

### 4. 启动前端

```bash
cd frontend
npm install
npm run dev
```

打开 <http://localhost:5173>。开发环境通过 Vite 代理把 `/api`、`/uploads` 转发到 `http://127.0.0.1:8000`，接口地址也可在 `frontend/.env.development` 中调整。

## 配置说明

| 变量 | 位置 | 说明 |
| --- | --- | --- |
| `DATABASE_URL` | `backend/.env` | SQLAlchemy 数据库连接串 |
| `JWT_SECRET_KEY` | `backend/.env` | JWT 签名密钥，生产环境务必替换 |
| `JWT_EXPIRE_HOURS` | `backend/.env` | Token 有效期（小时） |
| `JWT_ALGORITHM` | `backend/.env` | JWT 签名算法，如 `HS256` |
| `VITE_API_BASE_URL` | `frontend/.env.development` | 前端请求的基础地址 |

> `.env` 已被 `.gitignore` 忽略，不要提交真实数据库密码和密钥。

## 主要接口

| 模块 | 方法与路径 | 说明 |
| --- | --- | --- |
| 认证 | `POST /api/auth/register` | 注册（默认学生） |
| 认证 | `POST /api/auth/login` | 登录，返回 JWT |
| 用户 | `GET /api/user/me` | 当前用户信息 |
| 用户 | `PUT /api/user/me` / `PUT /api/user/password` | 修改资料 / 密码 |
| 用户 | `GET /api/user/list` | 用户分页列表（管理员） |
| 实验室 | `GET /api/lab/list` | 实验室分页查询 |
| 实验室 | `POST /api/lab` / `PUT /api/lab/{id}` / `DELETE /api/lab/{id}` | 实验室增改删（管理员） |
| 设备 | `GET /api/equipment/list` | 设备分页查询 |
| 设备 | `POST /api/equipment` / `PUT /api/equipment/{id}` / `DELETE /api/equipment/{id}` | 设备增改删（管理员） |
| 预约 | `POST /api/reservation` | 创建预约 |
| 预约 | `GET /api/reservation/list` | 预约列表（学生仅本人） |
| 预约 | `PUT /api/reservation/{id}/cancel` | 取消预约 |
| 预约 | `PUT /api/reservation/{id}/audit` | 审核预约（管理员） |
| 文件 | `POST /api/files/upload` | 上传图片 / 文档，返回访问 URL |
| AI | `POST /api/ai/chat` | 非流式对话 |
| AI | `POST /api/ai/chat/stream` | 纯文本流式对话 |
| AI | `POST /api/ai/chat/events` | NDJSON 事件流（推荐前端使用） |

`/api/ai/chat/events` 输出示例：

```json
{"type":"node","name":"agent"}
{"type":"tool_call","name":"list_open_labs","args":{"keywords":"化学"}}
{"type":"tool_result","name":"list_open_labs","ok":true,"preview":"{\"total\": 1, ...}"}
{"type":"token","content":"化学实验室"}
```

## 实现要点

- **Agent 状态图**：使用 `MessagesState` 维护对话，`tools_condition` 在“继续调用工具”和“结束”之间路由；`recursion_limit=25` 以容纳预约流程的多轮工具往返。
- **事件流聚合**：`stream_mode=["messages", "updates"]` 同时获取 token 与节点更新，转换成前端易消费的事件对象。
- **安全预约**：预约工具内部复用业务层与 Pydantic 校验，Agent 无法绕过时间、开放时段、冲突检查。
- **统一响应与异常**：`Response` / `PageResponse` 封装返回；业务异常、参数校验异常、未知异常统一处理。
- **XSS 防护**：AI 回复的 Markdown 经 `marked` 解析后由 `DOMPurify` 清洗再渲染。

## 已知限制 / 后续计划

- 依赖清单 `requirement.txt` 目前只包含 Web 基础依赖，AI 相关依赖需按上文单独安装
- 预约冲突校验在应用层完成，高并发场景建议增加数据库唯一约束或锁
- 尚未接入自动化测试与容器化部署
- 大模型默认走本地 Ollama，首次响应速度取决于本机显存与模型加载状态

## 说明

本项目用于学习与实践，欢迎交流。提交 Issue 前请勿附带数据库密码、JWT 密钥等敏感信息。