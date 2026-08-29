# JCET CampusIQ — Unified Local Development Launcher
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  JCET CampusIQ — Intelligent Campus Information System   " -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host ""

$RootPath = $PSScriptRoot
$VenvPython = Join-Path $RootPath ".venv\Scripts\python.exe"

if (-not (Test-Path $VenvPython)) {
    Write-Host "[ERROR] Python virtual environment not found at .venv" -ForegroundColor Red
    exit 1
}

Write-Host "[1/3] Verifying database connectivity..." -ForegroundColor Yellow
& $VenvPython (Join-Path $RootPath "backend\scripts\verify_database.py")
if ($LASTEXITCODE -ne 0) {
    Write-Host "[WARNING] Database connection issue detected. Proceeding anyway..." -ForegroundColor Yellow
} else {
    Write-Host "[OK] Database connected & pgvector extension enabled." -ForegroundColor Green
}

Write-Host ""
Write-Host "[2/3] Launching FastAPI backend on http://localhost:8000 ..." -ForegroundColor Cyan
$BackendJob = Start-Process -FilePath $VenvPython -ArgumentList "-m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload" -WorkingDirectory (Join-Path $RootPath "backend") -PassThru

Write-Host "[3/3] Launching Vite frontend on http://localhost:5173 ..." -ForegroundColor Cyan
$FrontendJob = Start-Process -FilePath "npm.cmd" -ArgumentList "run dev -- --host" -WorkingDirectory (Join-Path $RootPath "frontend") -PassThru

Write-Host ""
Write-Host "==========================================================" -ForegroundColor Green
Write-Host "  JCET CampusIQ is running locally!                       " -ForegroundColor Green
Write-Host "  - Frontend: http://localhost:5173                       " -ForegroundColor White
Write-Host "  - Backend:  http://localhost:8000                       " -ForegroundColor White
Write-Host "  - API Docs: http://localhost:8000/docs                  " -ForegroundColor White
Write-Host "==========================================================" -ForegroundColor Green
Write-Host "Press Ctrl+C or close this terminal to stop both servers." -ForegroundColor Gray

# Trap exit to cleanup background jobs
try {
    while ($true) {
        Start-Sleep -Seconds 2
        if ($BackendJob.HasExited) {
            Write-Host "[Backend process exited]" -ForegroundColor Red
            break
        }
        if ($FrontendJob.HasExited) {
            Write-Host "[Frontend process exited]" -ForegroundColor Red
            break
        }
    }
} finally {
    Write-Host "Stopping servers..." -ForegroundColor Yellow
    if ($BackendJob -and -not $BackendJob.HasExited) { Stop-Process -Id $BackendJob.Id -Force -ErrorAction SilentlyContinue }
    if ($FrontendJob -and -not $FrontendJob.HasExited) { Stop-Process -Id $FrontendJob.Id -Force -ErrorAction SilentlyContinue }
}
