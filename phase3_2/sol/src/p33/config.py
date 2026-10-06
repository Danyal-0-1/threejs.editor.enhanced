"""config.py — paths, Sol defaults, run configuration and hashing.

NOTHING HERE HARD-CODES A USERNAME. Every location resolves from environment
variables at runtime, with the documented Sol layout as the default:

    code      $P33_CODE_ROOT     default $HOME/phase3-3_experiment_sol/repo
    results   $P33_RESULTS_ROOT  default $HOME/phase3-3_experiment_sol/results
    models    $P33_HF_ROOT       default $SCRATCH/hf   (or /scratch/<login>/hf)

Sol scheduler defaults (verified by the user on 2026-10-05; overridable):

    account     $P33_ACCOUNT     grp_tlingego
    partition   $P33_PARTITION   public        (`general` is rejected)
    qos         $P33_QOS         public
    gres        $P33_GRES        gpu:a100:1
    constraint  $P33_CONSTRAINT  a100_80

HUGGING FACE CACHE. `HF_HOME` is the root and `HF_HUB_CACHE` is set to
`$HF_HOME/hub`, the standard layout, so the cache can be inspected with the
normal tools. `TRANSFORMERS_CACHE` is exported too, but only for older
transformers: it has NO effect in transformers 5.x (verified: zero references
in the installed 5.16.1). It is not the variable that matters.
"""

from __future__ import annotations

import getpass
import hashlib
import json
import os
import tempfile
from dataclasses import asdict, dataclass, field
from typing import Any

from p33 import SCHEMA_VERSION, _paths  # noqa: F401


# ---------------------------------------------------------------------------
# locations
# ---------------------------------------------------------------------------

def _home() -> str:
    return os.environ.get("HOME") or os.path.expanduser("~")


def experiment_root() -> str:
    return os.environ.get("P33_EXPERIMENT_ROOT",
                          os.path.join(_home(), "phase3-3_experiment_sol"))


def code_root() -> str:
    return os.environ.get("P33_CODE_ROOT", os.path.join(experiment_root(), "repo"))


def results_root() -> str:
    return os.environ.get("P33_RESULTS_ROOT",
                          os.path.join(experiment_root(), "results"))


def scratch_root() -> str:
    return os.environ.get("SCRATCH") or os.path.join("/scratch", getpass.getuser())


def hf_root() -> str:
    return os.environ.get("P33_HF_ROOT", os.path.join(scratch_root(), "hf"))


def hf_env(*, offline: bool = True) -> dict[str, str]:
    """The environment every model-touching process must run under."""
    root = hf_root()
    env = {"HF_HOME": root,
           "HF_HUB_CACHE": os.path.join(root, "hub"),
           "TRANSFORMERS_CACHE": os.path.join(root, "hub"),   # no-op on transformers 5
           "TOKENIZERS_PARALLELISM": "false"}
    if offline:
        env.update({"HF_HUB_OFFLINE": "1", "TRANSFORMERS_OFFLINE": "1"})
    return env


@dataclass(frozen=True)
class SolDefaults:
    account: str = field(default_factory=lambda: os.environ.get("P33_ACCOUNT", "grp_tlingego"))
    partition: str = field(default_factory=lambda: os.environ.get("P33_PARTITION", "public"))
    qos: str = field(default_factory=lambda: os.environ.get("P33_QOS", "public"))
    gres: str = field(default_factory=lambda: os.environ.get("P33_GRES", "gpu:a100:1"))
    constraint: str = field(default_factory=lambda: os.environ.get("P33_CONSTRAINT", "a100_80"))


RUN_SUBDIRS = ("raw/shards", "checkpoints", "merged", "csv", "plots",
               "reports", "manifests", "logs")


def run_dir(run_id: str, root: str | None = None) -> str:
    return os.path.join(root or results_root(), run_id)


def ensure_run_layout(path: str) -> dict[str, str]:
    out = {}
    for sub in RUN_SUBDIRS:
        d = os.path.join(path, sub)
        os.makedirs(d, exist_ok=True)
        out[sub] = d
    return out


# ---------------------------------------------------------------------------
# run configuration
# ---------------------------------------------------------------------------

DEFAULT_SEEDS = {"bootstrap": 20261002, "demo_order": 20261005,
                 "h5_random": [1, 2, 3, 4, 5], "power": 20261006}


@dataclass
class RunConfig:
    run_id: str
    stage: str                                   # smoke | dev | heldout
    models: list[str]
    families: list[str]
    lexicons: list[str]
    site_limit: int = 0                          # 0 = every eligible site
    chunk_size: int = 64
    dtype: str = "bfloat16"
    lm_head_fp32: bool = True
    seeds: dict = field(default_factory=lambda: dict(DEFAULT_SEEDS))
    arm_a: dict = field(default_factory=lambda: {
        "conditions": ["rule", "norule", "norule_lenmatched"],
        "program_nll": True})
    primary: dict = field(default_factory=lambda: {
        "ladder": [0, 1, 2, 4, 8, 16, 32], "paraphrases": ["p0", "p1", "p2"],
        "site_limit": 400})
    armb: dict = field(default_factory=lambda: {
        "max_new_tokens": 192, "n_demos": 4, "template_limit": 0,
        "do_sample": False, "num_beams": 1})
    h5: dict = field(default_factory=lambda: {
        "budget": 3, "low_risk_tolerance": 0.02})
    analysis: dict = field(default_factory=lambda: {
        "B": 2000, "alpha": 0.05, "unit": "template", "min_clusters": 8,
        "precision_at_k": [10, 50], "ece_bins": 10})
    allow_exploratory: bool = False
    allow_non_a100: bool = False
    freeze_path: str | None = None               # heldout stage only
    note: str = ""
    schema_version: str = SCHEMA_VERSION

    # -- serialisation -----------------------------------------------------
    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "RunConfig":
        known = {k: v for k, v in d.items() if k in cls.__dataclass_fields__}
        return cls(**known)

    @classmethod
    def load(cls, path: str) -> "RunConfig":
        with open(path, encoding="utf-8") as fh:
            return cls.from_dict(json.load(fh))

    # -- identity ------------------------------------------------------------
    def config_hash(self) -> str:
        """Hash of everything that changes what is MEASURED.

        `run_id` and `note` are excluded: renaming a run must not invalidate
        it. Everything else is included, so a resume with a changed ladder,
        dtype, lexicon list or seed is rejected as incompatible.
        """
        d = self.to_dict()
        for k in ("run_id", "note"):
            d.pop(k, None)
        return sha256_json(d)

    def validate(self) -> None:
        if self.stage not in ("smoke", "dev", "heldout"):
            raise ValueError(f"stage must be smoke|dev|heldout, got {self.stage!r}")
        if not self.run_id.startswith(self.stage + "-"):
            raise ValueError(
                f"run_id {self.run_id!r} must start with '{self.stage}-' so "
                f"development and held-out outputs are physically separated")
        if self.stage == "heldout" and not self.freeze_path:
            raise ValueError("a heldout run must name its DEV_FREEZE.json")
        if self.stage == "smoke" and (len(self.models) != 1 or len(self.lexicons) != 1
                                      or len(self.families) != 1):
            raise ValueError("a smoke run is exactly one model, one lexicon, "
                             "one family")
        if not self.models or not self.families or not self.lexicons:
            raise ValueError("models, families and lexicons must be non-empty")


# ---------------------------------------------------------------------------
# hashing
# ---------------------------------------------------------------------------

_UMASK = os.umask(0)
os.umask(_UMASK)


def atomic_write_text(path: str, text: str) -> None:
    """Write `text` to `path` so that no reader ever sees a partial file (P33-014).

    The temp file comes from mkstemp in the target directory, so concurrent
    writers never share one: Slurm array tasks start together, run on different
    nodes over one shared filesystem, and can have the SAME pid -- a
    `.tmp.<pid>` or fixed `.tmp` name let two of them interleave into a corrupt
    plan/arms file that every later resume then refused. fsync, then os.replace.
    """
    d = os.path.dirname(path) or "."
    fd, tmp = tempfile.mkstemp(dir=d, prefix=os.path.basename(path) + ".tmp.")
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(text.encode("utf-8"))
            fh.flush()
            os.fsync(fh.fileno())
        os.chmod(tmp, 0o666 & ~_UMASK)        # mkstemp is 0600; keep the usual mode
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.remove(tmp)
        raise


def sha256_json(obj: Any) -> str:
    blob = json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, default=str)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def source_hashes() -> dict[str, str]:
    """Every source file whose change could change a result.

    Used by the freeze: held-out evaluation refuses to run if any of these
    differ from what was frozen, because then the frozen analysis is not the
    one being executed.
    """
    roots = [os.path.join(_paths.P33_SRC, "p33"),
             os.path.join(_paths.PHASE3_2_SRC, "phase3_2"),
             os.path.join(_paths.REPO_ROOT, "phase3", "src", "phase3")]
    out: dict[str, str] = {}
    for root in roots:
        for dirpath, _dirs, files in os.walk(root):
            for f in sorted(files):
                if f.endswith(".py"):
                    p = os.path.join(dirpath, f)
                    out[os.path.relpath(p, _paths.REPO_ROOT)] = sha256_file(p)
    cli = os.path.join(_paths.SOL_ROOT, "scripts", "p33.py")    # it picks the scorer
    out[os.path.relpath(cli, _paths.REPO_ROOT)] = sha256_file(cli)
    return dict(sorted(out.items()))


def materials_hash(lexicons: list[str]) -> dict[str, str]:
    """Hashes of the phi-maps, templates and terminal table a run depends on."""
    import phi as P
    from phase3_2 import templates as TM
    from phase3_2._vendor import CANDIDATES, PHASE1
    out = {"terminals.json": sha256_file(os.path.join(PHASE1, "terminals.json"))}
    for lx in sorted(set(lexicons)):
        p = os.path.join(CANDIDATES, f"phi_{lx}.json")
        out[f"phi_{lx}.json"] = sha256_file(p) if os.path.exists(p) else "MISSING"
    import canonicalize as C
    temps = TM.build_templates()
    out["templates"] = sha256_json([[t.template_id, C.canonical_json(t.ir)]
                                    for t in temps])
    from phase3_2 import backends
    out["blk_grammar"] = hashlib.sha256(backends.BLK_GRAMMAR.encode()).hexdigest()
    _ = P
    return out
