#!/bin/sh

echo "🔧 Use NFT's"
python3 ./src/entrypoint/scripts/nfts.py

echo "🔧 Use DB migrations"
alembic -c alembic.ini upgrade head

echo "🔧 Start app"
PYTHONPATH=. uvicorn src.entrypoint.main:app --host 0.0.0.0 --port 9000 --reload