from __future__ import annotations

import os

from flask import Flask, redirect, render_template, request, session, url_for

from banking_system.repository import AccountRepository
from banking_system.service import BankService

PIN_CODE = "1234"


def _default_db_path() -> str:
    env_path = os.getenv("ACCOUNT_DB_PATH")
    if env_path:
        return env_path

    if os.getenv("VERCEL"):
        return "/tmp/accounts.json"

    return "data/accounts.json"


def _create_app() -> Flask:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    template_dir = os.path.join(base_dir, "banking_system", "templates")
    static_dir = os.path.join(base_dir, "banking_system", "static")

    flask_app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
    flask_app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-only-secret-change-me")
    return flask_app


def _parse_amount(raw_value: str, field_name: str) -> float:
    try:
        value = float(raw_value)
    except (TypeError, ValueError):
        raise ValueError(f"{field_name} must be a valid number")

    return value


def _build_dashboard_stats(accounts: list) -> dict:
    total_balance = sum(account.balance for account in accounts)
    total_credited = 0.0
    total_debited = 0.0

    account_summaries = []
    for account in accounts:
        credited = 0.0
        debited = 0.0
        for tx in account.history:
            if tx.action == "deposit":
                credited += tx.amount
                total_credited += tx.amount
            elif tx.action == "withdraw":
                debited += tx.amount
                total_debited += tx.amount

        account_summaries.append(
            {
                "name": account.name,
                "kind": account.account_type(),
                "balance": account.balance,
                "credited": credited,
                "debited": debited,
                "account_id": account.account_id,
            }
        )

    return {
        "total_balance": total_balance,
        "total_credited": total_credited,
        "total_debited": total_debited,
        "active_accounts": len(accounts),
        "account_summaries": account_summaries,
    }


app = _create_app()
service = BankService(AccountRepository(_default_db_path()))


@app.before_request
def require_pin() -> None:
    public_endpoints = {"pin_login", "pin_login_submit", "static"}
    endpoint = request.endpoint or ""

    if endpoint in public_endpoints:
        return

    if session.get("pin_verified"):
        return

    return redirect(url_for("pin_login"))


@app.get("/pin")
def pin_login():
    return render_template("pin.html", error=None)


@app.post("/pin")
def pin_login_submit():
    pin = request.form.get("pin", "").strip()
    if pin == PIN_CODE:
        session["pin_verified"] = True
        return redirect(url_for("dashboard"))

    return render_template("pin.html", error="Invalid PIN. Try 1234."), 401


@app.post("/logout")
def logout():
    session.clear()
    return redirect(url_for("pin_login"))


@app.get("/")
def dashboard():
    accounts = list(service.accounts.values())
    stats = _build_dashboard_stats(accounts)
    return render_template("index.html", accounts=accounts, stats=stats, error=None, success=None)


@app.post("/accounts")
def create_account():
    try:
        name = request.form.get("name", "").strip()
        account_type = request.form.get("account_type", "savings")
        initial_balance = _parse_amount(request.form.get("initial_balance", "0"), "Initial balance")
        min_balance = _parse_amount(request.form.get("min_balance", "500"), "Minimum balance")
        overdraft_limit = _parse_amount(request.form.get("overdraft_limit", "1000"), "Overdraft limit")

        service.create_account(
            name=name,
            account_kind=account_type,
            initial_balance=initial_balance,
            min_balance=min_balance,
            overdraft_limit=overdraft_limit,
        )
        return redirect(url_for("dashboard"))
    except ValueError as exc:
        return render_template(
            "index.html",
            accounts=list(service.accounts.values()),
            stats=_build_dashboard_stats(list(service.accounts.values())),
            error=str(exc),
            success=None,
        ), 400


@app.post("/accounts/<account_id>/deposit")
def deposit(account_id: str):
    try:
        amount = _parse_amount(request.form.get("amount", "0"), "Deposit amount")
        service.deposit(account_id, amount, note="Web deposit")
        return redirect(url_for("dashboard"))
    except ValueError as exc:
        return render_template(
            "index.html",
            accounts=list(service.accounts.values()),
            stats=_build_dashboard_stats(list(service.accounts.values())),
            error=str(exc),
            success=None,
        ), 400


@app.post("/accounts/<account_id>/withdraw")
def withdraw(account_id: str):
    try:
        amount = _parse_amount(request.form.get("amount", "0"), "Withdraw amount")
        service.withdraw(account_id, amount, note="Web withdrawal")
        return redirect(url_for("dashboard"))
    except ValueError as exc:
        return render_template(
            "index.html",
            accounts=list(service.accounts.values()),
            stats=_build_dashboard_stats(list(service.accounts.values())),
            error=str(exc),
            success=None,
        ), 400


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
