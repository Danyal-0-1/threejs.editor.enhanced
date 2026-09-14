# Outcome taxonomy (scaffolded)

**Y axis** case counts. **Denominator** `n` paired generation cases per bar.

Buckets are MUTUALLY EXCLUSIVE and evaluated in order (SCORING_POLICY.md S3):
`LEX_FAIL` (cannot tokenise) · `PARSE_FAIL` (tokenises, no derivation) ·
`VALID_VACUOUS` (parses, zero operations — the D5 rule: a parse success and a
task failure) · `VALID_WRONG` (parses, ≥1 op, IR ≠ gold) · `VALID_CORRECT` ·
plus `OOM` / `TIMEOUT` / `HARNESS_ERROR`.

A parse failure is **not** a hallucination; hallucination categories are counted
separately.
