# Banking System

> A learning project for applying object-oriented design, layered architecture, persistence, testing, and web deployment to a small banking domain.

## Why I built this

I wanted a project where the business rules were more important than the UI.

A banking system is a useful exercise because it forces you to model different account types, balance rules, transactions, persistence, and validation.

I used the project to practice turning business rules into a maintainable Python architecture.

## What it does

- Savings accounts
- Current accounts
- Deposits and withdrawals
- Minimum-balance rules
- Overdraft rules
- Transaction history
- JSON persistence
- Web dashboard
- CLI interaction
- Unit tests

## Architecture

~~~text
Web UI / CLI
     │
     ▼
BankService
     │
     ├── SavingsAccount
     ├── CurrentAccount
     └── Transaction
     │
     ▼
AccountRepository
     │
     ▼
JSON persistence
~~~

The main separation is simple: models contain domain rules, the service contains application operations, the repository handles persistence, and the UI handles web and CLI interaction.

## OOP concepts demonstrated

### Abstraction

BankAccount defines the common contract for account types.

### Encapsulation

Balance changes happen through controlled operations.

### Inheritance

SavingsAccount and CurrentAccount extend the base account model.

### Polymorphism

Each account type implements its own withdrawal rule.

~~~text
Savings:
balance - withdrawal >= minimum balance

Current:
balance - withdrawal >= -overdraft limit
~~~

## Tech stack

- Python
- Flask
- Object-oriented design
- JSON persistence
- pytest
- Vercel

## Project structure

~~~text
.
├── app.py
├── banking_system/
│   ├── models.py
│   ├── service.py
│   ├── repository.py
│   ├── templates/
│   └── static/
├── tests/
├── api/
├── requirements.txt
└── vercel.json
~~~

## Run locally

~~~bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
~~~

Open http://localhost:8000

Run tests with pytest -q.

## Deployment

The project includes a Vercel entrypoint. For the deployed version, JSON storage is placed under /tmp.

That is useful for demonstrating deployment, but it is not durable production storage.

## Engineering trade-offs

### JSON instead of PostgreSQL

I kept persistence simple so the focus stayed on domain modeling.

### Float instead of Decimal

The implementation currently uses floats for simplicity. A financial production system should use Decimal or another exact monetary representation.

### No authentication

The project focuses on application architecture rather than identity and authorization.

## What I learned

This project taught me that good architecture is mostly about boundaries. Keeping domain rules separate from persistence and UI made the system easier to reason about and extend.

## Roadmap

- [ ] Replace JSON with PostgreSQL
- [ ] Use Decimal for monetary values
- [ ] Add authentication and authorization
- [ ] Add account-to-account transfers
- [ ] Add transaction reversal flows
- [ ] Add structured logging
- [ ] Add API documentation
- [ ] Add CI

## Status

✅ Learning project / deployable demo
