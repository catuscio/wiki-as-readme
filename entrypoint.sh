#!/bin/bash
set -e

echo "Starting API server..."
gunicorn -k uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --workers 1 \
    --access-logfile - \
    --error-logfile - \
    src.server:app &

echo "Waiting for API to initialize..."
sleep 5

echo "Starting Streamlit app..."
streamlit run src/app.py --server.address=0.0.0.0 --server.port=8501
