# Unlock provenance — heldout-20261007a

The unlock phrase was entered by Claude (AI coding assistant) on 2026-10-07T23:05:31-07:00, at the
investigator s explicit direction ("Freeze, unlock, run all", 2026-10-07), after:

- the CPU-test job passed on Sol (results/setup-20261007b; 138 + 1 hardware-blocked, 36, 54);
- the D9 re-analysis of dev-20261006a was recorded on Sol
  (analysis_revisions/r1-2026-10-07-metric-corrections: 652 inputs byte-identical, all checks passed,
  analysis-source digest 3c3e772c66ecf51e);
- all 21 held-out checkpoints were downloaded to scratch and pinned (model_pins.json: 21 pins, no failures);
- the development freeze was written by job 64942745 (DEV_FREEZE.json sha256 b319c3fcba3dd325..., git 78b2bcd).

The registered design was frozen as is, including the pooled rule effect at about 25% power at the pilot ICC
(POWER_ANALYSIS.md of dev-20261006a).
