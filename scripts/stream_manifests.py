#!/usr/bin/env python
"""Write the reference's PSG streams as conformance manifests.

    python scripts/stream_manifests.py --reference external/sn76489-python --synthetic --out DIR
    python scripts/stream_manifests.py --reference ... --streams ../sn76489-python/validation/streams --out DIR

A stream is the reference's ``(clock, data)`` list (``scripts/run_psg_compare.py``).
Its ``compare`` writes each byte when the chip has run exactly ``clock`` input clocks
from power-on, then runs to ``--tail`` clocks past the last write (32,000, its
default). The manifest does the same, so a trace identical to the reference's here
is the run the reference compared with Nuked-PSG, clock for clock.

The synthetic streams are written in all four variants: the reference compared them
as the YM7101, and the other three share its engine and differ in data, which these
runs exercise over the same writes. A board stream is written in its own machine's
variant (its exported metadata names the machine).

Run with the reference's interpreter: it imports the reference's scripts. Board
streams are derived from ROMs, so their manifests stay local like the streams.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

TAIL = 16 * 2000
VARIANTS = ("ym7101", "sega-vdp", "game-gear", "sn76489an")
MACHINE_VARIANT = {
    "genesis": "ym7101",
    "sms2": "sega-vdp",
    "sms1": "sega-vdp",
    "gamegear": "game-gear",
    "sg1000": "sn76489an",
}


def slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def write(out: Path, name: str, events: list[tuple[int, int]], variants, tail: int) -> int:
    clocks = (events[-1][0] if events else 0) + tail
    for variant in variants:
        manifest = {
            "version": 1,
            "name": f"{name}-{variant}",
            "variant": variant,
            "clocks": clocks,
            "events": [{"t": clock, "kind": "write", "data": data} for clock, data in events],
        }
        (out / f"{name}-{variant}.json").write_text(json.dumps(manifest), encoding="utf-8")
    return clocks


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--synthetic", action="store_true", help="the six synthetic streams")
    parser.add_argument("--streams", type=Path, help="a directory of exported board streams")
    parser.add_argument("--tail", type=int, default=TAIL)
    parser.add_argument(
        "--bench",
        action="store_true",
        help="the benchmark's stream: the seed-1 random walk, 40,000 latches (benchmarks/bench.py)",
    )
    args = parser.parse_args(argv)
    sys.path.insert(0, str(args.reference / "scripts"))
    import referees
    import run_psg_compare as psg

    args.out.mkdir(parents=True, exist_ok=True)
    streams: list[tuple[str, list[tuple[int, int]], tuple[str, ...]]] = []
    if args.synthetic:
        streams += [
            (name, events, VARIANTS)
            for name, events in (
                ("random-seed-1", psg.stream_random(1, 3000)),
                ("random-seed-2", psg.stream_random(2, 3000)),
                ("dense-seed-3", psg.stream_dense(3, 6000)),
                ("every-tone-period", psg.stream_tones()),
                ("every-noise-setting", psg.stream_noise()),
                ("every-attenuation", psg.stream_volumes()),
            )
        ]
    if args.bench:
        streams.append(("bench-random-seed-1-40000", psg.stream_random(1, 40_000), ("ym7101",)))
    if args.streams:
        files = sorted(args.streams.glob("*.bin"))
        if not files:
            print(f"{args.streams}: no exported streams (scripts/export_board_streams.py)")
            return 1
        for path in files:
            meta = json.loads(path.with_suffix(".json").read_text())
            variant = MACHINE_VARIANT[meta["machine"]]
            streams.append((slug(path.stem), referees.read_events(path), (variant,)))
    total = 0
    for name, events, variants in streams:
        clocks = write(args.out, name, events, variants, args.tail)
        total += clocks * len(variants)
        print(f"{name}: {len(events):,} writes, {clocks:,} clocks, {', '.join(variants)}")
    print(f"{len(streams)} streams, {total:,} clocks in all, in {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
