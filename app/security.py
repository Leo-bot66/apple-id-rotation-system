from __future__ import annotations

from cryptography.fernet import Fernet, InvalidToken


class SecretBox:
    """Encrypt/decrypt short secrets using a Fernet key.

    This is a local-development abstraction. In production, replace it with a
    KMS/Vault-backed implementation while keeping the repository interface.
    """

    def __init__(self, key: str | bytes) -> None:
        try:
            self._fernet = Fernet(key.encode() if isinstance(key, str) else key)
        except (TypeError, ValueError) as exc:
            raise ValueError("ROTATOR_FERNET_KEY is not a valid Fernet key") from exc

    def encrypt(self, value: str | None) -> bytes | None:
        if value is None:
            return None
        return self._fernet.encrypt(value.encode("utf-8"))

    def decrypt(self, value: bytes | str | None) -> str | None:
        if value is None:
            return None
        token = value.encode("ascii") if isinstance(value, str) else value
        try:
            return self._fernet.decrypt(token).decode("utf-8")
        except (InvalidToken, UnicodeDecodeError) as exc:
            raise ValueError("Unable to decrypt stored secret") from exc

    @staticmethod
    def redact(value: str | None, visible: int = 2) -> str:
        """Return a safe log representation; never log secrets directly."""
        if not value:
            return "<empty>"
        if len(value) <= visible:
            return "*" * len(value)
        return f"{value[:visible]}***"
