# 贡献指南

感谢你愿意改进这个项目。以下约定用于让改动更容易被理解和合并。

## 开始之前

先按 [README](README.md) 的「快速开始」把前后端跑起来，确认本地环境可用。涉及数据库结构的改动，请同时更新 `toutiao_backend/database.sql`，并在 PR 描述里说明升级方式。

## 分支与提交

- 从 `main` 切出分支，命名用 `feat/xxx`、`fix/xxx`、`docs/xxx`、`refactor/xxx`。
- 提交信息采用 Conventional Commits 的简短形式，例如 `fix: 收藏列表分页缺少 hasMore`。
- 一个提交只做一件事，避免把格式化与功能改动混在一起。
- 提交信息用中文或英文均可，保持同一个 PR 内一致。

## 代码风格

### 后端

- 遵循 PEP 8，4 空格缩进。
- 命名：模块与函数 `snake_case`，类 `PascalCase`，常量全大写。
- 分层职责保持清晰：`routers/` 负责参数校验与响应组装，`crud/` 负责数据库查询，`modules/` 是 SQLAlchemy ORM 模型，`schemas/` 是 Pydantic 请求/响应模型。
- 新增接口需要登录时，加上 `user: User = Depends(get_current_user)`。
- 数据库会话统一用 `Depends(get_db)`，不要在路由里自行创建 Session。
- 响应保持 `{code, message, data}` 结构，成功响应优先复用 `utils.response.success_response`。

### 前端

- 2 空格缩进，单文件组件按 `<template>`、`<script setup>`、`<style scoped>` 顺序书写。
- 组合式 API 统一使用 `<script setup>`。
- 组件文件用 `PascalCase`，页面放在 `src/views/`，可复用组件放在 `src/components/`。
- 全局状态放 Pinia，接口请求集中在 `src/store/modules/`，页面组件不直接写 axios 调用。
- 新增文案时同步补充 `src/i18n/locales/zh-CN.js` 与 `en-US.js`。

## 提交前自检

```bash
# 前端构建通过
cd news-headline-frontend && npm run build

# 后端可以正常导入（不要求数据库已启动）
cd toutiao_backend && python -c "import main; print(main.app.title)"

# 确认没有把密钥或本地产物带进提交
git grep -nE 'sk-[A-Za-z0-9]{16,}' -- . ':(exclude)package-lock.json' || echo "no api key"
git ls-files | grep -E '(^|/)\.env$' && echo "发现 .env 被跟踪，请移出索引" || true
git status --short
```

不要提交 `.env`、`node_modules/`、`dist/`、`__pycache__/`、`.idea/`、`.DS_Store`、`dump.rdb`。这些已在 `.gitignore` 中忽略，如果发现被跟踪，用 `git rm --cached <path>` 移出索引。

## 提交 Pull Request

PR 描述里写清三件事：

- 改了什么，对应哪个 Issue（如果有）。
- 为什么这样改，有没有考虑过其他方案。
- 如何验证，包括执行的命令与关键输出。

界面相关改动请附截图或录屏；接口相关改动请附请求与响应示例。修改或新增接口时，同步更新 README 的「API 一览」与「缓存策略」。

## 提交 Issue

请提供复现步骤、期望结果、实际结果，以及以下环境信息：

- 操作系统与版本
- Python / Node 版本
- MySQL / Redis 版本
- 后端或前端的完整报错日志

涉及安全问题时不要公开提 Issue，请通过 GitHub 的私密漏洞报告渠道联系维护者。

## 依赖升级

后端依赖锁定在 `toutiao_backend/requirements.txt`，前端锁定在 `package-lock.json`。升级流程：

```bash
cd toutiao_backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -c "import main"
```

确认 README 的启动步骤仍然可用后再提交版本号变更。`bcrypt` 必须保持在 `4.0.1`，升级会导致 passlib 读取版本失败。
