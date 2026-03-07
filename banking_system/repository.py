from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from banking_system.models import BankAccount, CurrentAccount, SavingsAccount, Transaction


class AccountRepository:
    def __init__(self, db_path: str = "data/accounts.json") -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def save(self, accounts: dict[str, BankAccount]) -> None:
        payload = {"accounts": [self._serialize_account(account) for account in accounts.values()]}
        self.db_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def load(self) -> dict[str, BankAccount]:
        if not self.db_path.exists():
            return {}

        raw = self.db_path.read_text(encoding="utf-8")
        if not raw.strip():
            return {}

        payload = json.loads(raw)
        result: dict[str, BankAccount] = {}
        for item in payload.get("accounts", []):
            account = self._deserialize_account(item)
            result[account.account_id] = account
        return result

    @staticmethod
    def _serialize_account(account: BankAccount) -> dict:
        return {
            "account_id": account.account_id,
            "name": account.name,
            "balance": account.balance,
            "type": account.account_type(),
            "config": account.serialize_config(),
            "history": [asdict(tx) for tx in account.history],
        }

    @staticmethod
    def _deserialize_account(item: dict) -> BankAccount:
        if item["type"] == "Savings Account":
            account: BankAccount = SavingsAccount(
                account_id=item["account_id"],
                name=item["name"],
                balance=float(item["balance"]),
                min_balance=float(item.get("config", {}).get("min_balance", 500.0)),
            )
        elif item["type"] == "Current Account":
            account = CurrentAccount(
                account_id=item["account_id"],
                name=item["name"],
                balance=float(item["balance"]),
                overdraft_limit=float(item.get("config", {}).get("overdraft_limit", 1000.0)),
            )
        else:
            raise ValueError(f"Unknown account type: {item['type']}")

        account._history = [Transaction(**tx) for tx in item.get("history", [])]
        return account
