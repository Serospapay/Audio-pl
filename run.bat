@echo off
chcp 65001 >nul
title Audio Player

echo ========================================
echo      Audio Player - Запуск
echo ========================================
echo.

REM Перевірка наявності Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ПОМИЛКА] Python не знайдено!
    echo Будь ласка, встановіть Python 3.8 або новіший.
    echo.
    pause
    exit /b 1
)

echo [OK] Python знайдено
echo.

REM Перевірка наявності залежностей
echo Перевірка залежностей...
python -c "import PyQt6" >nul 2>&1
if errorlevel 1 (
    echo [УВАГА] Залежності не встановлені!
    echo Встановлення залежностей...
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo [ПОМИЛКА] Не вдалося встановити залежності!
        pause
        exit /b 1
    )
    echo [OK] Залежності встановлено
    echo.
)

echo Запуск програми...
echo.

REM Запуск програми
python main.py

REM Обробка помилок
if errorlevel 1 (
    echo.
    echo [ПОМИЛКА] Програма завершилася з помилкою!
    echo Перевірте логи в папці logs/
    echo.
    pause
    exit /b 1
)

exit /b 0

