#!/usr/bin/env bash
# The reference's benchmark on this core: its stream (the seed-1 random walk of
# 40,000 latches) as a manifest, driven through run() by sn76489-bench.
# Usage: scripts/bench.sh [--seconds S] [--repeat N] [--variants a,b]
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
REF=${SN76489_PYTHON:-"$ROOT/external/sn76489-python"}
OUT="$ROOT/external/manifests/bench"
"$REF/.venv/bin/python" "$ROOT/scripts/stream_manifests.py" --reference "$REF" --bench --out "$OUT" > /dev/null
cargo build --release -q --manifest-path "$ROOT/Cargo.toml"
exec "$ROOT/target/release/sn76489-bench" "$OUT/bench-random-seed-1-40000-ym7101.json" "$@"
