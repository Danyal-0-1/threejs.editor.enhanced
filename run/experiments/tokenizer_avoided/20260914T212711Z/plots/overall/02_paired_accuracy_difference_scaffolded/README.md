# Lane B — paired semantic-accuracy difference from identity (scaffolded)

**Y axis** paired risk difference = (alien accuracy) − (identity accuracy) on
MATCHED items. Negative = the alien arm solved fewer of the same cases.

**Denominator** `n_pairs` matched cases per bar.

**Uncertainty** 95% paired item-level bootstrap (10 000 resamples, seed
20260910). `mcnemar_p` is the exact McNemar two-sided p on the discordant pairs
only; `n_discordant` shows how much evidence that test actually has. With a
21-case set, effect sizes and intervals matter more than p-values.
