# Parse validity vs semantic correctness

**X** fraction of outputs that are well-formed programs in the target language.
**Y** fraction that are also semantically correct against the gold IR.
**Denominator** `n` paired generation cases per point.

The dashed diagonal is parity. Points far below it parse but mean the wrong
thing — SCORING_POLICY.md S1's whole point: these are orthogonal constructs and
collapsing them into one "accuracy" number hides the behaviour under study.
