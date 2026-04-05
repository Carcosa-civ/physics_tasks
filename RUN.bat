@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion
title Запуск Django проекта "Физика: Задачи и учебные материалы"
echo ====================================================
echo    Запуск учебного проекта по физике
echo ====================================================
echo.

cd /d "%~dp0"

if not exist "venv\Scripts\python.exe" (
    echo Ошибка: Виртуальное окружение не найдено в папке venv.
    echo Создайте его командой: python -m venv venv
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
echo Выполнение миграций...
python manage.py makemigrations
python manage.py migrate

echo.
echo Загрузка тестовых данных (статьи, задачи, контрольные)...
python manage.py load_test_data

echo.
echo Проверка суперпользователя...
set "tmp_script=%temp%\check_admin.py"
(
echo import os, sys
echo import django
echo os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'physics_tasks.settings')
echo django.setup()
echo from django.contrib.auth.models import User
echo exists = User.objects.filter(is_superuser=True).exists()
echo sys.stdout.write('1' if exists else '0')
) > "%tmp_script%"

for /f %%i in ('python "%tmp_script%"') do set ADMIN_EXISTS=%%i
del "%tmp_script%"

if "%ADMIN_EXISTS%"=="1" (
    echo Суперпользователь уже существует.
    set /p CHOICE="Хотите создать дополнительного суперпользователя? (y/n): "
    if /i "!CHOICE!"=="y" (
        python manage.py createsuperuser
    ) else (
        echo Пропуск создания.
    )
) else (
    echo Суперпользователь не найден.
    set /p CHOICE="Создать суперпользователя сейчас? (y/n): "
    if /i "!CHOICE!"=="y" (
        python manage.py createsuperuser
    ) else (
        echo Вы можете создать позже командой: python manage.py createsuperuser
    )
)

echo.
echo Запуск сервера разработки...
echo Сервер доступен: http://127.0.0.1:8000
echo Для остановки нажмите Ctrl+C
echo ====================================================
python manage.py runserver

pause
endlocal