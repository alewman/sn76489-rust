#!/usr/bin/env python
"""Seeded random conformance manifests: rung 5, where no fixed stream reaches.

    python scripts/random_manifests.py --count 128 --seed 1 --out DIR

Seed ``s`` makes the same manifest on every machine (Python's ``random.Random``,
version 2 seeding, is stable across versions). Each manifest picks one of the four
variants and a run of 200,000-2,000,000 input clocks, then fills it with:

* first, all four channels programmed to sound: tone periods from 2 to 1023 (and now
  and then 0 or 1, where the variants differ), attenuations 0-12, a noise setting;
* then writes at gaps drawn from one clock (the die's single data register, faster
  than any console) through tens of thousands, landing on every phase of the
  rotation: latch bytes for all eight registers, data bytes with bit 7 clear (whole
  values into a latched volume or noise register, high bits into a tone), noise
  rewrites that restart the register, the voices programmed again now and then;
* Game Gear stereo writes on every variant (the others must ignore them);
* the test bits now and then, mostly bit 0 for a few hundred clocks.

Standard library only. The files are rewritten on each run; ``--out`` is expected to
hold nothing else.
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

VARIANTS = ("ym7101", "sega-vdp", "game-gear", "sn76489an")


def voices(rng: random.Random, t: int, events: list[dict]) -> int:
    for channel in range(3):
        period = rng.choice((0, 1)) if rng.random() < 0.1 else rng.randrange(2, 1024)
        for data in (0x80 | channel << 5 | (period & 0x0F), (period >> 4) & 0x3F,
                     0x90 | channel << 5 | rng.randrange(13)):  # fmt: skip
            events.append({"t": t, "kind": "write", "data": data})
            t += rng.randrange(16, 400)
    for data in (0xE0 | rng.randrange(8), 0xF0 | rng.randrange(13)):
        events.append({"t": t, "kind": "write", "data": data})
        t += rng.randrange(16, 400)
    return t


def manifest(seed: int) -> dict:
    rng = random.Random(seed)
    variant = VARIANTS[seed % 4]
    clocks = rng.randrange(200_000, 2_000_001)
    events: list[dict] = []
    t = voices(rng, rng.randrange(0, 64), events)
    while True:
        roll = rng.random()
        gap = (
            rng.randrange(1, 5) if roll < 0.15
            else rng.randrange(5, 300) if roll < 0.75
            else rng.randrange(300, 30_000)
        )  # fmt: skip
        t += gap
        if t > clocks - 1000:
            break
        roll = rng.random()
        if roll < 0.40:  # a latch byte, any register
            data = 0x80 | rng.randrange(8) << 4 | rng.randrange(16)
        elif roll < 0.75:  # a data byte, bit 7 clear
            data = rng.randrange(0x80)
        elif roll < 0.85:  # a noise rewrite, which restarts the register
            data = 0xE0 | rng.randrange(8)
        elif roll < 0.90:
            t = voices(rng, t, events)
            continue
        elif roll < 0.96:
            events.append({"t": t, "kind": "stereo", "data": rng.randrange(256)})
            continue
        else:
            bits = 1 if rng.random() < 0.7 else rng.randrange(8)
            events.append({"t": t, "kind": "test", "data": bits})
            t += rng.randrange(1, 600)
            events.append({"t": t, "kind": "test", "data": 0})
            continue
        events.append({"t": t, "kind": "write", "data": data})
    # The voices and the test pulses can run past the end; the run covers them.
    clocks = max(clocks, events[-1]["t"] + 1000)
    return {
        "version": 1,
        "name": f"random-{seed}-{variant}",
        "variant": variant,
        "clocks": clocks,
        "events": events,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--count", type=int, default=128)
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    args.out.mkdir(parents=True, exist_ok=True)
    totals = {"clocks": 0, "write": 0, "stereo": 0, "test": 0}
    for seed in range(args.seed, args.seed + args.count):
        document = manifest(seed)
        (args.out / f"random-{seed:04d}.json").write_text(json.dumps(document), encoding="utf-8")
        totals["clocks"] += document["clocks"]
        for event in document["events"]:
            totals[event["kind"]] += 1
    print(
        f"{args.count} manifests from seed {args.seed}: {totals['clocks']:,} clocks, "
        f"{totals['write']:,} writes, {totals['stereo']:,} stereo, {totals['test']:,} test"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
