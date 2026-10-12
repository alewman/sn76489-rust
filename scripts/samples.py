#!/usr/bin/env python
"""Run a manifest on the reference and print ``take_samples()``, one ``left right``
line per sample by ``repr``, as ``sn76489-samples`` prints this core's (rung 1).
The events are applied as the reference's ``trace_manifest`` applies them."""

import sys

from sn76489_python import SN76489
from sn76489_python.conformance import VARIANTS, load_manifest

manifest = load_manifest(sys.argv[1])
chip = SN76489(VARIANTS[manifest.variant])
apply = {"write": chip.write, "stereo": chip.write_stereo, "test": chip.write_test}
for event in manifest.events:
    chip.run(event.t - chip.clock)
    apply[event.kind](event.data)
chip.run(manifest.clocks - chip.clock)
for left, right in chip.take_samples():
    print(repr(left), repr(right))
