# Voice RAG Bot - System Startup Script
# Starts FastAPI backend and Streamlit frontend

Write-Host "=================================="
Write-Host "Voice RAG Bot - System Startup"
Write-Host "=================================="
Write-Host ""

# Check if venv exists
if (-not (Test-Path "venv\Scripts\Activate.ps1")) {
    Write-Host "ERROR: Virtual environment not found!"
    Write-Host "Please run: python -m venv venv"
    exit 1
}

# Activate venv
Write-Host "[1/3] Activating virtual environment..."
& .\venv\Scripts\Activate.ps1

# Check if Qdrant is running
Write-Host "[2/3] Checking Qdrant connection..."
try {
    $response = Invoke-WebRequest -Uri "http://localhost:6333/health" -UseBasicParsing -TimeoutSec 2
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Qdrant is running on localhost:6333"
    }
} catch {
    Write-Host "⚠️  WARNING: Cannot connect to Qdrant on localhost:6333"
    Write-Host "   Make sure Docker is running and Qdrant container is active"
    Write-Host "   Run: docker run -p 6333:6333 qdrant/qdrant:latest"
}

Write-Host ""
Write-Host "[3/3] Starting services..."
Write-Host ""

# Start backend in a separate process
Write-Host "Starting FastAPI backend on http://localhost:8000"
$backendProcess = Start-Process -NoNewWindow -FilePath "python" -ArgumentList "backend/main.py" -PassThru
Start-Sleep -Seconds 3

# Start Streamlit
Write-Host "Starting Streamlit frontend on http://localhost:8501"
Write-Host ""
Write-Host "=================================="
Write-Host "Services started successfully!"
Write-Host "=================================="
Write-Host ""
Write-Host "Frontend URL: http://localhost:8501"
Write-Host "Backend API: http://localhost:8000"
Write-Host ""
Write-Host "Backend PID: $($backendProcess.Id)"
Write-Host ""
Write-Host "To stop the backend, run: Stop-Process -Id $($backendProcess.Id)"
Write-Host ""

# Start Streamlit
python -m streamlit run frontend/streamlit_app.py

# Cleanup
Write-Host ""
Write-Host "Stopping backend..."
Stop-Process -Id $backendProcess.Id -Force
Write-Host "Shutdown complete."
