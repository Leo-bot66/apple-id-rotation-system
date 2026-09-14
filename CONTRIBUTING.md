# Contributing

Thanks for helping improve Apple ID Rotation System.

## Ground rules

- Only contribute integrations for systems you own or are explicitly authorized to test.
- Do not submit live credentials, TOTP seeds, mailbox contents, personal data, server addresses, deployment inventories, or production logs.
- Keep service-specific automation behind a small, typed adapter boundary.
- Never log decrypted secrets or one-time codes.
- Add tests that run without contacting real external services.

## Development setup

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
python -m pytest -q
```

For the demo dashboard:

```powershell
Set-Location dashboard
npm ci
npm run build
npm run test:sites
```

## Pull requests

Keep changes focused, explain the security implications, and document new configuration. A pull request should pass the Python tests and dashboard build checks before review.
