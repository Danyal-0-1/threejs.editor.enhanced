# Limitations — run `20260914T212711Z`

## Design limitations

1. **Fertility is not controlled — this is the defining limitation.** The Experiment 01 eligibility gate (relative fertility ∈ [0.95, 1.05]) was deliberately waived so behaviour could be observed at all. Every alien language therefore differs from 3DOM in spelling **and** in token cost simultaneously. No result here can attribute an accuracy difference to spelling rather than to length, or vice versa.

2. **Gamma is not a clean isomorphic control.** It carries 24 findings from Experiment 01's proposed check (g): 22 `g1` (word-class spellings became symbols, changing how keywords are distinguished from identifiers) and 2 `g2` (token sequences reachable in gamma that no 3DOM text can produce). Gamma is a Unicode/lexer stress diagnostic. Dense-prior claims must not rest on it.

3. **Alpha is the cleanest exploratory comparison but still out of band.** Its relative fertility is 1.068× (Qwen2) / 1.073× (DeepSeek-V3), above the 1.05 limit. Alpha is also an *interference* design — it reuses 3DOM words with permuted meanings — so it confounds unfamiliarity with active misdirection.

4. **Beta is strongly fertility-confounded** (1.401× Qwen2) despite matching 3DOM's character length almost exactly.

5. **Small behavioural dataset.** 21 generation cases (plus 1 graceful-refusal case) from one editing domain and two fixture scenes. Wilson and bootstrap intervals are correspondingly wide, and the exact McNemar tests have few discordant pairs and therefore little power.

6. **One model family.** All behavioural models are Qwen2.5-Coder and share one Qwen2 BPE tokenizer. The fertility measurement adds a second tokenizer design (DeepSeek-V3), but **DeepSeek-V3 was used as a tokenizer only** — its weights (671B) are not runnable on this machine and it was **never** behaviourally tested.

7. **One prompt design.** A single specification format, one worked-example set, one scaffold format. Prompt wording is known to move small-model behaviour substantially; none of that variance is sampled here.

8. **English descriptions unavoidably favour identity.** The operation descriptions are plain English and identical in all four arms, but identity's *spellings* are themselves English words, so the description and the spelling agree only in the identity arm. This is inherent to comparing a native notation against invented ones, and is part of the phenomenon under study rather than a harness defect.

9. **Conditional task loss depends on the reference serialisation.** It scores one chosen gold program string; a different but equally correct program would give different numbers.

10. **Greedy decoding only.** One deterministic completion per case. No sampling, no temperature sweep, no self-consistency, no pass@k.

## Measurement limitations

11. **Lane A scores base models, Lane B scores instruct models.** They answer different questions and are never pooled. Base-model NLL is language-model surprise on teacher-forced text; it is not task accuracy.

12. **No training occurred anywhere in this study.** There is no training loss and no loss-over-epochs curve.

13. **Timing is hardware- and condition-specific.** Figures come from one RTX 3080 Ti Laptop GPU under FP16 (Lane B) and FP32 (Lane A). CPU and GPU runs, and different precisions, are never compared as though they were one condition.

14. **Blocked cells.** The following were attempted under the predeclared configuration and recorded as failures rather than retried at different settings:

    - `Qwen/Qwen2.5-Coder-7B` Lane A (fp32/cuda) — **OOM**. Command: `lane_a.py --model Qwen/Qwen2.5-Coder-7B --precision fp32 --device cuda`. Error: OutOfMemoryError: CUDA out of memory. Tried to allocate 260.00 MiB. GPU 0 has a total capacity of 15.61 GiB of which 114.12 MiB is free. Including non-PyTorch memory, this process has 15.15 GiB memory

## What this study does not do

- It does **not** select or announce a winning alien syntax.
- It does **not** make any candidate eligible under Experiment 01's rule.
- It does **not** prove that dense prior knowledge caused any failure.
- It does **not** show that fertility confirms hallucination.
- It does **not** show that a model 'cannot understand' alien syntax.
- It does **not** claim gamma is isomorphic to 3DOM.
