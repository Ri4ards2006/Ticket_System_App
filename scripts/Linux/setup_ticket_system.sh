#!/bin/bash

echo "🎫 Ticket System Setup"
echo "======================"
echo "1️⃣ Nano (Streamlit, demo)"
echo "2️⃣ Micro (Flask, lightweight)"
echo "3️⃣ Native (Docker, enterprise)"
read -p "👉 Choose version [1-3]: " VERSION

BASE_DIR="$HOME/ticket-system"
mkdir -p "$BASE_DIR"
cd "$BASE_DIR" || exit 1

echo "📥 Cloning repository..."
git clone https://github.com/Ri4ards2006/Ticket_System_App.git
cd DEIN-REPO || exit 1

if [ "$VERSION" == "1" ]; then
    echo "🚀 Starting NANO version"
    cd Ticket_System_Nano || exit 1
    python3 -m venv .venv
    source .venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    streamlit run src/app.py --server.address 0.0.0.0

elif [ "$VERSION" == "2" ]; then
    echo "⚙️ Starting MICRO version"
    cd Ticket_System_Micro || exit 1
    python3 -m venv .venv
    source .venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    python app.py

elif [ "$VERSION" == "3" ]; then
    echo "🐳 Starting NATIVE version (Docker)"
    docker-compose up --build

else
    echo "❌ Invalid selection"
    exit 1
fi
