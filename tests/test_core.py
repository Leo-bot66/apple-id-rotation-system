from __future__ import annotations

from pathlib import Path

import pyotp
from cryptography.fernet import Fernet

from app.db import SQLiteAccountRepository
from app.rotator import AccountRotator
from app.security import SecretBox


def make_repository(tmp_path: Path) -> SQLiteAccountRepository:
    return SQLiteAccountRepository(
        tmp_path / "rotator.sqlite3",
        SecretBox(Fernet.generate_key()),
    )


def test_secret_box_round_trip() -> None:
    box = SecretBox(Fernet.generate_key())
    assert box.decrypt(box.encrypt("密文测试")) == "密文测试"
    assert box.decrypt(None) is None


def test_account_is_encrypted_at_rest(tmp_path: Path) -> None:
    repository = make_repository(tmp_path)
    repository.add_account(
        account_name="qa-001",
        current_credential="A-strong-test-password!",
        security_answer="answer",
        totp_secret=pyotp.random_base32(),
        imap_host="imap.example.test",
        imap_username="qa@example.test",
        imap_password="mail-password",
    )

    raw = (tmp_path / "rotator.sqlite3").read_bytes()
    assert b"A-strong-test-password!" not in raw
    assert repository.get_account("qa-001").current_credential == "A-strong-test-password!"


def test_totp_generation(tmp_path: Path) -> None:
    secret = "JBSWY3DPEHPK3PXP"
    repository = make_repository(tmp_path)
    repository.add_account(account_name="qa-002", totp_secret=secret)
    rotator = AccountRotator(repository)

    assert rotator.generate_totp("qa-002", for_time=0) == pyotp.TOTP(secret).at(0)


def test_credential_candidate_is_bound_to_known_account(tmp_path: Path) -> None:
    repository = make_repository(tmp_path)
    repository.add_account(account_name="qa-003")
    candidate = AccountRotator(repository).generate_credential("qa-003")

    assert candidate.account_name == "qa-003"
    assert len(candidate.new_credential) == 24
    assert any(char.isupper() for char in candidate.new_credential)
    assert any(char.islower() for char in candidate.new_credential)
    assert any(char.isdigit() for char in candidate.new_credential)
