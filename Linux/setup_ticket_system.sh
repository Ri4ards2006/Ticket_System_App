#!/bin/bash

echo "=== Ticket-System Server Setup ==="

BASE_DIR="$HOME/ticket-system"
mkdir -p "$BASE_DIR"
cd "$BASE_DIR" || exit 1

command -v git >/dev/null 2>&1 || { echo "Git fehlt"; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "Python fehlt"; exit 1; }

git clone https://github.com/DEIN-USERNAME/DEIN-REPO.git
cd DEIN-REPO || exit 1

python3 -m venv .venv
source .venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt

streamlit run Ticket_System_Nano/src/app.py --server.address 0.0.0.0
