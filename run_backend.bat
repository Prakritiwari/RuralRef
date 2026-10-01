@echo off
title RuralRefLink - backend (FastAPI :8000)

cd /d "%~dp0backend"

REM --- Pick a Python version that has prebuilt wheels for the pinned deps ----
REM     Python 3.14 cannot build pydantic-core==2.33.2 without a Rust toolchain.
set "PY="
py -3.13 --version >nul 2>&1 && set "PY=py -3.13"
if not defined PY py -3.12 --version >nul 2>&1 && set "PY=py -3.12"
if not defined PY py -3.11 --version >nul 2>&1 && set "PY=py -3.11"
if not defined PY set "PY=python"
echo Using Python: %PY%
%PY% --version

if not exist ".venv" (
    echo Creating virtual environment...
    %PY% -m venv .venv
)

call ".venv\Scripts\activate.bat"
python -m pip install --upgrade pip >nul
pip install -r requirements.txt

if not exist ".env" (
    echo.
    echo [note] No backend\.env found - the app will use the bundled SQLite database.
    echo        Run setup_database.bat once to use PostgreSQL instead.
    echo.
)

echo Starting API on http://localhost:8000  (docs: http://localhost:8000/docs)
uvicorn app.main:app --reload --port 8000
