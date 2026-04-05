@echo off
chcp 65001 > nul
title Запуск pylint для проекта Physics Tasks
echo ====================================================
echo    Проверка кода с помощью pylint
echo ====================================================
echo.

cd /d "%~dp0"

if not exist "venv\Scripts\python.exe" (
    echo Ошибка: Виртуальное окружение не найдено.
    pause
    exit /b 1
)

echo Активация виртуального окружения...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo Не удалось активировать окружение
    pause
    exit /b 1
)

echo.
echo Проверка наличия pylint и pylint-django...
python -m pip show pylint > nul 2>&1
if errorlevel 1 (
    echo Установка pylint...
    python -m pip install pylint pylint-django
)

echo.
echo Запуск pylint с плагином django...
python -m pylint --rcfile=.pylintrc core

echo.
echo ====================================================
echo Проверка завершена.
pause