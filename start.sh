#!/bin/bash
PROJECT_DIR=$(pwd)
VENV_DIR=".venv"
REQUIREMENTS_FILE="requirements.txt"
APP_DIR="$PROJECT_DIR/hrgame"

if [ ! -d "$VENV_DIR" ]; then
    python -m venv $VENV_DIR
fi

source $VENV_DIR/bin/activate

pip install -r $REQUIREMENTS_FILE

python $APP_DIR/manage.py migrate

python $APP_DIR/manage.py runserver
