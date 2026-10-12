# Build record

2026-10-11, one session, the day sn76489-python was extracted and both boards adopted
it, and the day after ym2612-rust.

## The transcription

`chip.py` is about 430 lines: a per-clock loop, two internal phases, a register
update and a mixer. It became `src/chip.rs` in one pass, function for function. The
decisions:

- **Integers.** Every register is a `u32` and the clock a `u64`. Nothing in the engine
  is negative, so no floor-division care was needed, unlike ym2612-rust's /IC
  arithmetic.
- **The curves.** `levels` is a tuple of floats in the reference. Here it is a
  `Levels` value: the ideal curve is computed by the reference's formula when asked
  for (`10f64.powf(-0.1 * step)` for Python's `10 ** (-0.1 * step)`, both the C
  library's `pow`), since a `const` cannot call `powf`. A host's own curve is
  `Levels::Table`.
- **The mixer** sums in the reference's order (`a + b + c + d` for mono, `0.0 +` each
  routed channel for stereo), so the floats are the same bits, and rung 1 checks that
  they are.

The first build reproduced all ten example traces and every rung's manifests on the
first run. No divergence between the two cores was found.

## Rung 1, widened

The reference's rung 1 is "the `levels` tables equal contract.md's". The trace sees
only attenuations, so the curves, and the Game Gear's stereo routing inside
`take_samples()`, are data a port copies unchecked; the reference's own mutation run
records that its examples miss a wrong curve and swapped sides. Here rung 1 prints
every variant's table from both cores (floats by Python's `repr`, which Rust's `{:?}`
matches: the shortest string that reads back as the same double) and compares
`take_samples()` over all ten examples to the bit. The seeded faults show it is needed:
the three faults the examples miss are exactly these, and rung 1 alone catches them.

## The ladder

| Rung | Result | Wall |
| --- | --- | --- |
| 1 | 4 variants, 10 examples' samples | seconds |
| 2 | 10 / 10 | seconds |
| 3 | 24 / 24, 2,990,093 clocks each variant | 3 s |
| 4 | 13 / 13, 630,272,479 clocks | 35 s |
| 5 | 128 / 128, 132,223,397 clocks | 16 s |

The reference wrote its traces on PyPy 7.3.20, 16 manifests at a time. Rung 5's first
run reported 126 of 128: two manifests put a test-bit release past the run's end,
which both cores refuse. The generator now extends the run to cover its last event.

## The seeded faults

14 faults, each one change in a copy of the repository (`scripts/seeded_faults.py`).
The examples catch 11; rung 1 catches the other 3 (the stereo sides and the two
curves), which rungs 3 and 5 cannot see by design.

## Tooling notes

- `cargo clippy` and the wasm build here need the rustup stable toolchain through
  `RUSTC`, as in ym2612-rust:
  `CARGO_TARGET_DIR=target/clippy RUSTC=$(rustup which --toolchain stable rustc) rustup run stable cargo clippy --release --all-targets -- -D warnings`
  and the same with `CARGO_TARGET_DIR=target/wasm ... cargo build --release --lib --target wasm32-unknown-unknown`.
  The default toolchain is an old nightly without the wasm target.
- `scripts/fetch_sn76489python.sh` clones the private reference over HTTPS by
  default. `SN76489_PYTHON_SOURCE=/data/emu/sn76489-python` clones the local one.
