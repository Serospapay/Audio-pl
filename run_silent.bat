@echo off
REM Тихий запуск без виводу (для ярликів)
chcp 65001 >nul
python main.py
exit /b %errorlevel%

