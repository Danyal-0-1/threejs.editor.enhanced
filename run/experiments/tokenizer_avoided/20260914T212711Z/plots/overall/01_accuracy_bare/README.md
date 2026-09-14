# Lane B — semantic accuracy by language and model (bare)

**Y axis** canonical semantic accuracy = all applicable task components correct
**AND** the answer was written in the language that was asked for.

**Denominator** the paired generation cases (`n` in data.csv) — the graceful
refusal case is excluded and scored separately.

**Uncertainty** Wilson 95% interval on the proportion.

**Reading** these are INSTRUCT checkpoints answering an editing request. They
are task accuracy, and must never be read as base-model NLL.
