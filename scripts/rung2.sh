#!/usr/bin/env bash
# Rung 2: every example manifest in the reference's examples/conformance/ diffs
# identical.
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
REF=${SN76489_PYTHON:-"$ROOT/external/sn76489-python"}
exec "$ROOT/scripts/diff_all.sh" "$REF"/examples/conformance/*.json
