# RuralRefLink

**Real-Time Rural Hospital Referral & Resource Coordination**

RuralRefLink is a full-stack prototype that helps PHC doctors refer patients to suitable hospitals based on real-time resource availability.

> **Note:** This is an academic/demo coordination system, not a medical diagnostic system. Recommendations do not replace clinician judgement.

## Features

* Role-based login: Patient, PHC Doctor, Hospital Admin
* Create and manage patient referrals
* Hospital recommendations based on:

  * ICU beds
  * Specialists
  * Oxygen
  * Ventilators
* Explainable hospital ranking
* Referral accept/reject workflow
* Atomic resource reservation
* Ambulance allocation and live/simulated tracking
* Hospital dashboard
* Resource updates affect recommendations in real time

## Tech Stack

| Layer | Technology |
| ----- | ---------- |
| Frontend | React 18, Vite, CSS, Leaflet |
| Backend | FastAPI, SQLAlchemy 2.0, Pydantic v2 |
| Database | **PostgreSQL** (recommended) or **SQLite** (zero-setup fallback) |
| Authentication | JWT (python-jose), PBKDF2-SHA256 password hashing |
| Live updates | Polling + optional Supabase Realtime |

## Prerequisites

| Requirement | Version | Notes |
| ----------- | ------- | ----- |
| Python | **3.11 - 3.13** | Python 3.14 fails: `pydantic-core==2.33.2` has no prebuilt wheel and would require a Rust toolchain |
| Node.js | 18+ | |
| PostgreSQL | 13+ | Optional - only needed for the PostgreSQL database |

## Quick Start (Windows)

```bat
run_backend.bat     :: creates the venv, installs dependencies, starts the API on :8000
run_frontend.bat    :: installs npm dependencies, starts the web UI on :5173
```

Open **http://localhost:5173** and log in with a demo account.

> With no `backend\.env` present the project runs on **SQLite** and needs **zero
> database setup**. To use **PostgreSQL**, run `setup_database.bat` once (see below).

### Manual start (any OS)

```bash
# Backend
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev
```

## Database

All data access goes through SQLAlchemy. **The tables and the demo data are created automatically the first time the backend starts** - you never create them by hand. You only choose which engine to use.

### Option A - PostgreSQL (recommended)

Run the one-time setup script:

```bat
setup_database.bat
```

It asks for your `postgres` superuser password **once**, and then:

1. creates the role `ruralref` and the database `ruralref` (skipped if they already exist),
2. writes `backend\.env` with the connection string.

Then start the backend - it creates all 11 tables and seeds the demo data.

<details>
<summary>Manual equivalent</summary>

```bash
# 1) create the role + database (run as the postgres superuser)
psql -U postgres -d postgres -f scripts/bootstrap_database.sql

# 2) point the backend at it - backend/.env
DATABASE_URL=postgresql+psycopg://ruralref:ruralref@localhost:5432/ruralref
```

</details>

**Inspect the database at any time:**

```bat
show_database.bat
```

Prints the table list, row counts, the latest referrals, the hospital resource inventory and the recent audit trail - useful for demonstrating that the data is really persisted.

**Reset to a clean, freshly seeded database:**

```bat
setup_database.bat --reset
:: then restart run_backend.bat
```

### Option B - SQLite (zero setup)

Do nothing. Without a `backend\.env` the backend falls back to `sqlite:///./ruralref.db`, which is created and seeded automatically on first run.

### Tables created

| Table | Purpose |
| ----- | ------- |
| `profiles` | users - PHC / HOSPITAL / ADMIN / PATIENT |
| `phcs` | primary health centres |
| `hospitals` | referral hospitals |
| `resources` | resource catalog (ICU, ventilator, oxygen, blood, imaging, specialists) |
| `hospital_resources` | per-hospital inventory (total / available / reserved) |
| `patients` | patient records |
| `referrals` | referral requests and their status lifecycle |
| `referral_resources` | resources required by each referral |
| `ambulances` | ambulance fleet |
| `ambulance_locations` | GPS telemetry trail |
| `audit_logs` | JSON audit trail of every coordination action |

Referral status lifecycle:
`PENDING -> ACCEPTED / REJECTED -> AMBULANCE_ASSIGNED -> AMBULANCE_EN_ROUTE -> PATIENT_PICKED_UP -> PATIENT_IN_TRANSIT -> ARRIVED -> COMPLETED` (or `CANCELLED`).

## Demo Accounts

**Password for all accounts:** `demo123`

| Role           | Email               |
| -------------- | ------------------- |
| Admin          | `admin@demo.com`    |
| PHC Doctor     | `doctor@demo.com`   |
| Hospital Admin | `hospital@demo.com` |
| Patient        | `patient@demo.com`  |

The backend automatically creates the demo hospitals, specialists, ambulances, resources and user accounts on first startup.

## Project Structure

```text
RuralRef/
├── backend/                     FastAPI + SQLAlchemy API
│   ├── app/
│   │   ├── api/                 route modules (auth, referrals, hospitals, ...)
│   │   ├── models/              SQLAlchemy models (11 tables)
│   │   ├── schemas/             Pydantic request/response models
│   │   ├── services/            business logic (referral, resource, ambulance, ...)
│   │   ├── utils/               security (JWT + PBKDF2) and geo helpers
│   │   ├── config.py            settings (reads .env)
│   │   ├── database.py          engine / session / Base
│   │   └── main.py              app factory, table creation + seeding
│   ├── tests/                   pytest suite (in-memory SQLite)
│   └── .env.example             backend environment template
├── frontend/                    React + Vite UI
├── scripts/
│   ├── bootstrap_database.sql   idempotent role + database creation
│   ├── drop_database.sql        used by setup_database.bat --reset
│   └── find_psql.bat            locates the PostgreSQL client
├── setup_database.bat           one-time PostgreSQL setup
├── show_database.bat            display the live database
├── run_backend.bat              start the API
└── run_frontend.bat             start the UI
```

## Architecture

```text
PHC Doctor
    ↓
Create Referral
    ↓
Recommendation Engine
    ↓
Suitable Hospitals
    ↓
Hospital Accepts/Rejects
    ↓
Reserve Resources
    ↓
Allocate Ambulance
    ↓
Track Patient Transfer
```

## Troubleshooting

| Problem | Fix |
| ------- | --- |
| `pip install` fails while building `pydantic-core` | You are on Python 3.14. Use Python 3.11-3.13: `py -3.13 -m venv .venv` |
| `Could not find psql.exe` | PostgreSQL is not installed, or its `bin` folder is not on PATH. Re-run the PostgreSQL installer with "Command Line Tools", or check `C:\Program Files\PostgreSQL\<version>\bin`. |
| `could not connect to server` | The PostgreSQL service is stopped, or the password/port is wrong (default `5432`). Look for `postgresql-x64-<version>` in Windows Services. |
| `database "ruralref" does not exist` | Run `setup_database.bat` once. |
| "Cannot connect to the backend server" in the UI | The FastAPI server is not running - start `run_backend.bat`. |
| Password contains `#`, `@`, `:` or `/` | Do not put it in a connection URL. The setup script uses a dedicated `ruralref` role so you never have to escape it. |
| `git pull` complains about local changes to `ruralref.db` | The committed SQLite file was modified by running the app. Run `git checkout -- backend/ruralref.db`, then pull. |

## Production Improvements

For production deployment:

* PostgreSQL instead of SQLite (already supported - just set `DATABASE_URL`)
* Redis/WebSockets for real-time updates
* Encrypted health records
* Audit logging and consent management (the `audit_logs` table already exists)
* Verified hospital integrations
* Regulated mapping and notification services

## Disclaimer

RuralRefLink is an **academic/demo project**. It does not provide medical diagnosis or treatment recommendations. The recommendation engine only assists with operational hospital/resource coordination.
