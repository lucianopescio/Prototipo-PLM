@echo off
title Sistema PLM - Iniciador Automatico
echo ========================================
echo    SISTEMA PLM - INICIADOR AUTOMATICO
echo ========================================
echo.

echo [1/4] Activando entorno virtual Python...
call "%~dp0.venv\Scripts\activate.bat"
if errorlevel 1 (
    echo ERROR: No se pudo activar el entorno virtual
    echo Ejecuta primero: python -m venv .venv
    pause
    exit /b 1
)

echo [2/4] Verificando dependencias del backend...
python -c "import fastapi, uvicorn, pymongo, pandas, reportlab" 2>nul
if errorlevel 1 (
    echo ERROR: Faltan dependencias del backend
    echo Ejecutando: pip install -r requirements.txt
    pip install -r requirements.txt
)

echo [3/4] Verificando dependencias del frontend...
cd frontend
if not exist "node_modules" (
    echo Instalando dependencias del frontend...
    npm install
)
cd ..

echo [4/4] Iniciando servicios...
echo.
echo ⚡ INICIANDO BACKEND (Puerto 8000)...
start "PLM Backend" cmd /k "cd /d %~dp0 && .venv\Scripts\activate && python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload"

echo ⚡ Esperando 3 segundos...
timeout /t 3 /nobreak >nul

echo ⚡ INICIANDO FRONTEND (Puerto 3000)...
start "PLM Frontend" cmd /k "cd /d %~dp0\frontend && npm run dev"

echo.
echo ✅ SISTEMA INICIADO CORRECTAMENTE
echo.
echo 🌐 URLs del sistema:
echo    Backend API: http://127.0.0.1:8000
echo    Frontend Web: http://localhost:3000
echo.
echo 📱 El navegador se abrirá automáticamente en 5 segundos...
timeout /t 5 /nobreak >nul

echo ⚡ Abriendo navegador...
start http://localhost:3000

echo.
echo 🎯 SISTEMA LISTO PARA USAR
echo.
echo Para detener el sistema:
echo - Cierra las ventanas de Backend y Frontend
echo - O presiona Ctrl+C en cada ventana
echo.
pause