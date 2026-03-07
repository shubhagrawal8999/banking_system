from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class Transaction:
    account_id: str
    action: str
    amount: float
    balance_after: float
    timestamp: str
    note: str = ""

    @staticmethod
    def now_timestamp() -> str:
        return datetime.now(timezone.utc).isoformat()


class BankAccount(ABC):
    def __init__(self, account_id: str, name: str, balance: float) -> None:
        if balance < 0:
            raise ValueError("Starting balance cannot be negative")

        self.account_id = account_id
        self.name = name
        self._balance = float(balance)
        self._history: list[Transaction] = []

    @property
    def balance(self) -> float:
        return self._balance

    @property
    def history(self) -> list[Transaction]:
        return list(self._history)

    @abstractmethod
    def account_type(self) -> str:
        raise NotImplementedError

    def deposit(self, amount: float, note: str = "") -> Transaction:
        if amount <= 0:
            raise ValueError("Deposit amount must be greater than zero")

        self._balance += amount
        tx = Transaction(
            account_id=self.account_id,
            action="deposit",
            amount=amount,
            balance_after=self._balance,
            timestamp=Transaction.now_timestamp(),
            note=note,
        )
        self._history.append(tx)
        return tx

    def withdraw(self, amount: float, note: str = "") -> Transaction:
        if amount <= 0:
            raise ValueError("Withdraw amount must be greater than zero")

        if not self._can_withdraw(amount):
            raise ValueError("Insufficient allowed balance for withdrawal")

        self._balance -= amount
        tx = Transaction(
            account_id=self.account_id,
            action="withdraw",
            amount=amount,
            balance_after=self._balance,
            timestamp=Transaction.now_timestamp(),
            note=note,
        )
        self._history.append(tx)
        return tx

    @abstractmethod
    def _can_withdraw(self, amount: float) -> bool:
        raise NotImplementedError

    @abstractmethod
    def serialize_config(self) -> dict:
        raise NotImplementedError


class SavingsAccount(BankAccount):
    def __init__(self, account_id: str, name: str, balance: float, min_balance: float = 500.0) -> None:
        self.min_balance = min_balance
        super().__init__(account_id=account_id, name=name, balance=balance)
        if self._balance < self.min_balance:
            raise ValueError("Starting balance violates minimum savings balance")

    def account_type(self) -> str:
        return "Savings Account"

    def _can_withdraw(self, amount: float) -> bool:
        return (self._balance - amount) >= self.min_balance

    def serialize_config(self) -> dict:
        return {"min_balance": self.min_balance}


class CurrentAccount(BankAccount):
    def __init__(self, account_id: str, name: str, balance: float, overdraft_limit: float = 1000.0) -> None:
        self.overdraft_limit = overdraft_limit
        super().__init__(account_id=account_id, name=name, balance=balance)

    def account_type(self) -> str:
        return "Current Account"

    def _can_withdraw(self, amount: float) -> bool:
        return (self._balance - amount) >= -self.overdraft_limit

    def serialize_config(self) -> dict:
        return {"overdraft_limit": self.overdraft_limit}
