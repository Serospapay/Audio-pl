@echo off
chcp 65001 >nul
title Audio Player - Встановлення

echo ========================================
echo   Audio Player - Встановлення залежностей
echo ========================================
echo.

REM Перевірка наявності Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ПОМИЛКА] Python не знайдено!
    echo Будь ласка, встановіть Python 3.8 або новіший.
    echo Завантажити: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo [OK] Python знайдено
python --version
echo.

echo Встановлення залежностей...
echo Це може зайняти кілька хвилин...
echo.

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo [ПОМИЛКА] Не вдалося встановити залежності!
    echo Перевірте підключення до інтернету та спробуйте ще раз.
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo [OK] Встановлення завершено успішно!
echo ========================================
echo.
echo Тепер ви можете запустити програму через run.bat
echo.
pause

