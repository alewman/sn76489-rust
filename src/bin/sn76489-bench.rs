//! `sn76489-bench [--seconds S] [--repeat N] [--variants a,b] <manifest.json>`: input
//! clocks per second and the fraction of real time, measured as the reference's
//! `benchmarks/bench.py` measures it.
//!
//! The manifest's writes are driven through `run()` as a board drives the chip --
//! run to each write, write, and at the end take the samples -- for its first
//! `--seconds` of emulated time, in each of `--variants` (the YM7101 and the Game
//! Gear by default, the reference's pair). `scripts/bench.sh` makes the workload, the
//! reference's stream: the seed-1 random walk of 40,000 latches. Real time is
//! 3,579,545 input clocks a second (NTSC). Reports the best of `--repeat` runs, since
//! the machine is shared.

use std::hint::black_box;
use std::process::ExitCode;
use std::time::Instant;

use sn76489_rust::conformance::{load_manifest, variant, Kind, Manifest};
use sn76489_rust::{PSGVariant, SN76489};

const REAL_TIME: f64 = 3_579_545.0;

fn run(manifest: &Manifest, clocks: u64, variant: PSGVariant) -> f64 {
    let mut chip = SN76489::new(variant);
    let started = Instant::now();
    for event in &manifest.events {
        if event.t >= clocks {
            break;
        }
        if event.kind == Kind::Write {
            chip.run(event.t - chip.clock);
            chip.write(event.data);
        }
    }
    chip.run(clocks - chip.clock);
    black_box(chip.take_samples());
    started.elapsed().as_secs_f64()
}

fn main() -> ExitCode {
    let mut args: Vec<String> = std::env::args().skip(1).collect();
    let mut take = |name: &str| -> Option<String> {
        let i = args.iter().position(|a| a == name)?;
        let value = args.get(i + 1).cloned();
        args.drain(i..(i + 2).min(args.len()));
        value
    };
    let seconds: f64 = take("--seconds")
        .and_then(|v| v.parse().ok())
        .unwrap_or(2.0);
    let repeat: usize = take("--repeat").and_then(|v| v.parse().ok()).unwrap_or(10);
    let names = take("--variants").unwrap_or_else(|| "ym7101,game-gear".into());
    let variants: Option<Vec<PSGVariant>> = names.split(',').map(variant).collect();
    let (Some(variants), [path]) = (variants, args.as_slice()) else {
        eprintln!(
            "usage: sn76489-bench [--seconds S] [--repeat N] [--variants a,b] <manifest.json>"
        );
        return ExitCode::from(2);
    };
    let manifest = match load_manifest(path) {
        Ok(manifest) => manifest,
        Err(error) => {
            eprintln!("error: {error}");
            return ExitCode::from(2);
        }
    };
    let clocks = (REAL_TIME * seconds) as u64;
    println!("{}, {clocks} clocks, best of {repeat}", manifest.name);
    for variant in variants {
        let best = (0..repeat)
            .map(|_| run(&manifest, clocks, variant))
            .fold(f64::INFINITY, f64::min);
        let rate = clocks as f64 / best;
        println!(
            "  {:10} {rate:>14.0} clocks/s  {:8.2}x real time  ({best:.4} s)",
            variant.name,
            rate / REAL_TIME
        );
    }
    ExitCode::SUCCESS
}
