//! sn76489-rust: a Rust SN76489 PSG core transcribed from, and proven equivalent to,
//! [sn76489-python](https://github.com/alewman/sn76489-python).
//!
//! The chip is [`SN76489`]; its variants are [`SN76489AN`] (the discrete TI part),
//! [`SEGA_VDP_PSG`] (the Master System's), [`GAME_GEAR_PSG`] and [`YM7101_PSG`] (the
//! Mega Drive's). The contract -- the port, the time unit, the outputs -- is the
//! reference's `docs/contract.md`. [`conformance`] runs the reference's manifests and
//! writes its trace format.

pub mod chip;
pub mod conformance;

pub use chip::{
    ideal_levels, Levels, PSGVariant, CLOCKS_PER_SAMPLE, GAME_GEAR_PSG, SEGA_VDP_PSG, SN76489,
    SN76489AN, VARIANTS, YM7101_LEVELS, YM7101_PSG,
};
