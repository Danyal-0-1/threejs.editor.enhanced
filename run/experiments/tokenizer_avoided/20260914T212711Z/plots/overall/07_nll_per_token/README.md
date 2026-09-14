# Lane A — nll per token

**Y axis** nats / model token. **X axis** base checkpoint. Bars are the four languages.

**Denominator** corpus TOTALS over the 62 paired positive programs
(Σ nats ÷ Σ scored tokens),
not a mean of per-program ratios.

**Uncertainty** none shown here — this panel is the point estimate. Paired
uncertainty is in `08_delta_nll_per_char`.

**Reading** higher = the base model found that language's programs more
surprising. NLL/token is DIAGNOSTIC ONLY: token boundaries differ across languages, so a lexicon that fragments more spreads the same surprise over more steps.

This is language-model surprise on teacher-forced text. It is **not** task
accuracy, hallucination rate, instruction following, or training loss. **No
training occurred.**
