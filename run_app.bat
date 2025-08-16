@echo off
:: Path: C:\Users\Msi\Desktop\investmentapp\run_app.bat
cd C:\Users\Msi\Desktop\investmentapp
set PYTHONPATH=%CD%
call C:\Users\Msi\Desktop\investmentapp\venv\Scripts\activate
python -m src.core.main
pause