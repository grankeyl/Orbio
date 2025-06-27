#!/bin/sh

echo "🔧 Activate venv"
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
else
    echo "Virtual environment already exists."
fi
source venv/bin/activate

echo "🔧 Install dependencies"
pip install --no-cache-dir -r requirements.txt

# echo "🔧 Use NFT's"
# python3 ./src/entrypoint/scripts/nfts.py

echo "🔧 Use DB migrations"
# alembic revision --autogenerate -m "Initial migration"
alembic -c alembic.ini upgrade head

echo "🔧 Start app"
PYTHONPATH=. uvicorn src.entrypoint.main:app --host 0.0.0.0 --port 9000 --reload