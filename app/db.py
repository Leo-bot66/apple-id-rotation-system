from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from .models import Account
from .security import SecretBox


SCHEMA = """
CREATE TABLE IF NOT EXISTS accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_name TEXT NOT NULL UNIQUE,
    current_credential BLOB,
    security_answer BLOB,
    totp_secret BLOB,
    imap_host TEXT,
    imap_port INTEGER NOT NULL DEFAULT 993,
    imap_mailbox TEXT NOT NULL DEFAULT 'INBOX',
    imap_username BLOB,
    imap_password BLOB,
    status TEXT NOT NULL DEFAULT 'unknown',
    last_checked_at TEXT,
    last_rotated_at TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_accounts_status ON accounts(status);
"""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class SQLiteAccountRepository:
    """SQLite metadata store with encrypted secret columns."""

    def __init__(self, path: str | Path, secret_box: SecretBox) -> None:
        self.path = Path(path)
        self.secret_box = secret_box
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.executescript(SCHEMA)

    def add_account(
        self,
        *,
        account_name: str,
        current_credential: str | None = None,
        security_answer: str | None = None,
        totp_secret: str | None = None,
        imap_host: str | None = None,
        imap_port: int = 993,
        imap_mailbox: str = "INBOX",
        imap_username: str | None = None,
        imap_password: str | None = None,
    ) -> int:
        now = utc_now()
        with self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO accounts (
                    account_name, current_credential, security_answer, totp_secret,
                    imap_host, imap_port, imap_mailbox, imap_username, imap_password,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    account_name,
                    self.secret_box.encrypt(current_credential),
                    self.secret_box.encrypt(security_answer),
                    self.secret_box.encrypt(totp_secret),
                    imap_host,
                    imap_port,
                    imap_mailbox,
                    self.secret_box.encrypt(imap_username),
                    self.secret_box.encrypt(imap_password),
                    now,
                    now,
                ),
            )
            return int(cursor.lastrowid)

    def get_account(self, account_name: str) -> Account | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM accounts WHERE account_name = ?", (account_name,)
            ).fetchone()
        return self._row_to_account(row) if row else None

    def update_status(self, account_name: str, status: str) -> None:
        now = utc_now()
        with self._connect() as connection:
            connection.execute(
                """
                UPDATE accounts
                SET status = ?, last_checked_at = ?, updated_at = ?
                WHERE account_name = ?
                """,
                (status, now, now, account_name),
            )

    def record_successful_rotation(self, account_name: str, new_credential: str) -> None:
        """Persist a credential only after the remote system accepted it."""
        now = utc_now()
        with self._connect() as connection:
            connection.execute(
                """
                UPDATE accounts
                SET current_credential = ?, last_rotated_at = ?, updated_at = ?, status = 'available'
                WHERE account_name = ?
                """,
                (self.secret_box.encrypt(new_credential), now, now, account_name),
            )

    def _row_to_account(self, row: sqlite3.Row) -> Account:
        return Account(
            id=row["id"],
            account_name=row["account_name"],
            current_credential=self.secret_box.decrypt(row["current_credential"]),
            security_answer=self.secret_box.decrypt(row["security_answer"]),
            totp_secret=self.secret_box.decrypt(row["totp_secret"]),
            imap_host=row["imap_host"],
            imap_port=row["imap_port"],
            imap_mailbox=row["imap_mailbox"],
            imap_username=self.secret_box.decrypt(row["imap_username"]),
            imap_password=self.secret_box.decrypt(row["imap_password"]),
            status=row["status"],
            last_checked_at=row["last_checked_at"],
            last_rotated_at=row["last_rotated_at"],
        )
