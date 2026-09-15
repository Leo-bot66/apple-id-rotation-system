# 苹果ID轮转系统（Apple ID Rotation System）

[English](README.en.md) | 简体中文

苹果ID轮转系统是一套使用 **Python、SQLite、Fernet、TOTP、只读 IMAP 与 React** 构建的开源凭据轮转框架，面向**自有或已获明确授权的 Apple ID 测试账号**。项目涵盖账号凭据加密存储、候选密码生成、双重验证辅助、邮件只读读取与安全轮转编排，并附带一个仅使用虚构数据的状态面板。

> 本项目与 Apple Inc. 无关联。请勿用于未获授权的账号；公开版本不提供验证码绕过、CAPTCHA 规避或批量第三方账号操作能力。

## 项目简介

凭据轮转（Credential Rotation）是指按照安全策略更新密码、密钥等身份凭据，并在远端系统确认修改成功后同步本地记录。本项目通过明确的适配器边界，把“本地安全管理”和“经过授权的远端操作”分开，便于开发者学习或搭建内部测试账号管理方案。

公开仓库聚焦安全基础能力，不包含 Apple 网站自动化代码。它适合用于研究 Apple ID 测试账号管理、密码轮换、TOTP 双重验证、IMAP 邮件读取、Fernet 加密和 React 状态面板等技术。

## 核心功能

- 使用 SQLite 保存账号元数据，敏感字段通过 Fernet 加密后落盘。
- 为已登记的测试账号生成高强度候选凭据。
- 在进程内生成 6 位 TOTP，不记录或持久化一次性验证码。
- 通过 TLS 以只读模式读取 IMAP 邮件，并使用 `BODY.PEEK` 避免改变已读状态。
- 通过适配器边界预留状态检查与远端轮转能力；仓库本身不实现第三方站点自动化。
- 提供 React 演示面板，所有账号和密码均为 `.example` 虚构数据。

> **验证码说明：** 本项目涉及图片验证码的部分，需要在已获授权的测试环境中配合验证码识别系统使用。作者使用的平台是“超级鹰”，这里只说明个人使用情况，不作推荐；请自行在网上搜索并评估服务商。公开版本不内置验证码识别或绕过功能。

## 工作原理

1. 从 SQLite 读取已登记测试账号的非敏感元数据。
2. 使用独立保存的 Fernet 根密钥解密必要的本地凭据。
3. 检查轮转条件并生成高强度候选密码。
4. 由使用者自行实现的授权适配器完成远端状态检查或凭据修改。
5. 只有在远端确认成功后，系统才更新本地加密记录。
6. TOTP 和邮件验证码仅在内存中短暂处理，不写入日志或数据库。

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

## 安全模型

1. 仅在你拥有或明确获准管理的测试资产上使用本项目。
2. 不要提交 `.env`、SQLite 数据库、邮箱内容、TOTP 秘钥、密码或部署清单。
3. `ROTATOR_FERNET_KEY` 是本地加密根密钥；生产环境应改用 KMS、Vault 或云 Secret Manager，并与数据库分开保存。
4. 远端系统确认修改成功后，才可调用 `record_successful_rotation` 更新本地凭据。
5. 接入真实适配器前，应完成资产授权、最小权限、审计、速率限制、并发锁、失败退避和人工审批设计。

发现安全问题时，请遵循 [SECURITY.md](SECURITY.md)，不要在公开 Issue 中提交密钥或账号数据。

## 常见问题

### 这是可以直接操作 Apple 网站的自动化工具吗？

不是。公开版本提供的是凭据存储、TOTP、只读 IMAP 和轮转编排框架，不包含 Apple 网站自动化、验证码绕过或第三方账号批量操作实现。

### 可以用于真实 Apple ID 吗？

仅可用于你本人拥有或已获得明确授权管理的测试账号。接入任何真实环境前，都应完成资产授权、最小权限、速率限制、审计和人工审批设计。

### 项目会保存一次性验证码或邮件内容吗？

不会。TOTP 在进程内生成且不持久化；IMAP 客户端以 TLS 只读方式工作，并使用 `BODY.PEEK` 避免改变邮件已读状态。使用者也不应把邮箱内容写入公开日志。

### 这套系统可以直接用于生产环境吗？

公开版本更适合作为安全框架、学习项目和内部原型。生产部署应将本地 Fernet 密钥替换为 KMS、Vault 或云 Secret Manager，并补充并发锁、失败退避、审计与健康检查。

## 路线图

- 可插拔的内部系统适配器接口
- 不包含敏感数据的审计事件
- 并发锁、失败退避与健康检查
- 面向脱敏只读视图的面板 API
- KMS/Vault 密钥提供器

## 许可证

本项目使用 [MIT License](LICENSE)。

---

<h2 align="center">✨ 写在最后 ✨</h2>

<p align="center">
  这个项目由我凭着一些并不成熟的代码能力，与 <strong>GPT-5.6</strong> 历时半个月共同打磨，<br>
  最后再由 <strong>GPT-6</strong> 完成审计后上线。
</p>

<p align="center">
  项目不含后门和套路，欢迎各位小伙伴监督。<br>
  如果你觉得项目不错，还请点亮右上角的 <strong>⭐ Star 小心心</strong> 支持一下，谢谢！
</p>

<p align="center">
  下面是本小店的特色业务。有需要的小伙伴也欢迎赞助支持，<br>
  我会持续优化这个项目。
</p>

<h3 align="center">🐝 Newbee 小铺</h3>

<p align="center">
  <a href="https://nb.tangping.icu/">
    <img src="docs/assets/newbee-store-banner.jpg" width="520" alt="Newbee 小铺个人 IP 形象：全网苹果 ID 最低价">
  </a>
</p>

<h2 align="center">
  <a href="https://nb.tangping.icu/">🌐 https://nb.tangping.icu/</a>
</h2>

| 🍎 各区苹果 ID 小铺 | 🌐 特色机场服务 |
| --- | --- |
| 一件也是批发价；小火箭 ID 批发零售 15 元，量大还可再优惠。 | **特色机场服务：**真三网优化+独家朝鲜节点，AI+国内社媒IP展示，装逼与实用两不误。 |

<h3 align="center">关注作者</h3>

<p align="center">
  欢迎关注我的 X，及时了解作者和项目的最新动向：<br><br>
  <strong><a href="https://x.com/EricLee1108">𝕏 @EricLee1108</a></strong>
</p>
