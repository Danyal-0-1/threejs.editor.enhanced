"""p4 — the Phase 4 pipeline: a verified copy of the Phase 3.3 pipeline, one folder per stage.

Read the stages in the order the data flows through them (../README.md has the full map):

    language/     the two grammar families, the 80 template programs, the lexicon family
    sites/        decision sites, their collision classes, balanced site selection
    prompts/      the rule table and its controls, leakage-free worked examples
    scoring/      one model's margin at one site: first divergent token, fp32 output head
    experiments/  Arm A and the extinction ladder, Arm B (free generation), H5 (repair)
    analysis/     H4, k*, H2, the template-cluster bootstrap, power
    reporting/    a run's 19 CSVs, 12 figures and 10 reports
    governance/   the model registry, the registered split, freeze and unlock, provenance
    runtime/      configuration and locations, crash-safe shards, preflight, downloads

Importing p4 runs paths.py first, which puts the language library (../dsl) on sys.path.
"""

from p4 import paths  # noqa: F401  (side-effecting: sys.path)

SCHEMA_VERSION = "p33/1"     # unchanged from Phase 3.3, so the outputs stay comparable
