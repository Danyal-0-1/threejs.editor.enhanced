# 00 — What we found, in plain language

> ⚠️ **ERRATUM (2026-10-05) — read [`ERRATA.md`](ERRATA.md) first.** The `k*` ≈ 5–7 result below is **withdrawn** (82/120 sites saw their own target program among the demonstrations, plus two definition errors), and the rule-effect intervals are **corrected** (all four now include zero). `blk` is not a clean held-out grammar family.


Every important result below comes with a **mental image**. Read the images
first; the numbers and the maths are underneath each one. Nothing here is
simplified to the point of being wrong — where a result is shaky, it says so.

> **The one-line version.** A 3D-editing language that borrows CSS's look
> inherits CSS's habits. A small model picks the familiar-but-wrong spelling
> about **45% of the time**, handing it the full translation table barely
> helps, and it takes roughly **6 worked examples** to break the habit — if it
> breaks at all.

---

## The setup, in one picture

German **"Gift"** means *poison*. You write a perfectly grammatical German
sentence, hand someone a Gift, and poison them. No error message — the
sentence was valid. It just meant something else.

That is the bug:

```
.wheel   ← what CSS habit says   → valid 3DOM, edits the WRONG object
#wheel   ← what the rule says    → valid 3DOM, edits the wheel
```

The model is a **fluent CSS speaker handed a one-page 3DOM phrasebook**.
Under pressure it falls back on the language it actually knows.

We built 3,326 of these false-friend spots across two different-looking
versions of the language, then measured what models do at each one.

---

## Result 1 — The habit wins about 45% of the time

### 🧠 Mental image

> You give someone a glossary, point at the line that says *"Gift = poison,"*
> and ask them to use it. **Nearly half the time they still hand over a
> present.**

### The number

Reversion rate — how often the model prefers the familiar-but-wrong spelling,
**with the full 28-row translation table sitting in its context**:

| model | `dom` | `blk` |
|---|---|---|
| 0.5B base | 0.412 `[0.367, 0.457]` | 0.456 `[0.410, 0.505]` |
| 0.5B instruct | 0.445 `[0.400, 0.490]` | 0.423 `[0.376, 0.466]` |

Brackets are 95% intervals from resampling **templates**, not sites (why that
matters: Result 5).

### The maths, lightly

For one spot we compare the two spellings the model could write:

$$M = \log P(\text{the rule's spelling}) - \log P(\text{the familiar spelling})$$

`M > 0` means it prefers the rule. `M < 0` is **reversion**. The rate above is
just how often `M < 0`.

The logs turn "how many times more likely" into plain addition. `M = −2` means
the familiar spelling is about `e² ≈ 7×` more likely.

---

## Result 2 — Giving it the translation table barely helps

### 🧠 Mental image

> You hand the student a glossary. Then you take it away. **You can barely
> tell the difference in what they write.**

### The number

We ran every spot **twice**: once with the full table in the prompt, once with
a matched prompt that lists the roles but withholds the spellings.

$$\text{rule effect} = M(\text{with table}) - M(\text{without table})$$

| model | family | mean | 95% interval | helped |
|---|---|---:|---|---:|
| 0.5B base | dom | +0.171 | `[+0.029, +0.326]` | 55.1% |
| 0.5B base | blk | +0.156 | `[−0.020, +0.344]` | 52.6% |
| 0.5B instruct | dom | +0.199 | `[−0.003, +0.414]` | 53.7% |
| 0.5B instruct | blk | +0.222 | `[−0.004, +0.465]` | 59.2% |

**Three of the four intervals contain zero.** The table helps about as often
as a coin flip.

### Why this matters more than it looks

This is the first number in the whole project that is actually about
**following an instruction**, rather than about what the model already
believed. Earlier runs had a prompt that *said* "follow the token table" and
**contained no table** — so they measured habit strength and nothing else.

Published work (PLSemanticsBench) found this for whole programs. We now see it
at the level of a **single character**.

---

## Result 3 — It takes about 6 examples to break the habit ⭐ the headline

### 🧠 Mental image

> Don't ask *"does the student get it wrong?"* Ask **"how many worked examples
> before they stop getting it wrong?"**
>
> Answer: **about six.** And for roughly **one spot in eight, they never stop**
> — not within 32 examples.

### The number

We showed the model 0, 1, 2, 4, 8, 16, then 32 correct example programs and
watched `M` climb. `k*` is where it crosses zero.

| model | family | **k\* median** | 95% interval | never crossed |
|---|---|---:|---|---:|
| 0.5B base | dom | **6.64** | `[4.35, 10.40]` | 18% |
| 0.5B base | blk | **4.96** | `[3.84, 6.72]` | 15% |
| 0.5B instruct | dom | **6.94** | `[5.97, 12.38]` | 12% |
| 0.5B instruct | blk | **5.83** | `[5.37, 7.06]` | 8% |

### Why this is the *primary* result and not the reversion rate

Here is the trap it avoids. Suppose you measure "how much worse is condition A
than condition B" on a log scale. Stretch or squash that scale — take a
different but equally defensible measure — and the gap between two gaps can
grow, shrink, or **flip sign**. Interaction effects measured that way are
partly a fact about your ruler.

A **threshold is read off the horizontal axis.** "It took six examples" stays
six examples no matter how you rescale the vertical one.

### 🧠 Mental image for the "never crossed" column

> Those sites are **not** missing data, and you must not drop them. They are
> the *strongest* habits — the ones that resisted everything you threw at
> them. Deleting them is like measuring how long patients take to recover and
> throwing out everyone still sick at the end of the study.

Statisticians call this **censoring**. We report it (8–18%) beside every `k*`.

---

## Result 4 — It is not just a tokenizer artifact

### 🧠 Mental image

> Worry: maybe the alien spelling is only harder because it costs the model
> **more keystrokes**, not because it means something confusing.
>
> So we built a second version of the language where the keystroke cost is
> essentially identical — and got the same answer.

### The number

Token fertility — how many tokens the language costs per character, relative
to plain 3DOM:

| family | fertility | verdict |
|---|---:|---|
| `dom` | **1.077** | costs ~8% more tokens — confound present |
| `blk` | **1.008** | costs ~1% more — **controlled** |

And the reversion rates are the same in both (0.41–0.46). **The effect
survives in the family where token cost is controlled**, so it is about
meaning, not typing cost.

This is also why the second grammar family had to exist: `blk` has no
`.method()` chaining, and it turns out the `.`→`#` remap is exactly what
fragments tokens in `dom`.

---

## Result 5 — Why our error bars are wide on purpose

### 🧠 Mental image

> You survey 3,326 people — but they live in 80 households, and you
> interviewed whole households. **You do not have 3,326 independent opinions.
> You have about 80.**
>
> Treating them as 3,326 would make your error bars roughly 6× too narrow and
> every finding look certain.

### What we do

We resample **templates** (the 80 independently designed programs), not sites.
Each template drawn carries all of its sites with it. Our intervals are wide
because they are honest.

The code refuses to produce an interval from fewer than 8 clusters — with one
lexicon, a lexicon-level bootstrap returns `None` rather than a number.

---

## Result 6 — The wording of the prompt does not matter much

### 🧠 Mental image

> We asked the same question in three voices — curt, standard, and wordy — and
> got the same answer. **The finding is about the language, not about our
> phrasing.**

### The number

Reversion rate across three prompt framings carrying the identical table:

| model | family | range across p0/p1/p2 |
|---|---|---:|
| 0.5B base | dom | 0.050 |
| 0.5B base | blk | 0.033 |
| 0.5B instruct | dom | **0.017** |
| 0.5B instruct | blk | **0.017** |

Reversion moves by at most 5 percentage points. **The mean margin is less
stable than the rate** — so the binary outcome is the robust one, and that is
what we report.

---

## Result 7 — A conclusion we had to withdraw ⚠️

### 🧠 Mental image

> Earlier we announced: *"the effect is strongest where no 3D knowledge is
> needed, so this is purely about surface habits."* Clean, quotable, and it
> **evaporated** the moment we controlled the experiment properly.
>
> Worse: comparing those two groups was like deciding who is fitter by racing
> **sprinters against swimmers.** They never compete in the same event.

### What happened

Two defects produced that story: the run scored only one of the two grammar
families, and its prompt contained no table.

Fixed, the ordering **flips between conditions** — one stratum is lowest in
one setting (0.286) and highest in another (0.500).

Then the length-matched analysis showed why it is not fixable with the current
materials:

| group | token-length signatures |
|---|---|
| sigil sites (`.` vs `#`) | **1,208 are all "1 token vs 1 token"** |
| verb sites (`scale` vs `move`) | 288 are "2 vs 2", only 160 are "1 vs 1" |

They barely overlap. Where they do overlap (1-vs-1) there are **151 sigil
sites against only 20 verb sites**, and the difference is +0.08 in one family
and −0.01 in the other — nothing.

**So: the "does 3D knowledge matter?" question is reopened, not answered.** To
settle it we must deliberately build verb collisions with single-token
candidates.

### The lesson worth keeping

> **A clean result from an uncontrolled run is more dangerous than a messy
> one**, because it invites belief. Both defects pushed toward *more* order,
> not less.

---

## The four bugs we found in our own measuring equipment

### 🧠 Mental image

> Before trusting a speedometer, drive a measured mile. We did, four times,
> and the needle was wrong four different ways.

| id | what was broken | what it did |
|---|---|---|
| **P32-001** | the scorer returned `0.0` whenever the tokenizer glued the candidate onto the previous token (**44% of spots**) | **invented a null result** — reversion looked like 0.106 when it was 0.515 |
| **P32-002** | the prompt said "follow the token table" and **had no table in it** | measured habit, not instruction-following |
| **P32-003** | "take the first 240" over a list built family-by-family | scored **240 `dom`, 0 `blk`** — and `blk` was the fertility-controlled half |
| **P32-004** | only averages were saved | no re-analysis possible without re-running everything |

Each now has a test that **reproduces the bug on purpose** so it cannot
return.

### 🧠 Mental image for P32-001, the worst one

> You ask "`#` or `.`?" The tokenizer has already glued the answer onto the
> previous word, so the model is really choosing between `('#` and `('.` —
> and the old code, seeing no new token, scored both as *exactly zero*.
> Half the measurements were a flat line that looked like "no effect."

---

## What this adds up to

**Solid:**
- reversion ≈ 0.41–0.46 with the table present, tight intervals;
- `k*` ≈ 5–7 examples, 8–18% never crossing;
- holds in the fertility-controlled family;
- stable across three prompt phrasings;
- the measuring equipment is now tested, and tested against itself.

**Not solid:**
- one lexicon, one model family, one model size (0.5B);
- the rule effect's interval includes zero in 3 of 4 cells;
- the 3D-knowledge question is **not identifiable** with these materials;
- **no power analysis** — a null from the next run would be weak evidence.

### 🧠 The closing image

> We have built the runway, calibrated the instruments, taxied the plane, and
> flown one short hop in clear weather. It flew.
>
> We have **not** flown it loaded, in weather, or over distance. That is what
> Sol is for — and the preregistration is now written down **before** takeoff,
> so we cannot move the landing lights after we land.
