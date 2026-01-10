#!/bin/bash
# Quick start script for RemoteSysMon Desktop App

cd "$(dirname "$0")"

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "   Run: python3 -m venv venv && venv/bin/pip install PyQt6"
    exit 1
fi

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "⚠️  WARNING: Not running as root - CPU power monitoring unavailable"
    echo "   Run with: sudo ./run.sh"
    echo ""
fi

# Run the app
echo "🚀 Starting RemoteSysMon Desktop App..."
venv/bin/python3 main.py
