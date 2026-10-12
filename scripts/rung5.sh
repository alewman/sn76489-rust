#!/usr/bin/env bash
# Rung 5: seeded random manifests -- writes one clock to thousands apart, every
# register, noise restarts, Game Gear stereo writes on every variant, the test bits
# -- in all four variants, where no fixed stream reaches. Beyond the reference's
# own ladder, which stops at rung 4.
# Usage: scripts/rung5.sh [count, default 128] [first seed, default 1]
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
OUT="$ROOT/external/manifests/random"
python3 "$ROOT/scripts/random_manifests.py" --count "${1:-128}" --seed "${2:-1}" --out "$OUT"
exec "$ROOT/scripts/diff_all.sh" "$OUT"/*.json
