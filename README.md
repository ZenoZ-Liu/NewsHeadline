# NewsHeadline · 新闻头条

![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)
![Vue](https://img.shields.io/badge/Vue-3.5-42B883?logo=vue.js&logoColor=white)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?logo=fastapi&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

一个移动端新闻资讯应用，前端为 Vue 3 + Vant，后端为 FastAPI + SQLAlchemy 异步 ORM，搭配 MySQL 存储与 Redis 缓存。项目采用前后端分离结构，实现了新闻浏览、用户认证、收藏、浏览历史、主题与语言切换，以及接入通义千问的流式 AI 问答。

仓库为单仓结构：`news-headline-frontend/` 与 `toutiao_backend/` 各自独立安装依赖，分别启动。

## 功能特性

### 用户端

| 模块 | 说明 |
| --- | --- |
| 新闻浏览 | 8 个分类横向切换，列表下拉刷新、上拉分页加载，单页 10 条 |
| 新闻详情 | 封面、作者、发布时间、阅读量，进入详情自动浏览量 +1，底部展示同分类相关推荐 |
| 收藏 | 详情页一键收藏/取消，收藏状态实时校验，收藏列表分页展示，支持单条取消与一键清空 |
| 浏览历史 | 浏览详情自动记录，重复浏览更新时间而不重复插入，支持单条删除与清空 |
| 账号 | 注册、登录、退出，Token 本地持久化，个人资料编辑与修改密码 |
| 外观 | 浅色、深色、蓝色、绿色四套主题，选择结果写入 localStorage |
| 国际化 | 简体中文 / English 双语切换，基于 vue-i18n |
| AI 问答 | 独立的对话页面，对接 DashScope OpenAI 兼容接口，SSE 流式输出，Markdown 渲染并经 DOMPurify 清洗 |

### 服务端

| 能力 | 说明 |
| --- | --- |
| 异步数据访问 | SQLAlchemy 2.x async + aiomysql，全链路 `async/await` |
| 统一响应 | 成功响应固定为 `{code, message, data}`，收藏与历史分页附带 `total` 与 `hasMore` |
| 认证 | 登录签发 UUID4 Token，存 `user_token` 表，有效期 7 天，重新登录会覆盖旧 Token |
| 缓存 | Redis 缓存分类、列表、详情与相关推荐，缓存异常时自动回源数据库 |
| 异常处理 | 依次捕获 `HTTPException`、`IntegrityError`、`SQLAlchemyError` 与兜底 `Exception`，按约束名给出中文提示 |
| 接口文档 | FastAPI 自动生成 Swagger UI 与 ReDoc |

## 技术栈

| 层次 | 技术 |
| --- | --- |
| 前端 | Vue 3.5、Vite 7、Vant 4、Vue Router 4、Pinia 3（persistedstate）、vue-i18n 9、Axios、marked、DOMPurify |
| 后端 | Python 3.13、FastAPI、SQLAlchemy 2.1（async）、aiomysql、Pydantic v2、passlib + bcrypt、redis.asyncio、Uvicorn |
| 存储 | MySQL 8（`news_app` 库）、Redis 6+ |
| AI | 阿里云百炼 DashScope，模型默认 `qwen3-max-preview` |

## 架构

```
┌─────────────────────────────┐
│ 浏览器（移动端视口 / 750px） │
│ Vue 3 + Vant + Pinia        │
└──────────────┬──────────────┘
               │ HTTP / JSON（Axios）
               ▼
┌─────────────────────────────┐       ┌──────────────────────┐
│ FastAPI  127.0.0.1:8000     │──────▶│ MySQL 8  news_app    │
│ routers → crud → ORM 模型    │       └──────────────────────┘
│ 统一响应 / 四层异常处理       │       ┌──────────────────────┐
│                             │──────▶│ Redis  缓存（可降级） │
└──────────────┬──────────────┘       └──────────────────────┘
               │ AI 问答由前端直连
               ▼
  DashScope OpenAI 兼容接口（SSE 流式）
```

## 目录结构

```
NewsHeadline_Project/
├── README.md
├── LICENSE
├── CONTRIBUTING.md
├── CHANGELOG.md
├── .gitignore
│
├── news-headline-frontend/          # 前端
│   ├── .env.example                 # 前端环境变量模板
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── public/
│   └── src/
│       ├── main.js                  # 应用入口，注册 Vant 组件、路由、Pinia、i18n
│       ├── App.vue
│       ├── style.css
│       ├── assets/
│       ├── components/              # NewsItem 新闻卡片、TabBar 底部导航
│       ├── config/api.js            # 后端地址与 AI 接口配置（读 VITE_ 变量）
│       ├── i18n/                    # index.js、locales/zh-CN.js、locales/en-US.js
│       ├── router/index.js          # 11 个页面路由
│       ├── store/                   # user / theme / language
│       │   └── modules/             # news / favorite / history
│       └── views/                   # Home、Category、NewsDetail、Favorite、History、
│                                    # Login、Register、My、Profile、Settings、AIChat
│
└── toutiao_backend/                 # 后端
    ├── .env.example                 # 后端环境变量模板
    ├── main.py                      # FastAPI 实例、CORS、路由与异常处理注册
    ├── requirements.txt
    ├── database.sql                 # 建库建表 + 演示数据
    ├── config/
    │   ├── __init__.py              # 加载 .env
    │   ├── db_conf.py               # 异步引擎、会话工厂、get_db 依赖
    │   └── redis.py                 # Redis 客户端与缓存读写封装
    ├── modules/                     # ORM 模型：news、users、favorite、history
    ├── schemas/                     # Pydantic 请求/响应模型
    ├── routers/                     # 接口层：news、users、favorite、history
    ├── crud/                        # 数据访问层，news_cache.py 负责缓存键与 TTL
    └── utils/                       # auth、security、response、exception(_handlers)
```

## 快速开始

### 环境要求

| 依赖 | 版本 |
| --- | --- |
| Python | 3.11 及以上（开发环境 3.13） |
| Node.js | 20.19 及以上（Vite 7 要求） |
| MySQL | 8.0 及以上 |
| Redis | 6.0 及以上（可选，未启动时服务仍可运行，只是缓存失效） |

### 1. 克隆仓库并初始化数据库

```bash
git clone https://github.com/ZenoZ-Liu/NewsHeadline.git
cd NewsHeadline
```

`database.sql` 已包含 `CREATE DATABASE IF NOT EXISTS news_app` 与 `USE news_app`，直接导入即可：

```bash
mysql -u root -p < toutiao_backend/database.sql
```

导入后包含 8 个新闻分类、403 条演示新闻与 1 个测试账号。

### 2. 启动后端

```bash
cd toutiao_backend

python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

pip install -r requirements.txt
cp .env.example .env               # 按本机 MySQL / Redis 配置修改
uvicorn main:app --reload --port 8000
```

> 必须在 `toutiao_backend/` 目录下启动。`main.py` 使用 `from routers import ...` 形式的绝对导入，从仓库根目录执行 `uvicorn toutiao_backend.main:app` 会报 `ModuleNotFoundError: No module named 'routers'`。

启动后可访问：

- Swagger UI：<http://127.0.0.1:8000/docs>
- ReDoc：<http://127.0.0.1:8000/redoc>

### 3. 启动前端

```bash
cd news-headline-frontend

npm install
cp .env.example .env
npm run dev
```

浏览器打开 <http://localhost:5173>。前端默认请求 `http://127.0.0.1:8000`，如需修改，改 `VITE_API_BASE_URL` 后**重启 dev server**（Vite 不会热更新 `.env`）。

生产构建：

```bash
npm run build
npm run preview
```

## 配置说明

两个 `.env` 文件分别位于前端与后端目录，均不入库，仓库里只提交对应的 `.env.example`。

### 后端 `toutiao_backend/.env`

| 变量 | 默认值 | 说明 |
| --- | --- | --- |
| `MYSQL_HOST` | `127.0.0.1` | 数据库地址 |
| `MYSQL_PORT` | `3306` | 数据库端口 |
| `MYSQL_USER` | `root` | 数据库用户名 |
| `MYSQL_PASSWORD` | 空 | 数据库密码，含 `@ : / %` 等字符无需手工转义 |
| `MYSQL_DATABASE` | `news_app` | 数据库名 |
| `MYSQL_CHARSET` | `utf8mb4` | 连接字符集 |
| `DATABASE_URL` | 空 | 填写后覆盖以上 `MYSQL_*`，适合容器或云数据库 |
| `DB_POOL_SIZE` | `10` | 连接池大小 |
| `DB_MAX_OVERFLOW` | `20` | 连接池溢出上限 |
| `SQL_ECHO` | `false` | 设为 `true` 打印 SQL，调试用 |
| `REDIS_HOST` | `127.0.0.1` | Redis 地址 |
| `REDIS_PORT` | `6379` | Redis 端口 |
| `REDIS_DB` | `0` | Redis 库号 |
| `REDIS_PASSWORD` | 空 | Redis 密码，无密码留空 |

### 前端 `news-headline-frontend/.env`

| 变量 | 默认值 | 说明 |
| --- | --- | --- |
| `VITE_API_BASE_URL` | `http://127.0.0.1:8000` | 后端地址，末尾斜杠会被自动去掉 |
| `VITE_AI_ENDPOINT` | DashScope 兼容接口 | AI 对话接口地址 |
| `VITE_AI_MODEL` | `qwen3-max-preview` | 模型名称 |
| `VITE_AI_API_KEY` | 空 | DashScope API Key，留空则 AI 页面提示未配置 |

> `VITE_` 前缀的变量会在构建时以明文内联进前端产物，等同于公开信息。这里填写 API Key 只适合本地调试，公开部署请改为由后端代理调用。

## 接口示例

### 注册并登录

```bash
# 注册（用户名重复时返回 code=400）
curl -X POST http://127.0.0.1:8000/api/user/register \
  -H "Content-Type: application/json" \
  -d '{"username":"demo","password":"demo123456"}'

# 登录
curl -X POST http://127.0.0.1:8000/api/user/login \
  -H "Content-Type: application/json" \
  -d '{"username":"demo","password":"demo123456"}'
```

登录成功返回：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "token": "6f1d0c2e-8a4b-4f6d-9c1e-2b7a5d3e9f10",
    "userInfo": {
      "nickname": null,
      "avatar": "https://fastly.jsdelivr.net/npm/@vant/assets/cat.jpeg",
      "gender": "unknown",
      "bio": "这个人很懒，什么都没留下",
      "id": 2,
      "username": "demo"
    }
  }
}
```

### 携带 Token 访问

需要登录的接口在请求头中带上 Token。后端同时兼容 `Bearer <token>` 与直接传 `<token>`：

```bash
TOKEN="6f1d0c2e-8a4b-4f6d-9c1e-2b7a5d3e9f10"

# 新闻列表（公开接口）
curl "http://127.0.0.1:8000/api/news/list?categoryId=1&page=1&pageSize=10"

# 新闻详情（浏览量 +1）
curl "http://127.0.0.1:8000/api/news/detail?id=1"

# 收藏
curl -X POST http://127.0.0.1:8000/api/favorite/add \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"newsId":1}'

# 收藏列表
curl "http://127.0.0.1:8000/api/favorite/list?page=1&pageSize=10" \
  -H "Authorization: Bearer $TOKEN"
```

新闻列表响应：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "list": [
      {
        "id": 1,
        "title": "新闻标题",
        "description": "新闻简介",
        "image": "https://picsum.photos/id/100/200/200",
        "author": "新华社",
        "publishTime": "2024-01-01T08:00:00",
        "categoryId": 1,
        "views": 12500
      }
    ],
    "total": 50
  }
}
```

分页接口的 `data` 统一为 `{ list, total, hasMore }`（新闻列表只返回 `list` 与 `total`，前端按返回条数判断是否还有下一页）。

## API 一览

### 新闻 `/api/news`

| 方法 | 路径 | 说明 | 登录 |
| --- | --- | --- | :---: |
| GET | `/api/news/categories` | 获取新闻分类 | 否 |
| GET | `/api/news/list?categoryId=&page=&pageSize=` | 分类下的新闻列表（分页） | 否 |
| GET | `/api/news/detail?id=` | 新闻详情，浏览量 +1，附相关推荐 | 否 |

### 用户 `/api/user`

| 方法 | 路径 | 说明 | 登录 |
| --- | --- | --- | :---: |
| POST | `/api/user/register` | 注册，成功后直接返回 Token | 否 |
| POST | `/api/user/login` | 登录 | 否 |
| GET | `/api/user/info` | 当前用户信息 | 是 |
| PUT | `/api/user/update` | 更新昵称、头像、性别、简介、手机号 | 是 |
| PUT | `/api/user/password` | 修改密码 | 是 |

### 收藏 `/api/favorite`

| 方法 | 路径 | 说明 | 登录 |
| --- | --- | --- | :---: |
| GET | `/api/favorite/check?newsId=` | 检查是否已收藏 | 是 |
| POST | `/api/favorite/add` | 添加收藏（重复收藏幂等返回） | 是 |
| DELETE | `/api/favorite/remove?newsId=` | 取消收藏 | 是 |
| GET | `/api/favorite/list?page=&pageSize=` | 收藏列表（分页） | 是 |
| DELETE | `/api/favorite/clear` | 清空收藏 | 是 |

### 浏览历史 `/api/history`

| 方法 | 路径 | 说明 | 登录 |
| --- | --- | --- | :---: |
| POST | `/api/history/add` | 记录浏览（已存在则更新时间） | 是 |
| GET | `/api/history/list?page=&pageSize=` | 历史列表（分页） | 是 |
| DELETE | `/api/history/delete/{news_id}` | 删除单条历史 | 是 |
| DELETE | `/api/history/clear` | 清空历史 | 是 |

## 缓存策略

Redis 不可用时，`config/redis.py` 会捕获异常并返回 `None`，接口继续查数据库，不影响功能。

| 数据 | Key 格式 | TTL |
| --- | --- | --- |
| 新闻分类 | `news:categories` | 2 小时 |
| 新闻列表 | `news_list:{categoryId}:{page}:{pageSize}` | 30 分钟 |
| 新闻详情 | `news_detail:{newsId}` | 30 分钟 |
| 相关推荐 | `related_news:{newsId}:{categoryId}` | 30 分钟 |

## 数据库表

| 表名 | 说明 |
| --- | --- |
| `user` | 用户信息，密码以 bcrypt 哈希存储 |
| `user_token` | 登录令牌，UUID，7 天过期 |
| `news_category` | 新闻分类 |
| `news` | 新闻内容、封面、作者、浏览量、发布时间 |
| `favorite` | 收藏记录，`(user_id, news_id)` 唯一 |
| `history` | 浏览历史，重复浏览更新时间 |
| `related_news` | 预留表，当前相关推荐按同分类 + 浏览量实时查询 |
| `ai_chat` | 预留表，当前 AI 对话不落库 |

> `database.sql` 中的新闻内容与图片链接均为演示数据，仅用于功能测试，不代表真实报道；图片来自 picsum.photos，离线环境会显示裂图。脚本中的测试账号仅供本地调试，请勿用于生产环境。

## 常见问题

**启动后端报 `ModuleNotFoundError: No module named 'routers'`**
当前工作目录不对。先 `cd toutiao_backend` 再执行 `uvicorn main:app --reload`。

**报 `Access denied for user 'root'@'localhost'`**
`toutiao_backend/.env` 里的 `MYSQL_USER` / `MYSQL_PASSWORD` 与本机不一致，或没有从 `.env.example` 复制出 `.env`。

**Redis 没启动，接口还能用吗**
可以。缓存读写失败只会打印日志并回源数据库，功能不受影响，但响应会变慢。

**修改 `.env` 后没有生效**
后端 `--reload` 只监听代码文件，前端 Vite 也不热更新环境变量，改完需要重启进程。

**登录后刷新页面掉登录态**
检查浏览器是否禁用了 localStorage。用户、主题、语言状态都依赖它持久化。

**出现 `(trapped) error reading bcrypt version` 警告**
`bcrypt` 版本高于 4.0.1 导致 passlib 读取版本失败。按 `requirements.txt` 锁定 `bcrypt==4.0.1` 即可，不要单独升级它。

**前端请求被 CORS 拦截**
后端默认允许所有来源，通常不会触发。若自行收窄了 `main.py` 中的 `allow_origins`，需把前端地址加入白名单。

## 已知限制与安全说明

- 项目没有自动化测试、CI 与容器编排，属于学习与演示性质，不建议直接用于生产。
- AI 问答由前端直连 DashScope，API Key 会进入浏览器；正式部署应增加后端代理接口，把 Key 留在服务端。
- `main.py` 的 CORS 配置为 `allow_origins=["*"]`，生产环境应改为具体域名。
- `utils/exception.py` 中 `DEBUG_MODE = True` 会在错误响应里返回堆栈信息，上线前应改为 `False`。
- 密码哈希使用 bcrypt，仅前 72 字节有效；接口层目前只校验了最小长度 6 位。
- 令牌为不透明 UUID，服务端不校验请求来源，生产环境建议配合 HTTPS 与限流使用。

## 贡献

欢迎提交 Issue 与 Pull Request。提交前请阅读 [CONTRIBUTING.md](CONTRIBUTING.md)，版本变更见 [CHANGELOG.md](CHANGELOG.md)。

## 许可证

本项目基于 [MIT License](LICENSE) 开源，Copyright (c) 2026 ZenoZ-Liu。

## 联系方式

- GitHub：[@ZenoZ-Liu](https://github.com/ZenoZ-Liu)
- 问题反馈：[Issues](https://github.com/ZenoZ-Liu/NewsHeadline/issues)
