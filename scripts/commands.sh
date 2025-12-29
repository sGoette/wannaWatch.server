# Remove old venv (optional)
rm -rf .venv

# Create new venv using Python 3.14
python3.14 -m venv .venv

# Start in dev mode

cd backend
python3.14 -m venv .venv
source .venv/bin/activate

uvicorn app.main:app --reload

# macOS / Linux
source .venv/bin/activate

# Windows PowerShell
.venv\Scripts\Activate.ps1


# Setup
brew install python
python3.14 -m venv .venv
source .venv/bin/activate
pip install fastapi uvicorn watchdog
