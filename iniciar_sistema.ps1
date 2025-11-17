# ========================================
#    SISTEMA PLM - INICIADOR POWERSHELL
# ========================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   SISTEMA PLM - INICIADOR AUTOMATICO" -ForegroundColor Cyan  
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Configuración
$BackendPort = 8000
$FrontendPort = 3000
$ProjectRoot = $PSScriptRoot

Write-Host "[1/4] Activando entorno virtual Python..." -ForegroundColor Yellow
$VenvPath = Join-Path $ProjectRoot ".venv\Scripts\Activate.ps1"

try {
    & $VenvPath
    Write-Host "✅ Entorno virtual activado" -ForegroundColor Green
} catch {
    Write-Host "❌ ERROR: No se pudo activar el entorno virtual" -ForegroundColor Red
    Write-Host "Ejecuta primero: python -m venv .venv" -ForegroundColor Red
    Read-Host "Presiona Enter para continuar"
    exit 1
}

Write-Host "[2/4] Verificando dependencias del backend..." -ForegroundColor Yellow
try {
    python -c "import fastapi, uvicorn, pymongo, pandas, reportlab" 2>$null
    Write-Host "✅ Dependencias del backend verificadas" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Instalando dependencias del backend..." -ForegroundColor Yellow
    pip install -r requirements.txt
}

Write-Host "[3/4] Verificando dependencias del frontend..." -ForegroundColor Yellow
$FrontendPath = Join-Path $ProjectRoot "frontend"
Push-Location $FrontendPath

if (!(Test-Path "node_modules")) {
    Write-Host "⚠️ Instalando dependencias del frontend..." -ForegroundColor Yellow
    npm install
} else {
    Write-Host "✅ Dependencias del frontend verificadas" -ForegroundColor Green
}

Pop-Location

Write-Host "[4/4] Iniciando servicios..." -ForegroundColor Yellow
Write-Host ""

# Función para verificar si un puerto está en uso
function Test-Port {
    param($Port)
    try {
        $connection = New-Object System.Net.Sockets.TcpClient
        $connection.Connect("127.0.0.1", $Port)
        $connection.Close()
        return $true
    } catch {
        return $false
    }
}

# Verificar puertos
if (Test-Port $BackendPort) {
    Write-Host "⚠️ Puerto $BackendPort ya está en uso (Backend)" -ForegroundColor Yellow
} else {
    Write-Host "⚡ INICIANDO BACKEND (Puerto $BackendPort)..." -ForegroundColor Cyan
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$ProjectRoot'; & '.venv\Scripts\Activate.ps1'; python -m uvicorn backend.main:app --host 127.0.0.1 --port $BackendPort --reload" -WindowStyle Normal
}

Start-Sleep -Seconds 3

if (Test-Port $FrontendPort) {
    Write-Host "⚠️ Puerto $FrontendPort ya está en uso (Frontend)" -ForegroundColor Yellow  
} else {
    Write-Host "⚡ INICIANDO FRONTEND (Puerto $FrontendPort)..." -ForegroundColor Cyan
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$FrontendPath'; npm run dev" -WindowStyle Normal
}

Write-Host ""
Write-Host "✅ SISTEMA INICIADO CORRECTAMENTE" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 URLs del sistema:" -ForegroundColor White
Write-Host "   Backend API: http://127.0.0.1:$BackendPort" -ForegroundColor White
Write-Host "   Frontend Web: http://localhost:$FrontendPort" -ForegroundColor White
Write-Host ""

Write-Host "📱 Abriendo navegador en 5 segundos..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

Write-Host "⚡ Abriendo navegador..." -ForegroundColor Cyan
Start-Process "http://localhost:$FrontendPort"

Write-Host ""
Write-Host "🎯 SISTEMA LISTO PARA USAR" -ForegroundColor Green
Write-Host ""
Write-Host "Para detener el sistema:" -ForegroundColor White
Write-Host "- Cierra las ventanas de PowerShell del Backend y Frontend" -ForegroundColor White
Write-Host "- O presiona Ctrl+C en cada ventana" -ForegroundColor White
Write-Host ""

Read-Host "Presiona Enter para finalizar este script (los servicios seguirán ejecutándose)"