@echo off
REM ---------------------------------------------------------------------------
REM  Locates psql.exe and stores its full path in the PSQL variable.
REM
REM  Usage from another script:   call "%~dp0scripts\find_psql.bat"
REM
REM  NOTE: deliberately does NOT use "setlocal", so PSQL survives the call.
REM ---------------------------------------------------------------------------

set "PSQL="

REM 1) Prefer a psql that is already on PATH
for /f "delims=" %%P in ('where psql 2^>nul') do if not defined PSQL set "PSQL=%%P"

REM 2) Fall back to the standard PostgreSQL install locations (newest first)
if not defined PSQL (
    for /f "delims=" %%D in ('dir /b /o-n "C:\Program Files\PostgreSQL" 2^>nul') do (
        if not defined PSQL if exist "C:\Program Files\PostgreSQL\%%D\bin\psql.exe" set "PSQL=C:\Program Files\PostgreSQL\%%D\bin\psql.exe"
    )
)

REM 3) Last resort: un-versioned install path
if not defined PSQL if exist "C:\Program Files\PostgreSQL\bin\psql.exe" set "PSQL=C:\Program Files\PostgreSQL\bin\psql.exe"

exit /b 0
