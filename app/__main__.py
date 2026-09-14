from __future__ import annotations

from pathlib import Path

from .config import Settings
from .db import SQLiteAccountRepository
from .security import SecretBox


def main() -> None:
    settings = Settings.from_env()
    Path(settings.db_path).parent.mkdir(parents=True, exist_ok=True)
    repository = SQLiteAccountRepository(settings.db_path, SecretBox(settings.fernet_key))
    print(f"Database ready: {repository.path}")


if __name__ == "__main__":
    main()
