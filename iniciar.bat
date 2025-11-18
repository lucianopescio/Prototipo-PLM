@echo off
title Sistema PLM - Iniciador Rapido
echo ========================================
echo    SISTEMA PLM - INICIADOR RAPIDO
echo ========================================
echo.

echo [1/4] Verificando entorno virtual...
if not exist ".venv" (
    echo Creando entorno virtual...
    python -m venv .venv
    if errorlevel 1 (
        echo ERROR: No se pudo crear el entorno virtual
        echo Verifica que Python este instalado
        pause
        exit /b 1
    )
)

echo [2/4] Activando entorno virtual...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: No se pudo activar el entorno virtual
    pause
    exit /b 1
)

echo [3/6] Instalando dependencias Python...
pip install -r requirements.txt >nul 2>&1

echo [4/6] Verificando dependencias del frontend...
cd frontend
if not exist "node_modules" (
    echo [5/6] Instalando dependencias del frontend...
    npm install >nul 2>&1
) else (
    echo [5/6] Dependencias del frontend ya instaladas
)
cd ..

echo [6/6] Iniciando servicios...
echo   - Backend (Puerto 8000)...
start "PLM Backend" cmd /k "python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000"

echo   - Frontend (Puerto 3000)...
timeout /t 3 /nobreak >nul

cd frontend
start "PLM Frontend" cmd /k "npm run dev -- --no-open"
cd ..

echo.
echo  SISTEMA INICIADO CORRECTAMENTE
echo.
echo  URLs del sistema:
echo    Backend API: http://127.0.0.1:8000
echo    Frontend Web: http://localhost:3000
echo    Documentacion API: http://127.0.0.1:8000/docs
echo.
echo  Abriendo navegador automaticamente...
timeout /t 3 /nobreak >nul
start http://localhost:3000

echo.
echo  Sistema OK para uso 
echo Para detener: cierra las ventanas del Backend y Frontend
pause
