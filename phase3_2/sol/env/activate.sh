# activate.sh — activate the PROJECT environment safely under `set -euo pipefail`.
#
#   source "$P33_SOL/env/activate.sh"
#
# Why this exists: activating Sol's shared env under `set -u` FAILS because its
# MKL activation script reads an unset variable (verified 2026-10-05). nounset
# is therefore disabled ONLY around activation and restored afterwards.
# After sourcing, $P33_PY is the interpreter every job must use.

_p33_u=0
case $- in *u*) _p33_u=1; set +u ;; esac

if [ -x "${P33_ENV_DIR:-}/bin/python" ]; then
  # overlay mode needs the shared env's libraries on the loader path
  if [ -f "${P33_ENV_DIR}/.p33_overlay" ] && [ -d "${P33_SHARED_ENV:-}/lib" ]; then
    export CONDA_PREFIX="$P33_SHARED_ENV"
    export LD_LIBRARY_PATH="$P33_SHARED_ENV/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
  fi
  # shellcheck disable=SC1091
  . "${P33_ENV_DIR}/bin/activate"
  export P33_PY="${P33_ENV_DIR}/bin/python"
else
  echo "activate.sh: no project environment at '${P33_ENV_DIR:-unset}'." >&2
  echo "             Build it with: bash \$P33_SOL/env/make_env.sh" >&2
  [ "$_p33_u" = 1 ] && set -u
  unset _p33_u
  return 2 2>/dev/null || exit 2
fi

[ "$_p33_u" = 1 ] && set -u
unset _p33_u
