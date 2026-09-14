from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    db_path: Path
    fernet_key: str
    imap_timeout_seconds: float = 20.0
    imap_ca_file: str | None = None

    @classmethod
    def from_env(cls) -> "Settings":
        load_dotenv()

        key = os.getenv("ROTATOR_FERNET_KEY", "").strip()
        if not key or key == "replace-with-a-fernet-key":
            raise RuntimeError(
                "ROTATOR_FERNET_KEY is missing. Generate one with Fernet.generate_key()."
            )

        timeout = float(os.getenv("ROTATOR_IMAP_TIMEOUT_SECONDS", "20"))
        if timeout <= 0:
            raise ValueError("ROTATOR_IMAP_TIMEOUT_SECONDS must be positive")

        return cls(
            db_path=Path(os.getenv("ROTATOR_DB_PATH", "./data/rotator.sqlite3")),
            fernet_key=key,
            imap_timeout_seconds=timeout,
            imap_ca_file=os.getenv("ROTATOR_IMAP_CA_FILE") or None,
        )
