#!/usr/bin/env bash
# Rung 1: the data a port copies, which the trace does not see.
#  - Every variant's table (noise register width and taps, stereo, the low-period
#    rule, the sixteen levels) printed by this core and by the reference, equal to
#    the bit: floats are printed as Python's repr prints them.
#  - take_samples() over every example, equal to the bit: the levels curves and the
#    Game Gear's stereo routing, summed in the reference's order.
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
REF=${SN76489_PYTHON:-"$ROOT/external/sn76489-python"}
PY="$REF/.venv/bin/python"
[ -x "$PY" ] || { echo "no reference at $REF: run scripts/fetch_sn76489python.sh" >&2; exit 2; }
# BIN_DIR: another build to judge (scripts/seeded_faults.py uses it).
if [ -z "${BIN_DIR:-}" ]; then
    cargo build --release -q --manifest-path "$ROOT/Cargo.toml"
    BIN_DIR="$ROOT/target/release"
fi
status=0
if diff <("$BIN_DIR/sn76489-tables") <("$PY" "$ROOT/scripts/tables.py"); then
    echo "tables: $("$BIN_DIR/sn76489-tables" | wc -l) variants identical"
else
    echo "tables: DIFFERENT"; status=1
fi
for manifest in "$REF"/examples/conformance/*.json; do
    ours=$("$BIN_DIR/sn76489-samples" "$manifest" | sha256sum | cut -d' ' -f1)
    theirs=$("$PY" "$ROOT/scripts/samples.py" "$manifest" | sha256sum | cut -d' ' -f1)
    count=$("$BIN_DIR/sn76489-samples" "$manifest" | wc -l)
    if [ "$ours" = "$theirs" ]; then
        echo "samples $(basename "$manifest" .json): $count identical"
    else
        echo "samples $(basename "$manifest" .json): DIFFERENT"; status=1
    fi
done
exit $status
