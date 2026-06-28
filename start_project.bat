@echo off
echo Dang khoi dong Backend va Frontend...

:: Khoi dong Backend trong cua so moi
start "Helicopter Backend (Port 8088)" cmd /k "cd /d d:\UIT\Research\Viettel\backend && venv\Scripts\activate && python -m uvicorn main:app --port 8088"

:: Khoi dong Frontend trong cua so moi
start "Helicopter Frontend (Port 3088)" cmd /k "cd /d d:\UIT\Research\Viettel\frontend && npm run dev -- --port 3088"

echo Backend va Frontend dang duoc khoi dong trong cac cua so rieng biet.
pause
