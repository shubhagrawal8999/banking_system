from pathlib import Path

import pytest

from banking_system.repository import AccountRepository
from banking_system.service import BankService


@pytest.fixture()
def service(tmp_path: Path) -> BankService:
    repo = AccountRepository(str(tmp_path / "accounts.json"))
    return BankService(repo)


def test_create_savings_and_withdraw_min_balance(service: BankService) -> None:
    acc = service.create_account("Deepak", "savings", 2000, min_balance=500)
    service.withdraw(acc.account_id, 1200)
    assert service.accounts[acc.account_id].balance == pytest.approx(800)

    with pytest.raises(ValueError):
        service.withdraw(acc.account_id, 400)


def test_current_account_overdraft(service: BankService) -> None:
    acc = service.create_account("Amit", "current", 1000, overdraft_limit=2000)
    service.withdraw(acc.account_id, 2500)
    assert service.accounts[acc.account_id].balance == pytest.approx(-1500)

    with pytest.raises(ValueError):
        service.withdraw(acc.account_id, 1000)


def test_history_and_persistence(tmp_path: Path) -> None:
    db_path = tmp_path / "db.json"
    service = BankService(AccountRepository(str(db_path)))
    acc = service.create_account("Riya", "savings", 1200)
    service.deposit(acc.account_id, 300)
    service.withdraw(acc.account_id, 200)

    reloaded = BankService(AccountRepository(str(db_path)))
    saved = reloaded.accounts[acc.account_id]

    assert saved.balance == pytest.approx(1300)
    assert len(saved.history) == 2
    assert [tx.action for tx in saved.history] == ["deposit", "withdraw"]
