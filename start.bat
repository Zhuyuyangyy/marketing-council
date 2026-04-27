@echo off
cd /d "%~dp0backend"
echo Installing dependencies...
pip install -r requirements.txt -q
echo.
echo Starting MarketingCouncil on port 8009...
python -m uvicorn app.main:app --host 0.0.0.0 --port 8009 --reload
