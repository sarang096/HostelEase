# Activate virtual environment and run Flask app
Write-Host "Starting Hostel Management System..." -ForegroundColor Green
Write-Host "Activating virtual environment..." -ForegroundColor Yellow

# Activate virtual environment
& .\.venv\Scripts\Activate.ps1

Write-Host "Starting Flask server..." -ForegroundColor Yellow
Write-Host "Access the application at: http://localhost:3000" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Gray
Write-Host ""

# Run Flask app
python flask_app.py
