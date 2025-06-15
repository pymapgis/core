# Flight Delay Now - Windows Entry Script
# Auto-opens browser on Windows as specified

Write-Host "🛫 Starting Flight Delay Now..." -ForegroundColor Green

# Check if Docker is running
try {
    docker version | Out-Null
    Write-Host "✅ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not running. Please start Docker Desktop." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Build the container if it doesn't exist
Write-Host "🔨 Building Flight Delay Now container..." -ForegroundColor Yellow
docker build -t flight-delay-now .

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to build container" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Stop any existing container
docker stop flight-delay-now 2>$null
docker rm flight-delay-now 2>$null

# Run the container
Write-Host "🚀 Starting Flight Delay Now on http://localhost:8000" -ForegroundColor Green
Start-Process "http://localhost:8000"

# Run container in foreground so user can see logs
docker run --name flight-delay-now -p 8000:8000 flight-delay-now

Write-Host "🛑 Flight Delay Now stopped" -ForegroundColor Yellow
Read-Host "Press Enter to exit"
