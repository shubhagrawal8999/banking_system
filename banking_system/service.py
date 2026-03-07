from __future__ import annotations

from uuid import uuid4

from banking_system.models import BankAccount, CurrentAccount, SavingsAccount
from banking_system.repository import AccountRepository


class BankService:
    def __init__(self, repository: AccountRepository) -> None:
        self.repository = repository
        self.accounts: dict[str, BankAccount] = self.repository.load()

    def create_account(
        self,
        name: str,
        account_kind: str,
        initial_balance: float,
        min_balance: float = 500.0,
        overdraft_limit: float = 1000.0,
    ) -> BankAccount:
        account_id = str(uuid4())
        kind = account_kind.lower().strip()

        if kind == "savings":
            account: BankAccount = SavingsAccount(account_id, name, initial_balance, min_balance=min_balance)
        elif kind == "current":
            account = CurrentAccount(account_id, name, initial_balance, overdraft_limit=overdraft_limit)
        else:
            raise ValueError("Unknown account type")

        self.accounts[account_id] = account
        self.repository.save(self.accounts)
        return account

    def deposit(self, account_id: str, amount: float, note: str = "") -> None:
        account = self._get_account(account_id)
        account.deposit(amount, note=note)
        self.repository.save(self.accounts)

    def withdraw(self, account_id: str, amount: float, note: str = "") -> None:
        account = self._get_account(account_id)
        account.withdraw(amount, note=note)
        self.repository.save(self.accounts)

    def _get_account(self, account_id: str) -> BankAccount:
        if account_id not in self.accounts:
            raise ValueError("Account not found")
        return self.accounts[account_id]
