//! `sn76489-tables`: every variant's data, one line each, in the form
//! `scripts/tables.py` prints the reference's, for rung 1: the name, the noise
//! register's width and taps (as written and mirrored), stereo, the low-period rule,
//! and the sixteen levels. Floats are printed as Python's `repr` prints them (the
//! shortest string that reads back as the same double), so equal lines are equal bits.

use sn76489_rust::VARIANTS;

fn main() {
    for variant in VARIANTS {
        let levels: Vec<String> = variant
            .levels
            .table()
            .iter()
            .map(|level| format!("{level:?}"))
            .collect();
        println!(
            "{} {} {:#06x} {:#06x} {} {} {}",
            variant.name.replace(' ', "_"),
            variant.lfsr_bits,
            variant.white_noise_taps,
            variant.left_taps(),
            variant.stereo as i32,
            variant.low_periods_hold_high as i32,
            levels.join(" ")
        );
    }
}
