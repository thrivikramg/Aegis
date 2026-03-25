# AEGIS: AI-Enabled Guardrail Inspection System (Modern Portal)

$host.UI.RawUI.WindowTitle = "AEGIS - Modern Security Console"
Clear-Host

Write-Host "🛡️  AEGIS AI SECURITY FRAMEWORK" -ForegroundColor Cyan
Write-Host "Initializing Professional Modern Portal..." -ForegroundColor Magenta

# 1. Start the FastAPI Research API in a separate job
Write-Host "`n[1/3] Starting Phoenix Research API (Backend)..." -ForegroundColor Yellow
$BackendJob = Start-Job -ScriptBlock {
    cd "c:\Projects\Red-team\SentinelLLM"
    python -m uvicorn api.server:app --host 127.0.0.1 --port 8000
}

# 2. Check if jobs are running
Start-Sleep -Seconds 3
$Status = Get-Job -Id $BackendJob.Id
if ($Status.State -eq "Running") {
    Write-Host "✅ Backend API operational at http://localhost:8000" -ForegroundColor Green
} else {
    Write-Host "❌ Backend API failed to start. Check logs." -ForegroundColor Red
}

# 3. Launch the Next.js Frontend
Write-Host "`n[2/3] Launching AEGIS Modern Portal (Frontend)..." -ForegroundColor Yellow
Set-Location "c:\Projects\Red-team\SentinelLLM\aegis-portal"
Write-Host "🚀 Running 'npm run dev' with ExecutionPolicy Bypass..." -ForegroundColor Cyan
powershell -ExecutionPolicy Bypass -Command "npm run dev"

# Cleanup on exit
Stop-Job -Id $BackendJob.Id
Write-Host "`n🛑 AEGIS Components Terminated." -ForegroundColor Red
