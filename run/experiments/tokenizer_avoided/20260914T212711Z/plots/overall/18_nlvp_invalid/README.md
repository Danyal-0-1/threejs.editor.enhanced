# nLVP distribution for invalid generations

**Y** nLVP = longest valid prefix in **DSL tokens** ÷ DSL-token length of the
reference solution in that language. Bars are medians with IQR whiskers.

**Denominator** `n_invalid` — ONLY outputs whose outcome was `LEX_FAIL` or
`PARSE_FAIL`. A cell with `n_invalid = 0` is omitted rather than drawn as zero.

nLVP is measured in DSL tokens, which is a different space from model
(sub-word) tokens; the two are never reported as one another
(SCORING_POLICY.md S4).
