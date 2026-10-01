@echo off
title RuralRefLink - database viewer

set "ROOT=%~dp0"

call "%ROOT%scripts\find_psql.bat"
if not defined PSQL (
    echo [ERROR] Could not find psql.exe. Is PostgreSQL installed?
    echo.
    pause
    exit /b 1
)

set "PGPASSWORD=ruralref"
"%PSQL%" -h localhost -p 5432 -U ruralref -d ruralref -w -tAc "SELECT 1" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Cannot connect to database 'ruralref' on localhost:5432.
    echo         Run setup_database.bat first, then start the backend once
    echo         so the tables and demo data are created.
    echo.
    pause
    exit /b 1
)

echo ==============================================================
echo   RuralRefLink database  ^|  ruralref @ localhost:5432
echo ==============================================================

echo.
echo ### Tables
"%PSQL%" -h localhost -p 5432 -U ruralref -d ruralref -w -c "\dt"

echo ### Row counts
"%PSQL%" -h localhost -p 5432 -U ruralref -d ruralref -w -c "SELECT 'profiles' AS tbl, count(*) FROM profiles UNION ALL SELECT 'phcs', count(*) FROM phcs UNION ALL SELECT 'hospitals', count(*) FROM hospitals UNION ALL SELECT 'resources', count(*) FROM resources UNION ALL SELECT 'hospital_resources', count(*) FROM hospital_resources UNION ALL SELECT 'patients', count(*) FROM patients UNION ALL SELECT 'referrals', count(*) FROM referrals UNION ALL SELECT 'referral_resources', count(*) FROM referral_resources UNION ALL SELECT 'ambulances', count(*) FROM ambulances UNION ALL SELECT 'ambulance_locations', count(*) FROM ambulance_locations UNION ALL SELECT 'audit_logs', count(*) FROM audit_logs ORDER BY 1;"

echo ### Latest referrals
"%PSQL%" -h localhost -p 5432 -U ruralref -d ruralref -w -c "SELECT referral_number, urgency, status, created_at FROM referrals ORDER BY created_at DESC LIMIT 8;"

echo ### Hospital resource inventory (total / available / reserved)
"%PSQL%" -h localhost -p 5432 -U ruralref -d ruralref -w -c "SELECT h.name AS hospital, hr.resource_id, hr.total_quantity AS total, hr.available_quantity AS avail, hr.reserved_quantity AS reserved FROM hospital_resources hr JOIN hospitals h ON h.id = hr.hospital_id ORDER BY h.name, hr.resource_id;"

echo ### Recent audit trail
"%PSQL%" -h localhost -p 5432 -U ruralref -d ruralref -w -c "SELECT id, action, entity_type, created_at FROM audit_logs ORDER BY id DESC LIMIT 10;"

echo.
echo Tip: create a referral in the web UI, then run this script again to see it here.
echo.
pause
