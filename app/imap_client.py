from __future__ import annotations

import asyncio
import email
import imaplib
import ssl
from dataclasses import dataclass
from email.header import decode_header, make_header
from email.message import Message
from email.parser import BytesParser
from email.policy import default


@dataclass(frozen=True)
class IMAPConfig:
    host: str
    port: int = 993
    username: str = ""
    password: str = ""
    mailbox: str = "INBOX"
    timeout_seconds: float = 20.0
    ca_file: str | None = None


@dataclass(frozen=True)
class MailMessage:
    uid: str
    subject: str
    sender: str
    date: str
    text_body: str | None = None


class IMAPReader:
    """Read recent mail over IMAP TLS without marking messages as read.

    imaplib is blocking, so the public methods use asyncio.to_thread. This
    adapter decodes MIME transfer encoding only; application-specific email
    decryption and authorization-code extraction are deliberately hooks, not
    implemented behavior.
    """

    def __init__(self, config: IMAPConfig) -> None:
        self.config = config

    async def read_latest(self, limit: int = 10, include_body: bool = False) -> list[MailMessage]:
        if limit < 1 or limit > 100:
            raise ValueError("limit must be between 1 and 100")
        return await asyncio.to_thread(self._read_latest_blocking, limit, include_body)

    def _read_latest_blocking(self, limit: int, include_body: bool) -> list[MailMessage]:
        context = ssl.create_default_context(cafile=self.config.ca_file)
        client = imaplib.IMAP4_SSL(
            self.config.host,
            self.config.port,
            ssl_context=context,
            timeout=self.config.timeout_seconds,
        )
        try:
            client.login(self.config.username, self.config.password)
            result, _ = client.select(self.config.mailbox, readonly=True)
            if result != "OK":
                raise RuntimeError(f"Unable to select IMAP mailbox: {self.config.mailbox}")

            result, data = client.uid("search", None, "ALL")
            if result != "OK" or not data or not data[0]:
                return []

            uids = data[0].split()[-limit:]
            messages: list[MailMessage] = []
            for raw_uid in reversed(uids):
                uid = raw_uid.decode("ascii", errors="replace")
                messages.append(self._fetch_one(client, uid, include_body))
            return messages
        finally:
            try:
                client.close()
            except imaplib.IMAP4.error:
                pass
            try:
                client.logout()
            except imaplib.IMAP4.error:
                pass

    def _fetch_one(self, client: imaplib.IMAP4_SSL, uid: str, include_body: bool) -> MailMessage:
        section = "BODY.PEEK[]" if include_body else "BODY.PEEK[HEADER]"
        result, data = client.uid("fetch", uid, f"({section})")
        if result != "OK":
            raise RuntimeError(f"Unable to fetch IMAP message UID {uid}")
        raw = b"".join(part[1] for part in data if isinstance(part, tuple) and len(part) > 1)
        parsed = BytesParser(policy=default).parsebytes(raw)
        body = self._extract_text(parsed) if include_body else None
        return MailMessage(
            uid=uid,
            subject=self._decode_header_value(parsed.get("Subject", "")),
            sender=self._decode_header_value(parsed.get("From", "")),
            date=parsed.get("Date", ""),
            text_body=body,
        )

    @staticmethod
    def _decode_header_value(value: str) -> str:
        try:
            return str(make_header(decode_header(value)))
        except (ValueError, UnicodeError):
            return value

    @classmethod
    def _extract_text(cls, message: Message) -> str:
        chunks: list[str] = []
        parts = message.walk() if message.is_multipart() else [message]
        for part in parts:
            if part.get_content_maintype() == "multipart":
                continue
            if part.get_content_type() != "text/plain":
                continue
            payload = part.get_payload(decode=True)
            if not payload:
                continue
            charset = part.get_content_charset() or "utf-8"
            chunks.append(payload.decode(charset, errors="replace"))
        return "\n".join(chunks)

    def decrypt_message_body(self, encrypted_payload: bytes, *, key_id: str) -> bytes:
        """Integration point for an approved S/MIME/PGP service.

        Private keys must not be embedded in this project or stored in SQLite.
        """
        raise NotImplementedError(
            f"Configure an approved message-decryption provider for key_id={key_id!r}"
        )
