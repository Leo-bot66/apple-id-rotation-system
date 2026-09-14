from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Account:
    id: int
    account_name: str
    current_credential: str | None
    security_answer: str | None
    totp_secret: str | None
    imap_host: str | None
    imap_port: int
    imap_mailbox: str
    imap_username: str | None
    imap_password: str | None
    status: str
    last_checked_at: str | None
    last_rotated_at: str | None


@dataclass(frozen=True)
class RotationCandidate:
    account_name: str
    new_credential: str
