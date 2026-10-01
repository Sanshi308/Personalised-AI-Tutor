@echo off
echo Starting Vector Tutor backend...
start "Vector Tutor Backend" cmd /k "cd backend && .venv\Scripts\activate && uvicorn main:app --reload --port 8000"
timeout /t 3 >nul
echo Starting Vector Tutor frontend...
start "Vector Tutor Frontend" cmd /k "cd frontend && npm run dev"
echo.
echo Open http://localhost:3000
pause
