#!/usr/bin/env bash
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR/.."
cd "$PROJECT_ROOT"

echo "==================================="
echo " Twitter -> Telegram bot: first-time setup"
echo "==================================="

# --- 1. virtual environment ---
if [ ! -f venv/bin/python ]; then
    echo "[1/4] Creating virtual environment..."
    python3 -m venv venv
else
    echo "[1/4] Virtual environment already exists."
fi

# --- 2. dependencies ---
echo "[2/4] Installing dependencies..."
venv/bin/python -m pip install -r requirements.txt --quiet

# --- 3. .env ---
if [ ! -f .env ]; then
    echo "[3/4] No .env found - creating one from .env.example."
    cp .env.example .env
    echo
    echo "  Fill in BOT_TOKEN, TARGET_CHAT_ID, and ALLOWED_USER_IDS in .env,"
    echo "  then run this script again."
    echo
    if [ -n "$EDITOR" ]; then
        "$EDITOR" .env
    elif command -v nano >/dev/null 2>&1; then
        nano .env
    else
        echo "  (no \$EDITOR set and nano not found - edit .env manually)"
    fi
    exit 0
else
    echo "[3/4] .env found."
fi

# --- 4. ffmpeg ---
if command -v ffmpeg >/dev/null 2>&1; then
    echo "[4/4] ffmpeg found."
else
    echo "[4/4] WARNING: ffmpeg not found on PATH."
    echo "  Video merging will fail without it. Install with your"
    echo "  distro's package manager, e.g.:"
    echo "    sudo apt install ffmpeg      (Debian/Ubuntu)"
    echo "    sudo pacman -S ffmpeg        (Arch/EndeavourOS)"
    echo "    sudo dnf install ffmpeg      (Fedora)"
fi

echo
echo "Setup complete. Starting the bot now..."
exec "$SCRIPT_DIR/run.sh"
