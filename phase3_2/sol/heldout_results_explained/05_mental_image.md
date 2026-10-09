# 05 — The mental image: the exam results as pictures

> This continues the picture from
> [`../sol_experiment_explained/07_the_picture.md`](../sol_experiment_explained/07_the_picture.md).
> The model is a **driver**. The language is a **town whose road signs were swapped**. The
> held-out run was the **exam**: new towns, a second country, 21 drivers.

---

## The exam room

```
 21 DRIVERS          small cars (0.5B) ………………………………… trucks (72B)
 5 NEW TOWNS         a quarter of the signs swapped (d25) … three quarters swapped (d75)
 2 COUNTRIES         "dom": streets like home      "blk": a road system never driven
 THE RULE CARD       a dictionary of the new signs on the dashboard
```

---

## 🧠 Picture 1 — The habit survives every engine size

Hand each driver the dictionary and send them through 1,515 swapped corners.

```
   small car  █████████░░░░░░░░░░░  ~44% wrong turns
   truck      ██████████░░░░░░░░░░  ~48% wrong turns
                (the 72B truck is no better than the 0.5B car)
```

Every driver, 0.5B to 72B, takes the **old** turn at 40–56% of corners, even with the
dictionary in view. A bigger engine does not break the habit (D11: no trend survives).

---

## 🧠 Picture 2 — The dictionary nudges; it doesn't steer

Take the dictionary away and the wrong turns rise from ~49% to ~55% (the average over all
drivers).

- The dictionary always nudges the wheel the right way, by about +0.35 nats, a 1.4× odds
  shift.
- A nudge only fixes corners where the driver was *almost* right already.
- A blank card of the same size does nothing extra (the length control), so it is the *words*
  on the card that help, not the card itself.

---

## 🧠 Picture 3 — Practice runs: quick to switch, slow to settle

Before each corner, let the driver watch 0, 1, 2, 4, 8, 16 or 32 practice runs.

```
 practice runs:    0     1     2     4     8     16    32
 typical corner:   ✗     ✗     ✓     ✓     ✗     ✓     ✓      ← switches early, slips, settles
```

- **First correct turn:** after about **2** practice runs (the median among corners that
  switch).
- **Turns correctly *from then on*:** after about **8** (among corners whose switch lasts).
- **Never learned in 32 runs:** **1 corner in 5**.
- **The familiar country (`dom`)** takes 1.4–4.6 runs to switch; **the strange one (`blk`)**
  takes 3–12.
- **The learning curves wobble, and not a little.** 6 in 10 curves drop by more than an odds
  factor of 2.7 at some step. **1 in 3 corners that switched slips back later**, by a median
  of −0.76 nats ([09 §3.3](09_conclusions_claim_strength_and_venues.md)).

---

## 🧠 Picture 4 — The co-pilot knows where the driver will slip (H4, confirmed)

Every instruction-tuned driver has a twin: the base model it was trained from.

- **The warning light.** Before the drive, the twin *hesitates* at some corners.
- **The confirmatory result.** Those are exactly the corners where the driver goes wrong:
  AUROC 0.76–0.96, all 10 twins, both countries.
- **It is about the exact corner.** "Left turns are hard in general" (the role-level guess)
  predicts worse than the twin's warning about *this* corner.
- **It is about *this* driver's history** *(exploratory)*. A twin from another family warns
  too, but only about half as well (a median 46% of the signal). Some corners trip up
  everyone; the rest are this driver's own ([09 §3.1](09_conclusions_claim_strength_and_venues.md)).

```
   twin's hesitation:  low ───────────────────────────────► high
   driver's error:     rare ──────────────────────────────► common      (rank agreement 0.76–0.96)
```

---

## 🧠 Picture 5 — Punctuation signs vs word signs *(exploratory)*

```
   "#" and "." signs        ●  switch after ~1–3 runs        rarely wrong in real driving (9–11%)
   keyword signs (mesh)     ●●  ~3–9 runs                     sometimes wrong (18–23%)
   verb signs (duplicate)   ●●●●  ~7–11 runs, 1/3 never       often wrong (29–43%)
```

Words carry meaning the driver won't let go of. Two different tests agree on the ordering:
the practice runs and the real drives.

**A town where only a quarter of the signs changed is *harder* to adapt to than one where
most changed.** When almost everything looks like home, home habits win. *(Exploratory: one
town per level.)*

---

## 🧠 Picture 6 — Real driving (Arm B)

Now the driver plans the whole route from a spoken request, with the dictionary and 4 practice
runs.

- **Most drivers don't even take the same route.** Only 13.5% of corners are reached on the
  target route: 3% for small cars, about 30% for the 72B truck.
- **At a reached swapped sign, about 1 in 5 drivers takes the old turn.**
- **Only 1 in 10 whole routes is exactly right.**

```
   reach the corner? ──no (86%)──► (can't judge this corner)
          │yes (14%)
          ▼
   old turn? ──yes (20%)──► silent wrong program
          │no
          ▼
       correct turn
```

---

## 🧠 Picture 7 — Repainting signs (H5, not supported)

**The plan:** repaint only the 3 most dangerous signs in a brand-new alphabet, so that a wrong
turn hits a dead end (a loud error) instead of a real street (a silent error).

**What happened:**

```
   repaint 3 "most dangerous"   ≈  repaint 3 at random    (targeted wins 43 of 100 towns)
   repaint ALL swapped signs    →  silent wrong turns: 0   (and wrong turns drop by two-thirds)
```

**Why.** In these towns the signs were *swapped*, not invented: every old sign still points
to *some* real street. Repaint one sign, and its old wording still leads somewhere real, so
the error stays silent. Only repainting **every** swapped sign removes all the familiar
wordings.

**A side effect.** Repainting signs changes the dictionary, and drivers then also improved at
corners nobody repainted. That shows up as the "per-symbol" gain.

---

## 🧠 The one picture to keep

```
                    THE HABIT                      THE FIX THAT WORKS
   rule card ──► nudges, rarely steers        practice: switch at ~2, settle at ~8 (among switchers)
   bigger engine ──► same habit               repaint EVERYTHING ──► no silent errors
                                              repaint a few ──► no better than random

                    THE WARNING THAT WORKS
   the base twin's hesitation predicts the driver's mistakes, corner by corner (confirmed)
```

**In one sentence:** code models lean on familiar spellings at every size; rules and examples
help, but unevenly and unstably; their failures are predictable from the base model; and in a
permuted language, only a complete respelling removes the silent errors.

**The same picture with a real driver, and the brain systems involved:**
[10 — the human mirror](10_humans_and_the_brain.md).
