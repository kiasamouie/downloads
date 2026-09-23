#!/usr/bin/env bash
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

echo "==> Fixing ownership of $DIR (requires sudo)"
sudo chown -R kia:kia "$DIR"
sudo chmod 755 "$DIR"

echo "==> Installing system ffmpeg (requires sudo)"
sudo apt-get update -y
sudo apt-get install -y ffmpeg

echo "==> Creating Python virtual environment at $DIR/env"
if [ -x "$DIR/.py312/bin/python3.12" ]; then
    PY="$DIR/.py312/bin/python3.12"
else
    PY=python3
fi
"$PY" -m venv --clear env

echo "==> Installing/updating yt-dlp in the virtual environment"
env/bin/python -m pip install --upgrade pip
env/bin/python -m pip install --upgrade yt-dlp

echo
echo "==> Verification"
ffmpeg -version | head -n 1 || env/bin/ffmpeg -version | head -n 1
env/bin/python --version
env/bin/yt-dlp --version

echo
echo "Done. Use ./audio or ./video (see README.md)."
