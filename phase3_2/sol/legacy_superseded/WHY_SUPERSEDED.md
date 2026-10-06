# Why these files are superseded (moved, not deleted)

| file | defect | replaced by |
|---|---|---|
| `arm_a.slurm`, `primary.slurm` | `--partition=general` is rejected on Sol for public jobs (verified by the user on 2026-10-05); no `--qos`, no `--constraint=a100_80`; `set -euo pipefail` before conda activation, which fails because the shared env's MKL activation script reads an unset variable; no log-directory creation before `sbatch` (Slurm opens stdout before the job body runs); one monolithic job, no resume | `../jobs/*.slurm` + `../submit.sh` |
| `prefetch_models.py` | instantiates full causal models (`AutoModelForCausalLM.from_pretrained`) merely to download them; no revision pinning; no `allow_patterns`, so offline verification later fails as "incomplete snapshot" | `../src/p33/prefetch.py` |
| `README.md` | describes the above | `../README.md` |

Kept for provenance: Phase 3.3's earlier reports cite these scripts.
