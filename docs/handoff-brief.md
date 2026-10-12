# The request and the plan

## The request

2026-10-11, after ym2612-rust and ym2612-rust-fast: "we are going to publish, open the
ym2612-python PR, then the PSG".

The context: the megadrive-rust plan's step 3 was "decide the PSG". It was decided
the same day in another session. The PSG became a core of its own, sn76489-python,
folded from megadrive-python's engine and sms-python's variant table, and both boards
adopted it (megadrive-python #4, sms-python #1). So "the PSG", for a Rust Mega Drive
board, is this transcription: the last chip core the board needs in Rust, after
m68000-rust, z80-rust and ym2612-rust.

## The plan, read from the family's shape

The shape is ym2612-rust's: a transcription of the reference, module for module and
function for function, with the reference's names, comments and citations, proven
equivalent through the reference's conformance kit, and nothing redesigned.

1. `src/chip.rs` from `chip.py`, `src/conformance.rs` from `conformance.py` (the
   manifest reader and the trace writer; the diff stays the reference's).
2. The ladder is the reference's own (`docs/conformance.md`, "Certification ladder for
   a port"), with rung 1 widened and a rung 5 added:

   | Rung | What |
   | --- | --- |
   | 1 | The variant tables and the `levels` curves equal the reference's, and so does `take_samples()` over every example |
   | 2 | Every example in `examples/conformance/` diffs identical |
   | 3 | The six synthetic streams of `scripts/run_psg_compare.py` as manifests |
   | 4 | The exported board streams (scripts/export_board_streams.py) as manifests |
   | 5 | Seeded random manifests with stereo and test events, all four variants |

3. A gate that cannot fail proves nothing: seeded faults in this core must fail the
   rungs.
4. Speed measured as the reference's `benchmarks/bench.py` measures it.
5. Constraints: never copy GPL code (Nuked-PSG is cited through the reference, never
   read into this one); never commit anything derived from ROMs (the board streams'
   manifests stay in `external/`, ignored); a private GitHub repository and a push
   only when the owner asks.
