# Apple ID Rotation System — Open-Source Credential Rotation Framework

English | [简体中文](README.md)

Apple ID Rotation System is an open-source credential-rotation framework built with **Python, SQLite, Fernet, TOTP, read-only IMAP, and React**. It is designed for **Apple ID test accounts you own or are explicitly authorized to manage** and includes encrypted credential storage, secure password candidate generation, two-factor authentication helpers, rotation orchestration boundaries, and a sanitized dashboard backed only by fictional data.

> This project is not affiliated with Apple Inc. Do not use it with unauthorized accounts. The public edition does not implement verification-code bypass, CAPTCHA evasion, or bulk third-party account operations.

## Overview

Credential rotation is the controlled process of replacing passwords, keys, or other authentication material and synchronizing local records only after the remote change has been confirmed. This project separates local credential management from authorized remote operations through an explicit adapter boundary.

The public repository focuses on reusable security foundations rather than Apple website automation. It is useful for studying test-account management, password rotation, TOTP-based two-factor authentication, read-only IMAP access, Fernet encryption, SQLite storage, and React dashboards.

## Features

- SQLite metadata storage with Fernet-encrypted secret columns.
- High-entropy credential candidates for registered test accounts.
- In-memory six-digit TOTP generation without logging or persistence.
- TLS-only, read-only IMAP access using `BODY.PEEK`.
- Explicit adapter boundaries for status checks and remote rotation; no third-party site automation is included.
- A React dashboard populated exclusively with fictional `.example` data.

> **CAPTCHA note:** Any image-CAPTCHA workflow added for an authorized test environment requires a separate recognition provider. The author uses Chaojiying, which is mentioned only as personal implementation context and is not an endorsement. Please research and evaluate providers independently. No CAPTCHA recognition or bypass integration is included in this public repository.

## How it works

1. Read non-sensitive metadata for registered test accounts from SQLite.
2. Decrypt required local credentials with a separately stored Fernet root key.
3. Evaluate rotation conditions and generate a high-entropy password candidate.
4. Delegate remote status checks or changes to an adapter implemented for an authorized environment.
5. Update the encrypted local record only after the remote system confirms success.
6. Keep TOTP values and verification messages ephemeral rather than logging or persisting them.

## Quick start

Python 3.11 or 3.12 is recommended.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
Copy-Item .env.example .env
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Add the generated value to `.env` as `ROTATOR_FERNET_KEY`, then run:

```powershell
python -m pytest -q
python -m app
```

The default database is `./data/rotator.sqlite3`. Both the database and `.env` are excluded from Git.

## Demo dashboard

Node.js 20 or newer is required.

```powershell
Set-Location dashboard
npm ci
npm run dev
```

The dashboard does not connect to the Python package or any external account system. It is a sanitized UI demonstration only.

## Featured navigation

[Newbee International Navigation](https://nb.tangping.icu/) — official entry points and frequently used tools.

## Security boundaries

- Use this project only with assets you own or are explicitly authorized to manage.
- Never commit credentials, mailbox contents, TOTP seeds, databases, or deployment inventories.
- Replace local Fernet storage with KMS, Vault, or a cloud secret manager in production.
- Persist a new credential only after the remote system confirms the change.
- Complete authorization, least-privilege, audit, rate-limit, locking, backoff, and human-approval design before adding a real adapter.

See [SECURITY.md](SECURITY.md) for responsible reporting and [CONTRIBUTING.md](CONTRIBUTING.md) for development instructions.

## Frequently asked questions

### Does this repository automate the Apple website?

No. The public edition provides encrypted storage, TOTP, read-only IMAP, and rotation orchestration boundaries. It does not include Apple website automation, CAPTCHA bypass, or bulk third-party account operations.

### Can it manage real Apple IDs?

Use it only with accounts you own or are explicitly authorized to manage. Before connecting any real environment, implement authorization controls, least privilege, rate limits, audit events, locking, backoff, and human approval.

### Does it store one-time codes or mailbox contents?

No. TOTP values are generated in memory and are not persisted. The IMAP client uses TLS, read-only access, and `BODY.PEEK` to avoid changing message read state. Mailbox contents should never be copied into public logs.

### Is it production-ready?

The public edition is best treated as a security framework, learning project, or internal prototype. Production deployments should replace local key storage with KMS, Vault, or a cloud secret manager and add locking, backoff, audit, and health checks.

## License

[MIT](LICENSE)
