#!/bin/bash
# make_env.sh — build the PROJECT environment. Never modifies a shared env.
#
#   MODE=overlay    (default) venv layered on Sol's shared PyTorch env with
#                   --system-site-packages: torch/CUDA come from the shared
#                   env, our pinned pure-python deps (incl. lark) are added.
#                   Fast, no multi-GB torch download.
#   MODE=standalone fresh venv; torch from the PyTorch CUDA wheel index.
#                   Slower, independent of the shared env changing under you.
#
# Either way the RESOLVED versions are frozen into
# $P33_ENV_DIR/requirements.lock.sol.txt and verified with an import check.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$HERE/../sol.env"
MODE="${MODE:-overlay}"

if [ -e "$P33_ENV_DIR" ]; then
  echo "refusing: $P33_ENV_DIR exists. Remove it deliberately to rebuild." >&2
  exit 2
fi

if [ "$MODE" = overlay ]; then
  BASE_PY="$P33_SHARED_ENV/bin/python"
  [ -x "$BASE_PY" ] || { echo "no shared python at $BASE_PY" >&2; exit 2; }
  "$BASE_PY" -m venv --system-site-packages "$P33_ENV_DIR"
  touch "$P33_ENV_DIR/.p33_overlay"
else
  module load mamba/latest 2>/dev/null || true
  python3 -m venv "$P33_ENV_DIR"
  "$P33_ENV_DIR/bin/python" -m pip install --upgrade pip
  "$P33_ENV_DIR/bin/python" -m pip install torch --index-url https://download.pytorch.org/whl/cu121
fi

"$P33_ENV_DIR/bin/python" -m pip install -r "$HERE/requirements.in"
"$P33_ENV_DIR/bin/python" -m pip freeze --all > "$P33_ENV_DIR/requirements.lock.sol.txt"
cp "$P33_ENV_DIR/requirements.lock.sol.txt" "$HERE/requirements.lock.sol.txt" 2>/dev/null || true

# shellcheck disable=SC1091
source "$HERE/activate.sh"
"$P33_PY" - <<'PY'
import importlib
for m in ("lark", "numpy", "matplotlib", "transformers", "huggingface_hub", "torch"):
    mod = importlib.import_module(m)
    print(f"  {m:16s} {getattr(mod, '__version__', '?')}")
import torch
print("  torch.cuda.is_available() =", torch.cuda.is_available(), "(False is expected on a login node)")
PY
echo "environment ready: $P33_ENV_DIR (lock: requirements.lock.sol.txt)"
