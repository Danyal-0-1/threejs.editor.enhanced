# gamma — Lane A base-model NLL per character

**Y** nats per Unicode character on the 62-item paired positive corpus.
**Denominator** corpus totals (Σ nats ÷ Σ characters).
**Uncertainty** `delta_nll_per_char` with `ci_lo`/`ci_hi` (95% paired bootstrap,
10 000 resamples) is in data.csv.

Language-model surprise on teacher-forced programs with no task prompt. **Not**
task accuracy; **no training occurred.**
