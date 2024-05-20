$PROJECT_DIR = (Get-Location).Path
$VENV_DIR = ".venv"
$REQUIREMENTS_FILE = "requirements.txt"
$APP_DIR = "$PROJECT_DIR\hrgame"

if (!(Test-Path -Path $VENV_DIR)) {
    python -m venv $VENV_DIR
}

& $VENV_DIR\Scripts\Activate.ps1

pip install -r $REQUIREMENTS_FILE

python $APP_DIR\manage.py migrate

python $APP_DIR\manage.py runserver
