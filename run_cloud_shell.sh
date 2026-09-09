#!/bin/bash
# ==============================================================================
# PathCraft AI - Google Cloud Shell Dual Service Launcher (FastAPI + Streamlit)
# ==============================================================================

# 1. Check API Key
if [ -z "$GOOGLE_API_KEY" ]; then
    echo "⚠️  WARNING: GOOGLE_API_KEY environment variable is not set."
    echo "   Please run: export GOOGLE_API_KEY='your_api_key_here'"
    echo "   (You can also enter your key directly in the Streamlit sidebar)."
    echo ""
fi

echo "================================================================="
echo "🚀 Starting PathCraft AI Services in Cloud Shell..."
echo "================================================================="

# 2. Start FastAPI REST Backend in background on Port 8000
echo "⚡ [1/2] Starting FastAPI Backend on http://0.0.0.0:8000 (Swagger: http://0.0.0.0:8000/docs)..."
uvicorn api_server:app --host 0.0.0.0 --port 8000 &
FASTAPI_PID=$!

# Trap Ctrl+C to kill FastAPI on exit
trap "echo 'Stopping services...'; kill $FASTAPI_PID; exit" SIGINT SIGTERM

# Give FastAPI a moment to start
sleep 2

# 3. Start Streamlit UI on Port 8080 (Cloud Shell default Web Preview Port) or 8501
STREAMLIT_PORT="${PORT:-8080}"
echo "🖥️  [2/2] Starting Streamlit Web Dashboard on http://0.0.0.0:$STREAMLIT_PORT..."
echo "   👉 Open Google Cloud Shell 'Web Preview' button -> Preview on port $STREAMLIT_PORT"
echo "================================================================="

python -m streamlit run app.py \
    --server.port "$STREAMLIT_PORT" \
    --server.address "0.0.0.0" \
    --server.enableCORS false \
    --server.enableXsrfProtection false \
    --server.headless true
