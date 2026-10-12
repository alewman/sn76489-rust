#!/usr/bin/env python
"""Every variant's data, one line each, as ``sn76489-tables`` prints this core's:
the name, the noise register's width and taps (as written and mirrored), stereo, the
low-period rule, and the sixteen levels by ``repr``. Run with the reference's
interpreter (rung 1)."""

from sn76489_python import VARIANTS

for variant in VARIANTS.values():
    print(
        variant.name.replace(" ", "_"),
        variant.lfsr_bits,
        f"{variant.white_noise_taps:#06x}",
        f"{variant.left_taps():#06x}",
        int(variant.stereo),
        int(variant.low_periods_hold_high),
        " ".join(repr(level) for level in variant.levels),
    )
