#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

if [ ! -d ".venv-build" ]; then
    python3 -m venv .venv-build
fi

source .venv-build/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

python -m PyInstaller \
    --name VITCapstoneMatcher \
    --onefile \
    --clean \
    --add-data "app.py:." \
    --collect-data streamlit \
    --collect-all jobspy \
    --collect-all tls_client \
    --hidden-import jobspy \
    --hidden-import tls_client \
    --exclude-module PyQt5 \
    --exclude-module PySide6 \
    --exclude-module PyQt6 \
    --exclude-module matplotlib \
    --exclude-module torch \
    --exclude-module scipy \
    --exclude-module pygame \
    --exclude-module pygame_gui \
    --exclude-module IPython \
    launcher.py

chmod +x "$PROJECT_ROOT/dist/VITCapstoneMatcher"
echo ""
echo "macOS executable created at: $PROJECT_ROOT/dist/VITCapstoneMatcher"
