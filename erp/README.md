# ERP Monorepo

A minimal enterprise resource planning scaffold for accounting and finance teams. The backend exposes a Django REST Framework API backed by PostgreSQL, while the frontend delivers a Next.js 14 dashboard with Tailwind CSS.

## Stack

- **Backend:** Django 5, Django REST Framework, PostgreSQL, django-filter, django-cors-headers
- **Frontend:** Next.js 14 App Router, TypeScript, Tailwind CSS, fetch + Zod for typed API calls
- **Tooling:** pnpm, docker compose (Postgres), python-dotenv

## Repository layout

```
erp/
  backend/              # Django project (manage.py, apps, settings)
  frontend/             # Next.js application (App Router)
  docker-compose.yml    # Postgres service for local development
  .env.example          # Sample environment variables for both apps
```

### Backend apps

- `apps.accounts` – role management, authentication endpoints, seed command
- `apps.ledger` – chart of accounts, journal entries + nested lines with double-entry enforcement
- `apps.reports` – financial report services (trial balance, income statement, balance sheet, cash flow)
- `apps.budgets` – account budgets with cadence filters
- `apps.approvals` – workflow approvals and close checklist tracking

## Prerequisites

- Python 3.11+
- Node.js 18+
- pnpm 9+
- Docker + docker compose plugin (for Postgres)

## Environment

Copy the sample file and adjust as needed:

```bash
cp .env.example .env
```

> The backend reads `.env` from `erp/backend/.env` (same values as root). The frontend consumes `NEXT_PUBLIC_API_BASE_URL` at build/run time.

## Database (Postgres)

Start Postgres with docker compose:

```bash
cd erp
docker compose up -d db
```

Connection details match the defaults in `.env.example` (`postgresql://erp:erp@localhost:5432/erp`).

## Backend setup

```bash
cd erp/backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo   # loads demo users, chart of accounts, sample data
python manage.py runserver 0.0.0.0:8000
```

Key API endpoints (all prefixed with `/api/`):

- `auth/login`, `auth/logout`, `me`
- CRUD: `roles`, `users`, `accounts`, `journal-entries`, `budgets`, `approvals`, `close-checklist`
- Reports: `reports/trial-balance`, `reports/income-statement`, `reports/balance-sheet`, `reports/cash-flow`

Pagination, ordering, and filtering are enabled via query parameters (e.g. `?date_after=&date_before=&status=`).

## Frontend setup

```bash
cd erp/frontend
pnpm install
pnpm dev
```

The development server runs on [http://localhost:3000](http://localhost:3000) and consumes the Django API at `NEXT_PUBLIC_API_BASE_URL`.

### Frontend highlights

- Global shell with sidebar navigation and contextual top bar
- Income Statement view with date range, cadence selector, report view dropdown, filter stub, export buttons, and hierarchical table supporting expand/collapse
- Shared components: Sidebar, Topbar, DateRangePicker, Dropdown, Badge, Table with CollapsibleRow, ExportButtons
- Typed API client (`lib/api.ts`) using Zod schemas
- Loading/empty/error handling hooks ready to extend (table renders balanced values returned from the API)

## Seeding and roles

`python manage.py seed_demo` creates:

- Roles: Admin, Accountant, Viewer
- Users (password `changeme123`): `admin`, `accountant`, `viewer`
- Chart of accounts (1000–6300 ranges) with operating expense roll-ups
- Twelve months of sample revenue/expense journal entries (posted)
- Budgets for major operating expense accounts
- Sample approvals and close checklist items

## Next steps

- Connect remaining report pages (balance sheet, cash flow, trial balance) to the exposed API services
- Add authentication UI flows (login, role-aware visibility)
- Write automated tests for posting logic and reporting calculations
