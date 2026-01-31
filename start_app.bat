@echo off
echo Iniciando Conversor de Curriculo para PDF...
echo.
echo Abra o navegador em: http://127.0.0.1:5050
echo.
timeout /t 2 /nobreak > nul
start http://127.0.0.1:5050
python app.py
pause
