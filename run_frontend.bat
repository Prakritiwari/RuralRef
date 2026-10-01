@echo off
title RuralRefLink - frontend (Vite :5173)

cd /d "%~dp0frontend"

if not exist "node_modules" (
    echo Installing frontend dependencies...
    call npm install
)

echo Starting web UI on http://localhost:5173
call npm run dev
