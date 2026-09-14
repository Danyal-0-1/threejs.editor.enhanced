# End-to-end per-case latency

**Y** median of the repetitions for each case, then the median across cases.
**Denominator** paired generation cases. `e2e_p95` and `e2e_iqr` are in data.csv.

Model download, cold load and warm-up are **excluded** here and reported
separately in the model reports. CUDA is synchronised before and after every
timed region.

All bars are the SAME condition (FP16, CUDA, batch 1, greedy). CPU/GPU and
different precisions are never compared as if they were one condition.
