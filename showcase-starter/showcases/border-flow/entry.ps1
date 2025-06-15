# Border Flow Now - Windows Auto-Launch Script
# This script automatically opens the demo in your default browser

Write-Host "🚀 Starting Border Flow Now..." -ForegroundColor Green

# Wait for the server to start
Write-Host "⏳ Waiting for server to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

# Check if server is responding
$maxAttempts = 10
$attempt = 0
$serverReady = $false

while ($attempt -lt $maxAttempts -and -not $serverReady) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 2 -UseBasicParsing
        if ($response.StatusCode -eq 200) {
            $serverReady = $true
            Write-Host "✅ Server is ready!" -ForegroundColor Green
        }
    }
    catch {
        $attempt++
        Write-Host "⏳ Attempt $attempt/$maxAttempts - Server not ready yet..." -ForegroundColor Yellow
        Start-Sleep -Seconds 2
    }
}

if ($serverReady) {
    # Open the demo in default browser
    Write-Host "🌐 Opening Border Flow Now in your browser..." -ForegroundColor Green
    Start-Process "http://localhost:8000"
    
    Write-Host ""
    Write-Host "🎉 Border Flow Now is now running!" -ForegroundColor Green
    Write-Host "📍 URL: http://localhost:8000" -ForegroundColor Cyan
    Write-Host "🔍 Health Check: http://localhost:8000/health" -ForegroundColor Cyan
    Write-Host "📊 API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
} else {
    Write-Host "❌ Server failed to start after $maxAttempts attempts" -ForegroundColor Red
    Write-Host "💡 Try running manually: uvicorn app:app --host 0.0.0.0 --port 8000" -ForegroundColor Yellow
}
