# 07 — The picture: the Sol experiment as one image

Read this when you want the whole thing in your head at once. Every image
maps onto something real in the code, and the arrow (→) names it. The numbers
are the real ones.

---

## The one-line version

> We measure how often a code model falls back on a familiar-but-wrong
> spelling. The measuring machine is now built so that it cannot fool us: it
> cannot peek at the exam, cannot lose its notes when the power goes out, and
> cannot report a number it did not measure.

---

## 1. The driver and the swapped road signs

A model learned to drive in **CSS-land**, where `.` means *class* and `#`
means *id*. We send it to **3DOM-land**, where some signs have been swapped:
there, `#` means *class*. Nothing crashes when it takes the wrong turn. The
program is still valid; it just edits the wrong object. That is the German
"Gift": a perfectly good word that means poison.

Every spot where a swapped sign matters is an **intersection** (→ a *site*).
At each one the driver leans toward the habit or toward the new rule:

```
   the habit (CSS)                                   the new rule (3DOM)
   ◄──────────────────────────── M ────────────────────────────►
   M = −4  "strong habit"          M = 0          M = +4  "follows the rule"
              reversion  ◄─────────┤├─────────►  correct
```

**M** (→ `m_seq`) is how hard it leans toward the correct turn. Below zero,
the habit wins (→ *reversion*).

Real example from the one GPU run, at intersection `t000` (a class selector):
the rule says `#`, the habit says `.`. With the rulebook in hand, **M = +0.647**:
a slight lean toward the rule.

---

## 2. Five ways to test the driver

```
                      ┌──────────────────────────────┐
 Arm A                │ rulebook / no rulebook /     │  does the rulebook help?
                      │ same-thickness blank booklet │
                      └──────────────────────────────┘
                      ┌──────────────────────────────┐
 Extinction           │ 0,1,2,4,8,16,32 practice     │  when does the habit die?  → k*
 (primary)            │ trips before the test        │
                      └──────────────────────────────┘
                      ┌──────────────────────────────┐
 H4                   │ a mechanic predicts the bad  │  can we predict WHERE it fails?
                      │ intersections from a sister  │
                      │ car (the base model)         │
                      └──────────────────────────────┘
                      ┌──────────────────────────────┐
 H5                   │ repaint only the dangerous   │  is targeted repair cheaper
                      │ signs vs random vs all signs │  per sign changed?
                      └──────────────────────────────┘
                      ┌──────────────────────────────┐
 Arm B                │ let it drive freely: does it │  reach it? then turn right?
                      │ even reach the intersection? │  (two questions, never one)
                      └──────────────────────────────┘
```

- **The blank booklet** (→ `norule_lenmatched`): the no-rulebook prompt is a
  third shorter (1,014 vs 1,527 characters; 237 vs 298 tokens), so "the
  rulebook helped" could just mean "a longer prompt helped". The blank booklet
  pads the no-rulebook prompt to the rulebook's thickness (307 vs 298 tokens)
  without adding its content.
- **The sister car** (→ base model): H4 predicts the instruct model's failures
  from the base model's margins, before the instruct model ever drives.

---

## 3. The four protections

### 🧠 The sealed exam envelope (development / held-out split)

```
  PRACTICE ROADS (development)     │  EXAM ROADS (held-out)  ── sealed envelope ──
  4 lexicons, dom, 2 sizes         │  5 lexicons, dom + blk, 11 models
                                   │
  1. practise, analyse             │
  2. write the grading rules       │
     IN INK  (DEV_FREEZE.json,     │
     read-only + fingerprint)      │
  3. sign the envelope:  "I have finished the development analysis and will not change it"
                                   │  4. open, drive, grade
```

- **Opening the envelope early is impossible.** Every exam-road command checks the signature
  first (→ `HELDOUT_UNLOCK.json`).
- **The envelope re-checks the ink.** If anyone edits the grading rules after it is
  opened, it refuses again (→ source, materials and model pins re-checked on
  every held-out access).
- **`blk` is an exam road we drove on during practice.** It is no longer a clean
  exam road (→ EXPLORATORY-CONTAMINATED / HELDOUT-WEAK-FAMILY). No clean road
  with a *new layout* exists, so "works on a new grammar" (H4 criterion C3) is
  **NOT TESTABLE** yet.

### 🧠 The answer key in the practice packet (leakage)

The old practice trips were always the first 32 routes. **82 of the 120**
tested intersections lay *on* those routes, so the driver had seen the answer
before being asked. The "it takes ~6 examples" headline was therefore partly copying,
and it is **withdrawn**.

Now practice trips never include the tested route. Checked over the real
development plan: 400 sites, 2,800 practice packets, **0 leaks**. Under the old
rule, 177 of those 400 would have leaked.

### 🧠 The logbook with sealed pages (crash safety)

```
  page 1 ✔ sealed   page 2 ✔ sealed   page 3 ✎ writing…   page 4 ☐   page 5 ☐
                                          ▲
               "5 minutes left on the rental" (Slurm SIGUSR1)
               → finish the current line, tear out the unfinished page 3,
                 write INTERRUPTED, leave (exit 4)
               → next rental: redo page 3, then 4, 5 …
```

- **A sealed page** (→ shard) is written whole or not at all, and carries a fingerprint
  (sha256) of its contents. A torn page is detected and rewritten.
- **The final logbook is byte-for-byte identical** whether or not the work was
  interrupted (→ tested). Also checked with real signals: SIGUSR1 mid-run gave
  exit 4, the resumed run's 960 rows matched an uninterrupted run byte for byte,
  and a real SIGTERM recorded `INTERRUPTED, signal 15`.
- **Two drivers writing the same page at once** (→ Slurm array tasks on
  different nodes) each draft on their own sheet, so they can never scribble
  over each other (→ `atomic_write_text`).

### 🧠 The fine-grained speedometer (fp32 output head)

The question is only "above or below zero?". The model's native bf16 ruler has
marks every **1/16 nat**. Near zero, a coarse ruler can put you on the wrong
side.

```
   native bf16 :  +0.6250   (exactly 10/16)
   fp32 head   :  +0.6473
```

On three development sites, every reading from the fine ruler agreed in sign
with the coarse one, within 0.005–0.042 nats.

---

## 4. The statistics as pictures

### 🧠 Families, not strangers (template clusters)

Intersections from one template are **siblings**: same road layout, different
corner. Twenty siblings are not twenty independent witnesses. So uncertainty is
estimated by **resampling whole families**.

The old bug: when a family was drawn twice, it was **counted once**, which made
the error bars too narrow. The textbook check: families tA = 1 and tB = 3,
drawn [tA, tA, tB], should average **5/3**. The old code said **2.0**.

After the fix, **all four** earlier rule-effect intervals include zero.

### 🧠 "More than 32" is an answer, not a blank (censoring)

How many practice trips until the driver turns correctly?

- Some turn correctly with **0** trips (→ `k* = 0`, *already correct*).
- Some still have not after **32** (→ *censored*: we know only "more than 32").
- Dropping the "more than 32" drivers would make the habit look easier to
  break than it is. Kaplan–Meier is the method that counts them properly.

Real smoke example, six intersections:

```
 t005  sigil    +0.69 → +2.85 → +1.77 → +1.90 → +5.70   correct from the start  k*=0
 t011  keyword  −2.57 → −1.70 → +0.71 → +0.41 → −1.02   crossed at ≈1.7, then fell back
 t004  keyword  −5.48 → −6.30 → −6.18 → −5.82 → +2.53   crossed at ≈6.8
 t002  verb     −4.44 → −3.96 → −2.80 → −2.26 → −1.65   never crossed (censored)
            shots:  0       1       2       4       8
```

### 🧠 The wobbly needle (non-monotone curves)

Adding examples does not move the needle smoothly. In the audited Phase 3.3
data, **237 of 240** curves wobbled. "The first time it crossed zero" is
therefore noisy. Each curve also records "crossed and **stayed** crossed"
(→ `sustained_k`). For `t011` above, the first crossing is ≈ 1.7, but it never
stays crossed.

---

## 5. Where things stand (2026-10-07)

| | |
|---|---|
| the machine | built and tested: all 139 Sol-pipeline tests pass **locally** (not yet re-run on Sol since the 2026-10-07 changes). Rehearsed end to end on the fake scorer |
| the practice season on Sol (`dev-20261006a`) | **done**. Four drivers (Qwen2.5-Coder 0.5B and 1.5B, base and instruct) ran on A100s: 10,224 + 16,000 readings in about 17 GPU-minutes. Practice roads only, so everything below is *exploratory* |
| the old habit | even with the rulebook on the dashboard, the drivers take the old turn at **39–58%** of intersections |
| the rulebook | helps a little on average (+0.08 to +0.36 nats), but only **1 of 32** error bars clears zero |
| breaking the habit | for intersections first taken wrongly, the median is **3.6–6.2** practice trips. 13–22% never turned within 32, and about 98% of needles wobble |
| spotting the risky intersections (H4) | AUROC **0.87 / 0.94**. It beats both simple guesses (criteria C1 and C2), on practice roads only |
| the scorekeeping | corrected on 2026-10-07: tied scores no longer depend on the order of the file (D9). Only the simple guesses' AP and precision@k moved; every headline number stayed |
| is the exam big enough? | for the rulebook question, **no**. Siblings agree (ICC 0.252), so 80 families give about **25%** power, not the 99% the old report printed. For H4, yes: an AUROC of 0.62 or more is detected 80% of the time |
| bigger drivers | 10 drivers from 7B to 72B were added, for the exam only (D10). All are downloaded and pinned; the 72B pair drives with two GPUs |
| model access | all 11 original checkpoints are downloaded and pinned; the Llama-3.2-1B pair was approved on 2026-10-07 |
| old "~6 examples" headline | **withdrawn** (leakage plus two definition errors) |
| "works on a new grammar" | **not testable** with these materials |
| the grading rules | **in ink** since 2026-10-07: `DEV_FREEZE.json`, written by job 64942745 |
| the exam envelope | **opened** on 2026-10-07 at the investigator's direction. The exam (`heldout-20261007a`) runs one driver at a time: about 2–4 days |

Still to come, in order:

1. the exam for all 21 drivers;
2. Arm B and H5;
3. the final export;
4. the interpretation.

---

## 6. The one picture to keep

```
 practice roads ──► grading rules in ink ──► sign & open ──► exam roads ──► report
    (dev runs)         (DEV_FREEZE)          (UNLOCK)        (held-out)    (19 CSVs,
       ▲                                                          │       12 plots,
       │                                                          │       10 reports)
       └──── any change after the ink dries = a new practice season ◄──┘
```
