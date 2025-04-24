Write-Host "Starting CursorDraw..." -ForegroundColor Cyan

# Check if Python is available
try {
    python --version | Out-Null
} catch {
    Write-Host "Error: Python not found. Please install Python 3.6 or higher." -ForegroundColor Red
    exit 1
}

# Check for pygame
try {
    python -c "import pygame" 2>$null
} catch {
    Write-Host "Installing pygame..." -ForegroundColor Yellow
    python -m pip install pygame
}

# Create data directory if it doesn't exist
if (-not (Test-Path -Path "data")) {
    New-Item -ItemType Directory -Path "data" | Out-Null
    Write-Host "Created data directory" -ForegroundColor Green
}

# Run the game
python run.py

Write-Host "Game closed." -ForegroundColor Cyan 