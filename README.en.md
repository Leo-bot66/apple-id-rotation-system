# Apple ID Rotation System

English | [简体中文](README.md)

Apple ID Rotation System is a credential-rotation framework for **test accounts you own or are explicitly authorized to manage**. It includes encrypted storage, TOTP generation, read-only IMAP access, orchestration boundaries, and a demo dashboard backed only by fictional data.

> This project is not affiliated with Apple Inc. Do not use it with unauthorized accounts. The public edition does not implement verification-code bypass, CAPTCHA evasion, or bulk third-party account operations.

## Features

- SQLite metadata storage with Fernet-encrypted secret columns.
- High-entropy credential candidates for registered test accounts.
- In-memory six-digit TOTP generation without logging or persistence.
- TLS-only, read-only IMAP access using `BODY.PEEK`.
- Explicit adapter boundaries for status checks and remote rotation; no third-party site automation is included.
- A React dashboard populated exclusively with fictional `.example` data.

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

## License

[MIT](LICENSE)
