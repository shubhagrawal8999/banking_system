from __future__ import annotations

import os

from flask import Flask, redirect, render_template, request, url_for

from banking_system.repository import AccountRepository
from banking_system.service import BankService


def _default_db_path() -> str:
    env_path = os.getenv("ACCOUNT_DB_PATH")
    if env_path:
        return env_path

    if os.getenv("VERCEL"):
        return "/tmp/accounts.json"

    return "data/accounts.json"


app = Flask(__name__)
service = BankService(AccountRepository(_default_db_path()))


@app.get("/")
def dashboard():
    accounts = list(service.accounts.values())
    return render_template("index.html", accounts=accounts, error=None, success=None)


@app.post("/accounts")
def create_account():
    name = request.form.get("name", "").strip()
    account_type = request.form.get("account_type", "savings")
    initial_balance = float(request.form.get("initial_balance", 0))
    min_balance = float(request.form.get("min_balance", 500))
    overdraft_limit = float(request.form.get("overdraft_limit", 1000))

    try:
        service.create_account(
            name=name,
            account_kind=account_type,
            initial_balance=initial_balance,
            min_balance=min_balance,
            overdraft_limit=overdraft_limit,
        )
        return redirect(url_for("dashboard"))
    except ValueError as exc:
        return render_template("index.html", accounts=list(service.accounts.values()), error=str(exc), success=None), 400


@app.post("/accounts/<account_id>/deposit")
def deposit(account_id: str):
    amount = float(request.form.get("amount", 0))
    try:
        service.deposit(account_id, amount, note="Web deposit")
        return redirect(url_for("dashboard"))
    except ValueError as exc:
        return render_template("index.html", accounts=list(service.accounts.values()), error=str(exc), success=None), 400


@app.post("/accounts/<account_id>/withdraw")
def withdraw(account_id: str):
    amount = float(request.form.get("amount", 0))
    try:
        service.withdraw(account_id, amount, note="Web withdrawal")
        return redirect(url_for("dashboard"))
    except ValueError as exc:
        return render_template("index.html", accounts=list(service.accounts.values()), error=str(exc), success=None), 400


def run_cli_menu() -> None:
    while True:
        print("\n=== Banking CLI ===")
        print("1. List accounts")
        print("2. Create account")
        print("3. Deposit")
        print("4. Withdraw")
        print("5. Exit")

        choice = input("Select: ").strip()
        try:
            if choice == "1":
                for acc in service.accounts.values():
                    print(acc.account_id, acc.name, acc.account_type(), acc.balance)
            elif choice == "2":
                name = input("Name: ").strip()
                kind = input("Type (savings/current): ").strip()
                initial = float(input("Initial balance: ").strip())
                if kind == "savings":
                    min_bal = float(input("Minimum balance: ").strip() or "500")
                    account = service.create_account(name, kind, initial, min_balance=min_bal)
                else:
                    limit = float(input("Overdraft limit: ").strip() or "1000")
                    account = service.create_account(name, kind, initial, overdraft_limit=limit)
                print("Created account:", account.account_id)
            elif choice == "3":
                service.deposit(input("Account ID: ").strip(), float(input("Amount: ").strip()), note="CLI deposit")
                print("Deposit successful")
            elif choice == "4":
                service.withdraw(input("Account ID: ").strip(), float(input("Amount: ").strip()), note="CLI withdrawal")
                print("Withdrawal successful")
            elif choice == "5":
                break
            else:
                print("Invalid choice")
        except ValueError as exc:
            print("Error:", exc)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=False)
