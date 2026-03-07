# Banking System (OOP + Web + CLI)

A production-style mini banking project using:
- **Abstraction** (`BankAccount` abstract base class)
- **Encapsulation** (controlled balance updates)
- **Inheritance** (`SavingsAccount`, `CurrentAccount`)
- **Polymorphism** (type-specific withdrawal rules)
- **Layered design** (models, service, repository, UI)

## Features
- Create savings/current accounts
- Deposit and withdraw funds
- Savings minimum balance rule
- Current account overdraft rule
- Transaction history per account
- File persistence (`data/accounts.json` locally, `/tmp/accounts.json` on Vercel)
- Web dashboard inspired by PayPal + Paytm color language
- CLI menu helper for terminal use

## Run locally
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```
Then open: `http://localhost:8000`

## Deploy on Vercel
This repo is now Vercel-ready.

### 1) Push code to GitHub
```bash
git add .
git commit -m "prepare vercel deployment"
git push
```

### 2) Import project in Vercel
- Go to Vercel dashboard → **Add New Project**.
- Import your GitHub repo.
- Framework preset: **Other**.
- No special build command required.

### 3) Optional environment variable
If you want custom file path for storage:
- `ACCOUNT_DB_PATH=/tmp/accounts.json` (default already used on Vercel).

### 4) Deploy
- Click **Deploy**.
- Vercel uses `vercel.json` and `api/index.py` automatically.

## Important Vercel note
Vercel serverless filesystem is ephemeral. Data in `/tmp` can reset between executions.
For true production persistence, replace JSON file storage with a managed database (PostgreSQL, Supabase, Neon, etc.).

## Test
```bash
pytest -q
```

## Project structure
- `banking_system/models.py` -> domain entities and OOP rules
- `banking_system/service.py` -> business operations
- `banking_system/repository.py` -> JSON persistence
- `banking_system/templates/index.html` -> web UI
- `banking_system/static/styles.css` -> branding/styling
- `tests/test_banking_system.py` -> unit tests
- `api/index.py` -> Vercel Python serverless entrypoint
- `vercel.json` -> Vercel routing/build config

## Debug mindset & common challenges
1. **Concurrent writes to JSON file**: move to DB (PostgreSQL) with transactions for multi-user scale.
2. **Float precision for money**: use `Decimal` for financial accuracy in production.
3. **Authentication & authorization**: secure account operations with login, roles, and audit logging.
4. **Input validation and abuse protection**: add form validation, rate limiting, and CSRF protection.
5. **Observability**: add structured logging, metrics, and tracing for incidents.

## What can be improved next
- JWT-based auth + user identity mapping
- REST API layer (`/api/v1/...`) and OpenAPI docs
- Docker + CI pipeline + cloud deployment
- Switch storage to SQLAlchemy + PostgreSQL
- Add transfer between accounts + reversal workflow
