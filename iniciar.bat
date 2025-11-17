@echo off
title Sistema PLM - Iniciador Rapido
echo ========================================
echo    SISTEMA PLM - INICIADOR RAPIDO
echo ========================================
echo.

echo [1/3] Activando entorno virtual...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: No se pudo activar el entorno virtual
    echo Crea primero el entorno: python -m venv .venv
    pause
    exit /b 1
)

echo [2/3] Iniciando backend (Puerto 8000)...
start "PLM Backend" cmd /k "python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000"

echo [3/3] Esperando y iniciando frontend (Puerto 3000)...
timeout /t 3 /nobreak >nul

cd frontend
start "PLM Frontend" cmd /k "npm run dev"
cd ..

echo.
echo ✅ SISTEMA INICIADO CORRECTAMENTE
echo.
echo 🌐 URLs del sistema:
echo    Backend API: http://127.0.0.1:8000
echo    Frontend Web: http://localhost:3000
echo    Documentacion API: http://127.0.0.1:8000/docs
echo.
echo 📱 Abriendo navegador automaticamente...
timeout /t 3 /nobreak >nul
start http://localhost:3000

echo.
echo 🎯 Sistema listo para usar!
echo Para detener: cierra las ventanas del Backend y Frontend
pause
