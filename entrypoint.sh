#!/bin/bash
PORT="${PORT:-8080}"
echo "Starting PathCraft AI Streamlit Dashboard on port $PORT..."
exec python -m streamlit run app.py \
    --server.port "$PORT" \
    --server.address "0.0.0.0" \
    --server.enableCORS false \
    --server.enableXsrfProtection false \
    --server.headless true
