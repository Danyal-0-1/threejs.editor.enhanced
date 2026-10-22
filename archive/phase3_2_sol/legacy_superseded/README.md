# Sol launch kit

Everything needed to run Phase 3.3 on ASU Sol. Arm A is **forward-only** — two
short scoring calls per (site, condition), no generation, no gradients — so
the full sweep is single-digit A100-hours. It is not the expensive part and
should not be rationed.

## Before submitting

```bash
module load mamba/latest
mamba create -n phase3 python=3.12 -y && source activate phase3
pip install torch --index-url https://download.pytorch.org/whl/cu121
pip install transformers lark
```

Pre-stage the weights on a login node (compute nodes are usually offline):

```bash
export HF_HOME=/scratch/$USER/hf
python sol/prefetch_models.py          # downloads + prints pinned revisions
```

`prefetch_models.py` writes `outputs/model_pins.json`. **Commit it.** Every
result file records the revision actually loaded, so a silently updated
checkpoint is detectable after the fact.

## Submit

```bash
sbatch sol/arm_a.slurm        # the full Arm A sweep, all families/lexicons
sbatch sol/primary.slurm      # extinction curves (the primary estimand)
```

## Sizing (measured, then extrapolated)

Measured on one laptop RTX 3080 Ti, 0.5B, fp16:

| workload | measured | note |
|---|---|---|
| Arm A, 544 sites × 2 conditions | **70 s** | forward-only |
| extinction, 120 sites × 7 rungs | minutes | context grows with shots |

Extrapolating by parameter count and site count, the full planned sweep
(5 model families × base+instruct × 9 lexicons × 2 grammar families) is
**single-digit A100-hours for Arm A**. Extinction is the expensive arm
because context grows with the shot ladder.

**Memory.** A 3B model already produced allocator warnings at 32 shots on a
16 GB card, and 0.5B OOMed on the top rung. On an 80 GB A100, 32B in bf16
(~64 GB) fits for forward-only work. Set `--sites` and the ladder to match
the card, and prefer more short jobs over one long one.

## Model roster

Chosen on **two axes that matter more than size**: matched base/instruct pairs
(separates pretraining prior from instruction tuning) and tokenizer diversity
(P32-001's merge behaviour is a property of the tokenizer, so `k_common`
differs per family — that is the point, not noise).

| family | sizes | why |
|---|---|---|
| Qwen2.5-Coder | 0.5–32B | continuity with Exp 01/02 and all Phase 3.x work |
| DeepSeek-Coder | 1.3/6.7/33B | different code tokenizer |
| StarCoder2 | 3/7/15B | **open training data** (The Stack v2) |
| Llama-3.x | 1/3/8B | general, not code-specialised |
| OLMo-2 | 7/13B | **open training data** (Dolma) |

The two open-data rows are what later allow *measured corpus frequency* to
replace the model-preference proxy.

## Preregistration

`../PREREGISTRATION.md` is frozen. Held out: all of `blk`, all of δ75, seeds
s3, and every model above 1.5B. **Do not look at a held-out cell before the
development analysis is finished.**
