Write-Host "=== Ticket-System Server Setup ==="

# Arbeitsverzeichnis
$BASE_DIR = "$env:USERPROFILE\ticket-system"
New-Item -ItemType Directory -Force -Path $BASE_DIR
Set-Location $BASE_DIR

# Prüfen ob Git installiert ist
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Git nicht gefunden. Bitte installieren."
    exit 1
}

# Prüfen ob Python installiert ist
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Python nicht gefunden. Bitte Python 3.13 installieren."
    exit 1
}

# Repository klonen
Write-Host "📥 Klone Repository..."
git clone https://github.com/DEIN-USERNAME/DEIN-REPO.git
Set-Location DEIN-REPO

# Virtuelle Umgebung erstellen
Write-Host "🐍 Erstelle Python venv..."
python -m venv .venv
.\.venv\Scripts\activate

# Abhängigkeiten installieren
Write-Host "📦 Installiere Dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Ticket-System starten
Write-Host "🚀 Starte Ticket-System (Streamlit)..."
python -m streamlit run Ticket_System_Nano\src\app.py --server.address 0.0.0.0
