# Environment

`make_env.sh` builds the project environment at `$P33_ENV_DIR`; `activate.sh`
activates it safely under `set -euo pipefail`. Neither modifies Sol's shared
environment. The dependencies are declared in `requirements.in`.

| File | What it is |
|---|---|
| `requirements.in` | top-level dependencies and their version ranges |
| `requirements.lock.sol.txt` | written by `make_env.sh` the first time it runs on Sol: the exact resolution there |
| `requirements.lock.laptop.txt` | the resolution used for the local tests and the laptop smoke |

## Versions actually recorded

Every job writes its interpreter and package versions into its manifest
(`results/<run>/manifests/job_*.json`). The names of environments are never
trusted. For example, the shared env named `pytorch-gpu-2.3.1-cuda-12.1` was
reported to contain torch 2.11.

The development run `dev-20261006a` (2026-10-07, all 8 scoring jobs) recorded:

| | |
|---|---|
| python | 3.12.3 |
| torch | 2.8.0+cu126 (CUDA runtime 12.6) |
| transformers | 4.57.1 |
| huggingface_hub | 0.36.0 |
| tokenizers | 0.22.1 |
| safetensors | 0.6.2 |
| accelerate | 1.11.0 (needed for the 2-GPU models) |
| numpy | 2.2.6 |
| matplotlib | 3.10.7 |
| lark | 1.3.1 |
| GPU | NVIDIA A100-SXM4-80GB, driver 595.71.05 |

The local re-analysis on 2026-10-07 used transformers 5.16.1, numpy 2.5.2 and
matplotlib 3.11.2. Analysis needs no model library at all.

Re-exporting `dev-20261006a` locally with the code that produced it reproduced
18 of its 19 CSVs byte for byte. The nineteenth differed in one cell: a fitted
calibration intercept of −8.5e-17 against −7.9e-17, which is floating-point
noise on a value that is zero by construction.
