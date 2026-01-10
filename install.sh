#!/bin/bash
# Quick Install Script for RemoteSysMon

echo "🚀 RemoteSysMon Quick Install"
echo "=============================="
echo ""

# Check if running on Linux
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    echo "❌ This script is for Linux only"
    echo "   For Windows, install Python and PyQt6 manually"
    exit 1
fi

# Check Python version
echo "📌 Checking Python version..."
python_version=$(python3 --version 2>&1 | grep -oP '\d+\.\d+')
required_version="3.8"

if (( $(echo "$python_version >= $required_version" | bc -l) )); then
    echo "   ✅ Python $python_version found"
else
    echo "   ❌ Python $required_version or higher required"
    exit 1
fi

# Install system dependencies
echo ""
echo "📦 Installing system dependencies..."
if command -v apt &> /dev/null; then
    echo "   Detected Debian/Ubuntu"
    sudo apt update
    sudo apt install -y python3-pip adb
elif command -v pacman &> /dev/null; then
    echo "   Detected Arch Linux"
    sudo pacman -S --noconfirm python-pip android-tools
elif command -v dnf &> /dev/null; then
    echo "   Detected Fedora"
    sudo dnf install -y python3-pip android-tools
else
    echo "   ⚠️  Unsupported package manager - install ADB manually"
fi

# Install Python dependencies
echo ""
echo "📦 Installing Python dependencies..."
cd server
pip install -r requirements.txt --user

echo ""
echo "✅ Installation complete!"
echo ""
echo "📱 Next steps:"
echo "   1. Enable USB debugging on your Android device"
echo "   2. Connect your device via USB"
echo "   3. Run: sudo python3 main.py"
echo ""
echo "📖 See README_DESKTOP.md for more information"
