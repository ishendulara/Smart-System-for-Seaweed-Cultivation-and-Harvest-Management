#!/usr/bin/env python3
"""
Wrapper script to run the FastAPI app.
Usage: python run_server.py
"""
import subprocess
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent

print("Starting SeaWeed AI server...")
subprocess.run([
    sys.executable, "-m", "uvicorn",
    "app:app", "--reload",
    "--host", "0.0.0.0",
    "--port", "8000"
], cwd=str(BACKEND_DIR))
