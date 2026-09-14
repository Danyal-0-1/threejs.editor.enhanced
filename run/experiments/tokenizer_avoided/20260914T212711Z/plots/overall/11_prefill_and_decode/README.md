# Prompt-prefill runtime

**Y** median prefill seconds, measured as a 1-new-token `generate` on the same
input. `decode_median` (end-to-end minus prefill) is in the same data.csv.

**Denominator** paired generation cases. Prefill grows with PROMPT length, which
is where scaffolding and higher-fertility languages cost extra tokens.
