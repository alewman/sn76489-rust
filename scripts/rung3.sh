#!/usr/bin/env bash
# Rung 3: the six synthetic streams of the reference's scripts/run_psg_compare.py, as
# manifests in all four variants, every input clock. Equal to the reference here and
# the reference equal to Nuked-PSG on the same streams (as the YM7101) compose.
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
REF=${SN76489_PYTHON:-"$ROOT/external/sn76489-python"}
OUT=${1:-"$ROOT/external/manifests/synthetic"}
"$REF/.venv/bin/python" "$ROOT/scripts/stream_manifests.py" --reference "$REF" --synthetic --out "$OUT"
exec "$ROOT/scripts/diff_all.sh" "$OUT"/*.json
