#!/usr/bin/env bash
# Check out the sn76489-python reference at the pinned commit and install it into a
# virtual environment, so the rung 1-5 checks run against exactly that core and kit.
# Usage: scripts/fetch_sn76489python.sh [destination]
# SN76489_PYTHON_SOURCE overrides where it is cloned from (a local clone will do).
set -euo pipefail
COMMIT=${SN76489_PYTHON_COMMIT:-9ed3b85a333191caa662edfcaf7a7b3167b95476}
SOURCE=${SN76489_PYTHON_SOURCE:-https://github.com/alewman/sn76489-python.git}
DEST=${1:-"$(dirname "$0")/../external/sn76489-python"}
PYTHON=${PYTHON:-python3}
if [ ! -d "$DEST/.git" ]; then
    git clone -q "$SOURCE" "$DEST"
fi
git -C "$DEST" fetch -q origin
git -C "$DEST" checkout -q --detach "$COMMIT"
if [ ! -x "$DEST/.venv/bin/python" ]; then
    "$PYTHON" -m venv "$DEST/.venv"
fi
"$DEST/.venv/bin/python" -m pip install -q -e "$DEST"
echo "sn76489-python at $(git -C "$DEST" rev-parse --short HEAD) installed in $DEST/.venv"
