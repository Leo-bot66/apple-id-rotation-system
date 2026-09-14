from __future__ import annotations

import secrets
import string
from collections.abc import Callable
from datetime import datetime

import pyotp

from .db import SQLiteAccountRepository
from .imap_client import IMAPConfig, IMAPReader, MailMessage
from .models import Account, RotationCandidate


class AccountRotator:
    """Orchestrate safe, auditable account maintenance primitives.

    Remote status checks and password changes are intentionally represented by
    adapter boundaries. They must be implemented only for explicitly owned
    internal test assets and should return a typed result plus an audit event.
    """

    def __init__(
        self,
        repository: SQLiteAccountRepository,
        *,
        imap_reader_factory: Callable[[IMAPConfig], IMAPReader] = IMAPReader,
        imap_timeout_seconds: float = 20.0,
        imap_ca_file: str | None = None,
    ) -> None:
        self.repository = repository
        self.imap_reader_factory = imap_reader_factory
        self.imap_timeout_seconds = imap_timeout_seconds
        self.imap_ca_file = imap_ca_file

    def get_account(self, account_name: str) -> Account:
        account = self.repository.get_account(account_name)
        if account is None:
            raise KeyError(f"Unknown account: {account_name}")
        return account

    def generate_totp(self, account_name: str, for_time: datetime | int | None = None) -> str:
        """Generate a 6-digit TOTP in memory; never log or persist the result."""
        account = self.get_account(account_name)
        if not account.totp_secret:
            raise ValueError(f"Account {account_name!r} has no TOTP secret")
        totp = pyotp.TOTP(account.totp_secret, digits=6)
        return totp.now() if for_time is None else totp.at(for_time)

    async def read_mail(
        self,
        account_name: str,
        *,
        limit: int = 10,
        include_body: bool = False,
    ) -> list[MailMessage]:
        """Read recent associated mail over TLS without marking it as read."""
        account = self.get_account(account_name)
        if not all((account.imap_host, account.imap_username, account.imap_password)):
            raise ValueError(f"Account {account_name!r} has incomplete IMAP settings")

        config = IMAPConfig(
            host=account.imap_host,
            port=account.imap_port,
            username=account.imap_username,
            password=account.imap_password,
            mailbox=account.imap_mailbox,
            timeout_seconds=self.imap_timeout_seconds,
            ca_file=self.imap_ca_file,
        )
        reader = self.imap_reader_factory(config)
        return await reader.read_latest(limit=limit, include_body=include_body)

    def generate_credential(self, account_name: str, length: int = 24) -> RotationCandidate:
        """Create a high-entropy candidate for a known account.

        This only generates a candidate. It does not change a remote account or
        update SQLite; use record_successful_rotation after external success.
        """
        self.get_account(account_name)
        if length < 16:
            raise ValueError("Credential length must be at least 16")
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*()-_=+"
        while True:
            value = "".join(secrets.choice(alphabet) for _ in range(length))
            if (
                any(char.islower() for char in value)
                and any(char.isupper() for char in value)
                and any(char.isdigit() for char in value)
                and any(char in "!@#$%^&*()-_=+" for char in value)
            ):
                return RotationCandidate(account_name=account_name, new_credential=value)

    def record_successful_rotation(self, account_name: str, new_credential: str) -> None:
        """Commit a new credential only after a remote adapter confirms success."""
        self.get_account(account_name)
        self.repository.record_successful_rotation(account_name, new_credential)

    async def check_status(self, account_name: str) -> str:
        """Placeholder for a future, authorized internal-status adapter."""
        self.get_account(account_name)
        raise NotImplementedError(
            "Implement an approved status adapter for the owned internal test system"
        )
