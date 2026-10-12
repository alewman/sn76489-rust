//! `sn76489-samples <manifest.json>`: run a manifest and print `take_samples()`, one
//! `left right` line per sample, as `scripts/samples.py` prints the reference's, for
//! rung 1. The trace does not see the levels curves or the Game Gear's stereo
//! routing, which are data a port copies; this checks the copy, to the bit.

use std::io::{self, BufWriter, Write};
use std::process::ExitCode;

use sn76489_rust::conformance::{load_manifest, replay};

fn main() -> ExitCode {
    let args: Vec<String> = std::env::args().skip(1).collect();
    let [path] = args.as_slice() else {
        eprintln!("usage: sn76489-samples <manifest.json>");
        return ExitCode::from(2);
    };
    let manifest = match load_manifest(path) {
        Ok(manifest) => manifest,
        Err(error) => {
            eprintln!("error: {error}");
            return ExitCode::from(2);
        }
    };
    let mut chip = replay(&manifest, |_| Ok(())).expect("no output while running");
    let stdout = io::stdout();
    let mut out = BufWriter::new(stdout.lock());
    for (left, right) in chip.take_samples() {
        if writeln!(out, "{left:?} {right:?}").is_err() {
            return ExitCode::FAILURE;
        }
    }
    if out.flush().is_err() {
        return ExitCode::FAILURE;
    }
    ExitCode::SUCCESS
}
