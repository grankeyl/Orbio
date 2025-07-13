#!/bin/sh

echo "🔧 Activate venv"
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
else
    echo "Virtual environment already exists."
fi
. venv/bin/activate

echo "🔧 Install dependencies"
pip install --no-cache-dir -r requirements.txt

echo "🔧 Use NFT's"
python3 ./src/entrypoint/scripts/nfts.py

echo "🔧 Use DB migrations"
alembic revision --autogenerate -m "create tables"
alembic -c alembic.ini upgrade head

echo "🚀 Start deposit listener in background"
python3 ./src/entrypoint/scripts/deposit.py &

echo "🚀 Start main app"
PYTHONPATH=. uvicorn src.entrypoint.main:app --host 0.0.0.0 --port 9000 --reload