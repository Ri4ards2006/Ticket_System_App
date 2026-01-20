Write-Host "🎫 Ticket System Setup"
Write-Host "======================"
Write-Host "1️⃣ Nano (Streamlit, demo)"
Write-Host "2️⃣ Micro (Flask, lightweight)"
Write-Host "3️⃣ Native (Docker, enterprise)"
$version = Read-Host "👉 Choose version [1-3]"

$BASE_DIR = "$env:USERPROFILE\ticket-system"
New-Item -ItemType Directory -Force -Path $BASE_DIR | Out-Null
Set-Location $BASE_DIR

Write-Host "📥 Cloning repository..."
git clone https://github.com/DEIN-USERNAME/DEIN-REPO.git
Set-Location DEIN-REPO

if ($version -eq "1") {
    Write-Host "🚀 Starting NANO version"
    Set-Location Ticket_System_Nano
    python -m venv .venv
    .\.venv\Scripts\activate
    pip install --upgrade pip
    pip install -r requirements.txt
    python -m streamlit run src\app.py --server.address 0.0.0.0

} elseif ($version -eq "2") {
    Write-Host "⚙️ Starting MICRO version"
    Set-Location Ticket_System_Micro
    python -m venv .venv
    .\.venv\Scripts\activate
    pip install --upgrade pip
    pip install -r requirements.txt
    python app.py

} elseif ($version -eq "3") {
    Write-Host "🐳 Starting NATIVE version (Docker)"
    docker-compose up --build

} else {
    Write-Host "❌ Invalid selection"
}
