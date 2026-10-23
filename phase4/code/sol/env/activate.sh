# activate.sh — activate the PROJECT environment safely under `set -euo pipefail`.
#
#   source "$P4_SOL/env/activate.sh"
#
# Why this exists: activating Sol's shared env under `set -u` FAILS because its
# MKL activation script reads an unset variable (verified 2026-10-05). nounset
# is therefore disabled ONLY around activation and restored afterwards.
# After sourcing, $P4_PY is the interpreter every job must use.

_p33_u=0
case $- in *u*) _p33_u=1; set +u ;; esac

if [ -x "${P4_ENV_DIR:-}/bin/python" ]; then
  # overlay mode needs the shared env's libraries on the loader path
  if [ -f "${P4_ENV_DIR}/.p33_overlay" ] && [ -d "${P4_SHARED_ENV:-}/lib" ]; then
    export CONDA_PREFIX="$P4_SHARED_ENV"
    export LD_LIBRARY_PATH="$P4_SHARED_ENV/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
  fi
  # shellcheck disable=SC1091
  . "${P4_ENV_DIR}/bin/activate"
  export P4_PY="${P4_ENV_DIR}/bin/python"
else
  echo "activate.sh: no project environment at '${P4_ENV_DIR:-unset}'." >&2
  echo "             Build it with: bash \$P4_SOL/env/make_env.sh" >&2
  [ "$_p33_u" = 1 ] && set -u
  unset _p33_u
  return 2 2>/dev/null || exit 2
fi

[ "$_p33_u" = 1 ] && set -u
unset _p33_u
