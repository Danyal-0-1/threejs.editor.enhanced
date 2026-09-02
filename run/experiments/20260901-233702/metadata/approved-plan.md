# Approved execution plan (2026-09-01)

Approved by the user via three explicit choices before any phase ran:

1. Run scope        : "Lane A + B (Recommended)"
                      - Lane A: structural, offline, lark only
                      - Lane B: venv + transformers (~150MB) + 5 tokenizer
                        downloads (~50MB) to close CONSTRAINT 1
                      - Lane C (torch + multi-GB base models) NOT approved
2. Artifact drift   : "Report only, don't replace"
                      - regenerate into the experiment dir, diff, never
                        overwrite committed artifacts
3. Fix scope        : "All listed fixes + tests"
                      - ~9 engineering corrections, each with a test that
                        fails without it

Declared before approval:
  - structural lane est. 10-25 min, no network, no GPU, no downloads
  - Lane B est. 5 min, network yes, GPU no, ~200MB total download
  - files that may be modified: 9 source files + 3 test runners
  - files that may be added: 5-6 test suites + run/ deliverables
  - two items explicitly deferred to the user as RESEARCH-DECISION-REQUIRED:
    adoption of collision check (g), and the dNLL 5%/15% thresholds

Deviations from the declared plan: none in scope. One additional test suite was
added beyond the 5-6 declared (tests/test_preflight.py, 7 tests), and one
additional source file was touched (grammar/render_grammar.py, --outdir flag)
to make regenerate-and-compare possible without overwriting the artifact being
compared.
