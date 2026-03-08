#!/bin/bash

# Navigate to project root and activate virtual environment
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

if [ -d "$PROJECT_ROOT/.venv" ]; then
    source "$PROJECT_ROOT/.venv/bin/activate"
fi

cd "$SCRIPT_DIR"
echo "Starting SeaWeed AI server..."
uvicorn app:app --reload --host 0.0.0.0 --port 8000
