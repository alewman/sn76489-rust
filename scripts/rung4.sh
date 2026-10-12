#!/usr/bin/env bash
# Rung 4: the writes the boards' PSGs received running cartridges (five Mega Drive,
# five Master System, two Game Gear, one SG-1000), exported by the reference's
# scripts/export_board_streams.py, each in its machine's variant. Derived from ROMs,
# so local only: pass the directory they were exported to.
# Usage: scripts/rung4.sh [streams dir, default ../sn76489-python/validation/streams]
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
REF=${SN76489_PYTHON:-"$ROOT/external/sn76489-python"}
STREAMS=${1:-"$ROOT/../sn76489-python/validation/streams"}
OUT="$ROOT/external/manifests/board"
"$REF/.venv/bin/python" "$ROOT/scripts/stream_manifests.py" --reference "$REF" --streams "$STREAMS" --out "$OUT"
exec "$ROOT/scripts/diff_all.sh" "$OUT"/*.json
