#!/usr/bin/env bash
# BranchOS Local Development Startup Script
# Activates venv, starts API backend and Streamlit dashboard

set -e

# Default ports
API_PORT="${1:-8000}"
DASHBOARD_PORT="${2:-8502}"

echo "🚀 BranchOS Local Development Startup"
echo "========================================"
echo ""

# Check if virtual environment exists
if [ ! -f ".venv/bin/activate" ]; then
    echo "❌ Virtual environment not found at .venv"
    echo ""
    echo "Please create it first:"
    echo "  python -m venv .venv"
    echo "  source .venv/bin/activate"
    echo "  pip install -r requirements.txt"
    exit 1
fi

echo "✅ Virtual environment found"

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

echo "✅ Virtual environment activated"
echo ""

# Check if required packages are installed
echo "🔍 Checking dependencies..."
if ! python -c "import uvicorn, streamlit, fastapi" 2>/dev/null; then
    echo "❌ Missing dependencies. Installing..."
    pip install -r requirements.txt
fi
echo "✅ Dependencies verified"
echo ""

# Function to cleanup background jobs on exit
cleanup() {
    echo ""
    echo "🛑 Stopping services..."
    if [ -n "$API_PID" ]; then
        kill $API_PID 2>/dev/null || true
    fi
    if [ -n "$DASHBOARD_PID" ]; then
        kill $DASHBOARD_PID 2>/dev/null || true
    fi
    echo "✅ Services stopped"
}

# Set trap to cleanup on script exit
trap cleanup EXIT INT TERM

# Start API backend in background
echo "🌐 Starting FastAPI backend on port $API_PORT..."
python -m uvicorn branchberg.app.main:app --reload --port "$API_PORT" > /tmp/branchberg-api.log 2>&1 &
API_PID=$!

# Wait a moment for API to start
sleep 3

# Check if API started successfully
if kill -0 $API_PID 2>/dev/null; then
    echo "✅ API backend started (PID: $API_PID)"
    echo "   URL: http://localhost:$API_PORT"
    echo "   Docs: http://localhost:$API_PORT/docs"
    echo "   Logs: /tmp/branchberg-api.log"
else
    echo "❌ API backend failed to start"
    cat /tmp/branchberg-api.log
    exit 1
fi

echo ""

# Start Streamlit dashboard in background
echo "📊 Starting Streamlit dashboard on port $DASHBOARD_PORT..."
streamlit run branchberg/dashboard/streamlit_app.py --server.port "$DASHBOARD_PORT" --server.headless true > /tmp/branchberg-dashboard.log 2>&1 &
DASHBOARD_PID=$!

# Wait a moment for dashboard to start
sleep 3

# Check if dashboard started successfully
if kill -0 $DASHBOARD_PID 2>/dev/null; then
    echo "✅ Dashboard started (PID: $DASHBOARD_PID)"
    echo "   URL: http://localhost:$DASHBOARD_PORT"
    echo "   Logs: /tmp/branchberg-dashboard.log"
else
    echo "❌ Dashboard failed to start"
    cat /tmp/branchberg-dashboard.log
    exit 1
fi

echo ""
echo "========================================"
echo "✨ All services running!"
echo ""
echo "📌 Quick Links:"
echo "   API:       http://localhost:$API_PORT"
echo "   API Docs:  http://localhost:$API_PORT/docs"
echo "   Dashboard: http://localhost:$DASHBOARD_PORT"
echo ""
echo "📝 Process IDs:"
echo "   API:       $API_PID"
echo "   Dashboard: $DASHBOARD_PID"
echo ""
echo "📋 Log Files:"
echo "   API:       /tmp/branchberg-api.log"
echo "   Dashboard: /tmp/branchberg-dashboard.log"
echo ""
echo "Press Ctrl+C to stop all services"
echo "========================================"

# Keep script running and wait for Ctrl+C
wait
