"""extract.py — the FROZEN code-extraction rule and the outcome taxonomy.

FROZEN BEFORE INFERENCE. Extraction never repairs: it locates the model's code
and hands it to the parser unchanged. If the located text does not parse, that
is a PARSE_FAIL, not an invitation to fix it.

RULE (applied in order, first match wins):
  E1  the first ``` fenced block; its content verbatim, opening info-string
      line dropped
  E2  if there is no fence, the first run of lines from the first line
      containing the language's selector-entry spelling to the last line
      containing ')();'  -- a model that answers without a fence is still
      answering
  E3  otherwise the whole response, stripped

Everything E1-E3 produce is recorded; `extraction_rule` says which fired, so a
result can never be read without knowing how its code was obtained.
"""
from __future__ import annotations

import re

FENCE = re.compile(r"```[^\n]*\n(.*?)(?:```|\Z)", re.DOTALL)

# Mutually exclusive top-level outcomes (SCORING_POLICY.md S3).
LEX_FAIL, PARSE_FAIL = "LEX_FAIL", "PARSE_FAIL"
VALID_VACUOUS, VALID_WRONG, VALID_CORRECT = "VALID_VACUOUS", "VALID_WRONG", "VALID_CORRECT"
TIMEOUT, OOM, HARNESS_ERROR = "TIMEOUT", "OOM", "HARNESS_ERROR"
OUTCOMES = (LEX_FAIL, PARSE_FAIL, VALID_VACUOUS, VALID_WRONG, VALID_CORRECT,
            TIMEOUT, OOM, HARNESS_ERROR)


def extract_code(response: str, entry_spelling: str) -> tuple[str, str]:
    """(code, rule_id). Never raises, never repairs."""
    if not isinstance(response, str) or not response.strip():
        return "", "E0_EMPTY"

    m = FENCE.search(response)
    if m:
        return m.group(1).strip(), "E1_FENCE"

    lines = response.splitlines()
    start = next((i for i, l in enumerate(lines) if entry_spelling in l), None)
    if start is not None:
        end = next((i for i in range(len(lines) - 1, start - 1, -1)
                    if ")();" in lines[i]), None)
        if end is not None:
            return "\n".join(lines[start:end + 1]).strip(), "E2_UNFENCED"

    return response.strip(), "E3_WHOLE"
