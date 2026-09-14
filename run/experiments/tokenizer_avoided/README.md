# `tokenizer_avoided` — exploratory fertility-unmatched model evaluation

## What this experiment family is

This directory holds **exploratory fertility-unmatched model evaluations** of the
alien-syntax candidates `alpha`, `beta` and `gamma` against ordinary 3DOM
(`identity`).

Each run deliberately **waives the Experiment 01 token-fertility eligibility
gate** (relative fertility ∈ [0.95, 1.05]) so that model behaviour can be
observed anyway. Tokenizer fertility is still **measured, reported, plotted and
treated as a confounding variable**.

## What the directory name does NOT mean

> **`tokenizer_avoided` is a requested label only. Tokenizers are not bypassed.**
> A transformer model cannot operate without its tokenizer. Nothing in this
> directory is tokenizer-free.

This work is **not**:

- tokenizer-free
- tokenization-matched
- confirmatory
- a repair of Experiment 01

and it does **not** select a winning alien syntax, nor make any candidate
eligible under Experiment 01's rule.

## The two lanes — never mix them

| | **Lane A** | **Lane B** |
|---|---|---|
| Checkpoints | **Base** (`Qwen2.5-Coder-*`) | **Instruct** (`Qwen2.5-Coder-*-Instruct`) |
| Question | how *surprising* is this program? | did the model *do the task*? |
| Input | the program text alone — no prompt | language spec + editing request |
| Measure | negative log-likelihood (NLL) | canonical semantic accuracy |
| Corpus | 62 paired positive programs | 21 generation cases + 1 refusal case |

Lane A numbers are **language-model surprise**. They are never task accuracy,
hallucination rate, instruction following, or training loss. **No training
occurs anywhere in this experiment family**, so there is no training-loss curve
and no loss over epochs.

## Two corrections this family records

1. **Experiment 01 tested tokenizer configurations, not full behavioural
   models.** It loaded five tokenizer repositories through `AutoTokenizer` and
   measured how they split text; it never loaded model weights and never ran a
   forward pass. Because the four Qwen repositories share one `Qwen2Tokenizer`,
   that is evidence from **two distinct tokenizer designs**, not five. It is
   therefore incorrect to say "all five Experiment 01 models failed".
2. **CUDA is available on this machine.** An earlier audit suggested otherwise.
   Runs in this directory load real weights and execute real forward passes on
   the GPU; anything that could not run is labelled `BLOCKED` with its exact
   error.

**DeepSeek-V3** appears only as a **tokenizer**. Its weights (671B) are not
runnable here and it is **never** behaviourally tested.

## Layout

```
tokenizer_avoided/
├── README.md              <- this file
└── <UTC-RUN-ID>/          <- one self-contained run; never overwritten
    ├── STUDY_PLAN.md          frozen pre-registration + protocol deviations
    ├── STATUS.json            cell-by-cell status (VERIFIED/BLOCKED/...)
    ├── MANIFEST.json          every file with size and sha256
    ├── OVERALL_REPORT.md      the main report, written for a non-specialist
    ├── HYPOTHESIS_ASSESSMENT.md
    ├── LIMITATIONS.md
    ├── metadata/              environment, hardware, revisions, checksums
    ├── inputs/                frozen task dataset with validated gold IR
    ├── prompts/rendered/      the exact model input for every case
    ├── scripts/               the harness (see below)
    ├── logs/                  every command with its exit code
    ├── raw/<model>/<lane>/    per-item JSONL — the evidence
    ├── metrics/               aggregate.csv/json, paired items, fertility
    ├── reports/languages/     identity, alpha, beta, gamma
    ├── reports/models/        one per attempted model
    └── plots/                 each plot in its own dir:
                               plot.png + plot.svg + data.csv + README.md
```

## Runs

| run ID | date (UTC) | what it did |
|---|---|---|
| `20260914T212711Z` | 2026-09-14 | First behavioural run in this project. Lane A on 4 base checkpoints (0.5B/1.5B/3B GPU FP32, 7B CPU FP32); Lane B on the Instruct checkpoints across 4 languages × {bare, scaffolded}. Built the φ-aware behavioural harness, added validated gold IR to all 21 generation cases, and reproduced Experiment 01's fertility numbers exactly. |

## The harness built here

Experiment 01 had **no** alien-syntax instruction-model harness, and
`editMatrix.js` carried per-task expectations but **no gold programs**. Both gaps
are closed inside the run directory:

| script | what it does |
|---|---|
| `build_task_dataset.py` | ports the 22 editing / 13 multi-op / 9 labeling cases, **adds a canonical gold IR to every positive case**, and validates it five ways |
| `prompts.py` | renders the language spec + scaffold **mechanically from each φ-map**, so no 3DOM spelling is ever taught to an alien arm |
| `extract.py` | the **frozen** code-extraction rule and the outcome taxonomy |
| `score.py` | raw text → φ-parse → shared canonical IR → the Phase-1 scorers |
| `lane_a.py` / `lane_b.py` | the two lanes |
| `conditional_loss.py` | secondary: loss over a forced gold completion |
| `stats.py` | Wilson, paired bootstrap, exact McNemar, Holm |
| `aggregate.py` / `plots.py` / `reports.py` / `overall.py` | metrics, figures, prose |
| `validate.py` | the checks that must pass before conclusions are written |
| `test_harness.py` | unit tests for the renderer, parser, checkpointing and scoring |

**Alien output is never graded by surface-string equality**, and the browser's
identity-only JavaScript regex parser (`parseEmittedOps` in `editMatrix.js`) is
**never** used — on gamma input it would return `[]` and score 0 for reasons
that have nothing to do with the model.

## Ground rules that bind every run here

- Cells end in exactly one of `VERIFIED` / `FAILED` / `BLOCKED` / `SKIPPED` /
  `ERROR` / `PENDING`.
- Missing data is shown as BLOCKED / SKIPPED / NA — **never as zero**, never
  estimated, never interpolated.
- Parse validity and semantic correctness are reported in separate columns and
  **never averaged**.
- A changed precision, device, prompt, decoding setting or model revision is a
  **new, separately labelled condition** — never a silent retry.
- The archived Experiment 01 at `run/experiments/20260901-233702/` is
  **preserved unchanged**.

## Permitted and forbidden conclusions

**Permitted:** "the alien condition used more model tokens and took longer" ·
"under this tokenizer and prompt, the combined change in spelling, tokenization
and — in gamma — lexical behaviour was associated with lower performance" ·
"higher alien NLL and lower paired semantic accuracy are consistent with a
learned lexical-prior effect" · "scaffolding reduced the observed gap" ·
"accuracy remained stable despite increased token cost".

**Forbidden:** "the experiment proves dense prior knowledge caused the failures"
· "token fertility confirms hallucination" · "the model cannot understand alien
syntax" · "all five Experiment 01 models failed" · "gamma is isomorphic to 3DOM"
· "the candidates now satisfy Experiment 01" · "a winner has been established".

High fertility demonstrates **increased token cost**. Whether accuracy degrades
is a **separate measurement**. If only token count and runtime worsen while
semantic accuracy holds, that is an **efficiency cost, not a capability
failure**.
