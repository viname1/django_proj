@echo off
set PROJECT_DIR=%cd%
set VENV_DIR=.venv
set REQUIREMENTS_FILE=requirements.txt
set APP_DIR= %PROJECT_DIR%\hrgame

if not exist %VENV_DIR% (
    python -m venv %VENV_DIR%
)

call %VENV_DIR%\Scripts\activate.bat

pip install -r %REQUIREMENTS_FILE%

python %APP_DIR%\manage.py migrate

python %APP_DIR%\manage.py runserver
