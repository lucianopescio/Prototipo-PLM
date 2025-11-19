@echo off
title Sistema PLM - Diagnostico y Reparacion
color 0A
echo ========================================
echo    SISTEMA PLM - DIAGNOSTICO
echo ========================================
echo.

echo [1/8] Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Python no encontrado
    echo.
    echo SOLUCION:
    echo 1. Instala Python 3.8+ desde https://python.org
    echo 2. Asegurate de agregar Python al PATH
    echo 3. Reinicia el CMD y ejecuta este script nuevamente
    pause
    exit /b 1
) else (
    for /f "tokens=*" %%i in ('python --version') do echo ✅ %%i
)

echo [2/8] Verificando Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Node.js no encontrado
    echo.
    echo SOLUCION:
    echo 1. Instala Node.js LTS desde https://nodejs.org
    echo 2. Reinicia el CMD y ejecuta este script nuevamente
    pause
    exit /b 1
) else (
    for /f "tokens=*" %%i in ('node --version') do echo ✅ Node.js %%i
)

echo [3/8] Verificando ubicacion del proyecto...
if not exist "backend\main.py" (
    echo ❌ ERROR: No estas en la carpeta correcta del proyecto
    echo.
    echo SOLUCION:
    echo 1. Navega a la carpeta que contiene 'backend', 'frontend', etc.
    echo 2. Ejecuta este script desde esa ubicacion
    echo.
    echo ESTRUCTURA ESPERADA:
    echo   tu-carpeta\
    echo   ├── backend\
    echo   ├── frontend\
    echo   ├── iniciar.bat
    echo   └── diagnostico.bat ^(este archivo^)
    pause
    exit /b 1
) else (
    echo ✅ Proyecto encontrado en ubicacion correcta
)

echo [4/8] Creando/verificando entorno virtual...
if not exist ".venv" (
    echo Creando entorno virtual...
    python -m venv .venv
    if errorlevel 1 (
        echo ❌ ERROR: No se pudo crear entorno virtual
        pause
        exit /b 1
    )
    echo ✅ Entorno virtual creado
) else (
    echo ✅ Entorno virtual ya existe
)

echo [5/8] Activando entorno virtual...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ ERROR: No se pudo activar entorno virtual
    pause
    exit /b 1
) else (
    echo ✅ Entorno virtual activado
)

echo [6/8] Instalando dependencias Python...
echo Esto puede tomar unos minutos...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ ERROR: Problemas instalando dependencias Python
    echo Continuando con el diagnostico...
) else (
    echo ✅ Dependencias Python instaladas
)

echo [7/8] Verificando/instalando dependencias frontend...
cd frontend
if not exist "node_modules" (
    echo Instalando dependencias frontend...
    echo Esto puede tomar varios minutos...
    npm install
    if errorlevel 1 (
        echo ❌ ERROR: Problemas instalando dependencias frontend
        cd ..
        pause
        exit /b 1
    )
    echo ✅ Dependencias frontend instaladas
) else (
    echo ✅ Dependencias frontend ya instaladas
)
cd ..

echo [8/8] Verificando estructura de archivos...
set missing_files=0

if not exist "backend\main.py" (
    echo ❌ Falta: backend\main.py
    set /a missing_files+=1
)

if not exist "frontend\package.json" (
    echo ❌ Falta: frontend\package.json
    set /a missing_files+=1
)

if not exist "requirements.txt" (
    echo ❌ Falta: requirements.txt
    set /a missing_files+=1
)

if %missing_files% equ 0 (
    echo ✅ Todos los archivos principales encontrados
) else (
    echo ❌ Faltan %missing_files% archivos importantes
)

echo.
echo ========================================
echo    RESUMEN DEL DIAGNOSTICO
echo ========================================

if %missing_files% equ 0 (
    echo ✅ SISTEMA LISTO PARA USAR
    echo.
    echo CREDENCIALES DE ACCESO:
    echo   Email: demo@plm.com
    echo   Password: plm123
    echo.
    echo   O alternativamente:
    echo   Email: admin@plm.com  
    echo   Password: admin123
    echo.
    echo SIGUIENTE PASO:
    echo   Ejecuta 'iniciar.bat' para iniciar el sistema
) else (
    echo ❌ HAY PROBLEMAS QUE RESOLVER
    echo Revisa los errores mostrados arriba
)

echo.
pause