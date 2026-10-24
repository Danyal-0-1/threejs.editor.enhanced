# 05 — The mental image: new drivers, the same town, heard over the radio

> This continues the picture of Phase 3.3
> ([`../../phase3_3/heldout_results_explained/05_mental_image.md`](../../phase3_3/heldout_results_explained/05_mental_image.md)).
> The model is a **driver**. The language is a **town whose road signs were swapped**. Phase
> 3.3's held-out run was the **exam**: 21 drivers, 1,515 swapped corners per country, two
> countries.

---

## The new exam

```
 9 NEW DRIVERS     from other garages, some with enormous engines (up to ~550B)
 THE SAME TOWN     the same 3,030 corners, the same dictionary card, the same practice runs
 THE RADIO         we can't sit in their cars: we hear each turn over a radio link (the API)
```

Phase 3.3's drivers sat in our own cars, and we read the steering wheel directly (an fp32
output layer, exact to many decimals). The new drivers are in someone else's garage. We radio
the question and they radio back the answer.

---

## 🧠 Picture 1 — The radio has a little static

- **The dial is marked in eighths.** Most of the new drivers report the wheel's angle rounded to
  1/8, 1/16 or 1/32 of a turn (bf16 scores). When the two possible turns are closer than one
  mark, the report can say "dead ahead" (a tie) or even the wrong side.
- **Ask twice, hear slightly different numbers.** The garage answers many callers at once, and the
  arithmetic order depends on who else is on the line (batching). We asked each new driver
  about 300 corners a second time, hours later. Seven radios repeated themselves almost word for
  word: 2,061 of the 2,700 answers came back identical to the last digit. Two crackled: Gemma 4's
  angle sometimes came back several turns different (by up to 10.7 nats), and Qwen3.5 122B's
  almost never came back the same.
- **What it changes.** Mostly the corners where the driver was almost undecided, and those are
  few: 1–6% of corners lie within one mark of "dead ahead". Of the 2,700 corners asked twice, 39
  flipped side, and no driver's habit score moved by more than 1.3 points. The exception is the
  crackling radios: Gemma 4 flipped even at corners where it sounded sure.

---

## 🧠 Picture 2 — The habit survives, even in the giants

Hand each new driver the dictionary and send them through the 3,030 corners.

```
 with the dictionary open: share of corners where the old turn wins (each █ = 2 points)

 OLMo 3 32B Instruct           █████████████████████      41%
 Qwen3.5 27B                   █████████████████████      41%
 OLMo 3 7B Instruct            █████████████████████      42%
 Qwen3.5 397B-A17B             █████████████████████      43%
 OLMo 3 32B Think              ██████████████████████     43%
 DeepSeek-V4.1-Flash           ██████████████████████     43%
 Qwen3.5 122B-A10B             ██████████████████████     44%
 Qwen3-Coder 30B-A3B Instruct  ███████████████████████    45%
 Gemma 4 31B                   ████████████████████████   49%

 Phase 3.3's ten instruct drivers, the same corners: 43% … 51%
```

Every new driver, from the 7B OLMo to the roughly 550B DeepSeek, still takes the old road at
about two corners in five, with the dictionary open on the seat. The biggest engines (Qwen3.5
397B, DeepSeek) sit in the middle of the pack, and within the Qwen3.5 garage the 27B, 122B and
397B drivers are indistinguishable. Phase 3.3's drivers did the same. Newer and bigger did not
cure the habit.

---

## 🧠 Picture 3 — The dictionary nudges a little harder, and still doesn't steer

The dictionary pushes every new driver's wheel toward the right turn, a little harder than it
pushed Phase 3.3's (+0.34 to +0.86 nats, against +0.16 to +0.60). OLMo 3 Instruct gets the
hardest push (about +0.8) and still takes the old turn at 41–42% of corners.

An average push mostly changes the corners where the driver was nearly undecided. Most corners are decided
firmly one way or the other, so the habit rate falls by only 3–10 points. The dictionary helps;
it does not steer.

---

## 🧠 Picture 4 — Practice runs

Before each corner, show the driver some worked examples of the new town. Every driver improves
with practice: after 32 examples, 19–36% of corners still go the old way (Phase 3.3: 17–31%).

- **Quick learners.** Gemma 4 and Qwen3.5 27B switch after about two examples, like Phase 3.3's
  quickest.
- **Slow learners.** The OLMo 3 drivers on the `blk` roads: half their wrong corners need 12–15
  examples, more than any Phase 3.3 driver.
- **The first example confuses.** With one example, 7 of 9 new drivers take the old turn *more*
  often on the `dom` roads than with none. The improvement starts at two to four.

---

## 🧠 Picture 5 — Real driving (Arm B): better drivers, and some who never start

Now no forced choice: the driver gets a request ("move the meshes by (1, 2, 3)") and drives on
its own.

- **Gemma 4 drives furthest.** It reaches 54% and 46% of the corners. At the corners it reaches,
  it almost never takes the old turn (4%). Qwen3.5 397B is next.
- **Two OLMo 3 drivers mostly never start the engine.** Asked to drive, their first word is
  "over" (the end-of-turn token), so 290 and 334 of their 780 trips are empty. Qwen3.5 397B does
  the same on 48 trips.
- That is a quirk of how we asked (plain text, not the chat format these drivers were trained
  on), not proof that they cannot drive.

---

## 🧠 The one picture to keep

```
 newer, much bigger drivers, heard over a slightly noisy radio,
 still take the old turn at about two corners in five with the dictionary open.

   the dictionary nudges      ──►  helps, never steers
   practice                   ──►  helps, at different speeds
   size (7B → ~550B)          ──►  does not cure it
   the radio's static         ──►  matters for single corners (a lot, for two drivers),
                                   not for the habit rate
```
