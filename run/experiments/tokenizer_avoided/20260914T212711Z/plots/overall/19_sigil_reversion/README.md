# 3DOM class-sigil reversion — the interference signature

**Y axis** the share of *on-language* answers whose quoted selector body uses
3DOM's `.` class sigil even though this language's class sigil is something
else. **Denominator** `n_on_language`: generations that used this language's
selector-entry spelling, i.e. answers that were otherwise written in the right
language.

**What it isolates.** These are outputs where the model got the program shape,
the selector-entry token, the chain operator and often the verb right, and then
reached for `.` inside the selector — the one habit 3DOM and CSS share most
strongly.

**Why it matters.** The effect is essentially confined to **alpha**, whose class
sigil is `#` — a plausible-but-wrong alternative that an existing habit can
override. Beta (`~`) and gamma (`◈`) are alien enough that no competing habit
fires, and they show ~0% throughout. In the `scaffolded` condition the prompt
*displays the correct sigil next to every tag*, so reversion there is a
reversion against explicit, immediately-available instruction.

Descriptive: this counts a specific surface behaviour; it does not by itself
establish a mechanism.
