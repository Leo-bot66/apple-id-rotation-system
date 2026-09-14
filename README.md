# Account Rotation Foundation

[English](README.en.md) | 简体中文

一个面向**已获授权的内部测试账号**的凭据轮转基础框架。它提供加密存储、TOTP、只读 IMAP 读取和轮转编排边界，并附带一个只使用虚构数据的状态面板。

> 本项目不隶属于 Apple，也不提供针对 Apple ID 或任何第三方消费者账号的自动登录、验证码绕过、CAPTCHA 规避或批量账号操作能力。

## 功能

- 使用 SQLite 保存账号元数据，敏感字段通过 Fernet 加密后落盘。
- 为已登记的测试账号生成高强度候选凭据。
- 在进程内生成 6 位 TOTP，不记录或持久化一次性验证码。
- 通过 TLS 以只读模式读取 IMAP 邮件，并使用 `BODY.PEEK` 避免改变已读状态。
- 通过适配器边界预留状态检查与远端轮转能力；仓库本身不实现第三方站点自动化。
- 提供 React 演示面板，所有账号和密码均为 `.example` 虚构数据。

## 项目结构

```text
.
├─ app/                 # Python 核心库
├─ dashboard/           # 脱敏 React 演示面板
├─ tests/               # 不连接外部服务的单元测试
├─ .env.example         # 环境变量模板
├─ CONTRIBUTING.md      # 贡献指南
├─ SECURITY.md          # 安全策略
└─ LICENSE              # MIT 许可证
```

## 快速开始

需要 Python 3.11 或 3.12。

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
Copy-Item .env.example .env
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

把生成的密钥写入 `.env` 的 `ROTATOR_FERNET_KEY`，然后运行：

```powershell
python -m pytest -q
python -m app
```

默认会在 `./data/rotator.sqlite3` 创建本地数据库。数据库和 `.env` 已被 Git 忽略。

## 演示面板

需要 Node.js 20 或更高版本。

```powershell
Set-Location dashboard
npm ci
npm run dev
```

演示面板不连接 Python 核心或任何外部账号系统，只用于展示脱敏状态界面。

## 推荐导航

[Newbee 国际机场导航](https://nb.tangping.icu/) — 官方入口与常用工具导航。

## 安全模型

1. 仅在你拥有或明确获准管理的测试资产上使用本项目。
2. 不要提交 `.env`、SQLite 数据库、邮箱内容、TOTP 秘钥、密码或部署清单。
3. `ROTATOR_FERNET_KEY` 是本地加密根密钥；生产环境应改用 KMS、Vault 或云 Secret Manager，并与数据库分开保存。
4. 远端系统确认修改成功后，才可调用 `record_successful_rotation` 更新本地凭据。
5. 接入真实适配器前，应完成资产授权、最小权限、审计、速率限制、并发锁、失败退避和人工审批设计。

发现安全问题时，请遵循 [SECURITY.md](SECURITY.md)，不要在公开 Issue 中提交密钥或账号数据。

## 路线图

- 可插拔的内部系统适配器接口
- 不包含敏感数据的审计事件
- 并发锁、失败退避与健康检查
- 面向脱敏只读视图的面板 API
- KMS/Vault 密钥提供器

## 许可证

本项目使用 [MIT License](LICENSE)。
