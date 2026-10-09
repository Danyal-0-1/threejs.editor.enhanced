# 10 — The human mirror: people make the same mistake, and where it happens in the brain

> **What this is.** A plain-language picture of the results, through people. It continues the
> driver picture in [05](05_mental_image.md): now the driver is a real person, and we ask which
> brain systems do what the model does.
>
> **What this is not.** A claim that a transformer works like a brain. The analogy is about the
> **problem** and the **behaviour**, not the **mechanism**. Both a person and the model have:
>
> 1. a strong learned default;
> 2. a weaker rule held in mind;
> 3. practice that helps without erasing the default.
>
> The brain regions below are where cognitive neuroscience locates these three things in
> people. A transformer has no such regions. §5 lists where the analogy breaks.

---

## 0. One scene holds the whole study: Alex rents a car in London

Alex has driven on the right for fifteen years in Arizona. In London, the rental desk hands
Alex a card:

```
   ┌────────────────────────────────────────────────┐
   │ KEEP LEFT.                                     │
   │ Indicator: RIGHT stalk.   Wipers: LEFT stalk.  │   ← the token table
   └────────────────────────────────────────────────┘
```

| the model (3DOM) | Alex in London |
|---|---|
| pretraining on millions of CSS and jQuery files | fifteen years of driving on the right |
| the token table in the prompt | the card on the dashboard |
| a decision site: a place where a reassigned symbol must be written | a junction, a roundabout, the moment to signal |
| a **reversion**: writes the old spelling `mesh` | pulls into the right lane; flicks the wipers to signal |
| a **silent error**: a valid program that does the wrong job | the wipers work perfectly; they just aren't what Alex meant |
| worked examples in the prompt | the first days of driving |
| base model → instruct model | Alex's own driving history → Alex after a London driving lesson |
| a bigger model | a more experienced driver |
| respelling symbols (H5) | relabelling or redesigning the car's controls |

Every result of the study is one moment of Alex's week.

---

## 1. Ten moments, ten results

### Moment 1 — The habit (the prior)

- **Alex:** turning into the right lane takes no thought at all. The body does it.
- **The model:** before any table, the base model strongly prefers the familiar spelling. At
  the worked site (§2) it rates `mesh` **78 times** likelier than the new spelling `light`.
- **The name for it:** a *habit*, or *automaticity*: a response triggered by the situation, not
  chosen by the goal (Wood & Rünger, 2016).
- **In the brain:**
  - the **basal ganglia**, especially the **dorsolateral striatum** (putamen), with the
    motor cortex, run well-practised stimulus → response habits (Yin & Knowlton, 2006; in
    humans, Tricomi et al., 2009);
  - for written words, the **visual word form area** (left ventral occipitotemporal cortex)
    recognizes familiar spellings automatically (Dehaene & Cohen, 2011).

### Moment 2 — The card (the token table)

- **Alex:** reads "KEEP LEFT" and keeps it in mind.
- **The model:** the table moves every model toward the new spelling (+0.16 to +0.62 nats).
  Even so, models still choose the old spelling at **40–56%** of sites. At the worked site
  the base model goes from 78× for `mesh` down to **11.9×**: helped, still wrong.
- **The name for it:** a *task set*, a rule held in working memory. The textbook case is the
  **Stroop test**. Shown the word **BLUE** printed in red ink and told to name the ink,
  people know the rule, yet the word slows them and sometimes wins (Stroop, 1935; MacLeod,
  1991).
- **In the brain:** the **dorsolateral prefrontal cortex** (DLPFC) holds the current rule and
  biases processing toward it (Miller & Cohen, 2001; MacDonald et al., 2000).

```
   habit  ███████████████████  pulls toward `mesh` / the right lane
   rule   ███████████           pulls toward `light` / the left lane      → the habit still wins half the time
```

### Moment 3 — The junction (a decision site): conflict

- **Alex:** at a roundabout, the habit says *right* and the card says *left*. Alex hesitates.
- **The model:** at the worked site, the instruct model is at a coin flip: 6.2% for `mesh`
  against 6.0% for `light` (M = −0.034).
- **The name for it:** *response conflict*.
- **In the brain:** the **dorsal anterior cingulate cortex** (dACC) detects that two
  responses compete and calls in more control from the prefrontal cortex (Botvinick et al.,
  2001; MacDonald et al., 2000).
- **The difference that matters:** a person in conflict **slows down and looks again**. The
  model has no conflict monitor. It writes the likelier token immediately, even at 6.2% against
  6.0%. A checker or a "think first" step would be the model's second look.

### Moment 4 — The slip (a reversion)

- **Alex:** tired, pulling out of a car park, drives into the right lane. Or reaches to signal
  and the wipers sweep the windscreen.
- **The model:** writes `mesh`. In the new language, `mesh` means "group", so the program now
  selects groups instead of meshes.
- **The name for it:** a *capture error*, a classic action slip. A strong, frequent routine
  takes over a weaker intended one when attention lapses (Norman, 1981; Reason, 1990).
- **In the brain:** stopping a habitual response needs a brake: the **right inferior frontal
  gyrus**, the **pre-supplementary motor area** and the **subthalamic nucleus** (Aron et al.,
  2014). If the brake comes too late, the habit runs.
- **In the model:** there is no separate brake. The rule must outvote the habit inside the
  same next-token computation.

### Moment 5 — Nobody notices (silent errors)

- **Alex:** the wipers do exactly what that stalk does, so nothing beeps. The wrong lane is
  noticed only when a car comes the other way.
- **The model:** the program with `mesh` parses and runs. No error message, just the wrong
  objects changed. Every site in this study is built this way: the old spelling *still
  means something*.
- **The name for it:** an unnoticed error. People notice errors through an error signal, the
  **error-related negativity**, generated in the **anterior cingulate** when the action
  clashes with the intention (Gehring et al., 1993). A silent slip produces no clash to
  notice.
- **The design answer:** a **forcing function**, which makes the wrong action impossible or
  obvious (Norman, *The Design of Everyday Things*). London paints **LOOK RIGHT** on the road at
  crossings: a reminder placed exactly at the decision site.

### Moment 6 — Practice, then relapse (worked examples)

- **Alex:**
  - **day 1:** slips everywhere;
  - **day 3:** mostly right;
  - **day 5, late at night on an empty road:** drifts right again.
- **The model:**
  - sites that switch do so after a median of **about 2** examples, but a switch that lasts
    takes **about 8**;
  - **31%** of switched sites later fall back below zero, by a median of **−0.76 nats**
    ([09 §3.3](09_conclusions_claim_strength_and_venues.md));
  - **18%** never switch within 32 examples.

```
   examples:     0    1    2    4    8    16   32
   one site:     ✗    ✗    ✓    ✓    ✗    ✗    ✓        ← switched at ~1.7, relapsed at 8 and 16
```

- **The name for it:** *extinction is new learning, not forgetting*. The old habit survives
  underneath. It returns with time (*spontaneous recovery*) and in a new context
  (*renewal*) (Bouton, 2004).
- **In the brain:**
  - the **hippocampus** learns new arbitrary associations fast. The neocortex and striatum
    learn slowly, and keep the old knowledge (complementary learning systems: McClelland et
    al., 1995).
  - extinction memories depend on the **ventromedial prefrontal cortex**, which inhibits the
    old response rather than deleting it. This is shown mostly for fear extinction, in rats
    (the infralimbic cortex) and in people (Milad & Quirk, 2002).
- **In the model:** worked examples change the *activations* in this one prompt, not the
  *weights*. The prior is intact and ready to return. This is the complementary-learning-systems
  picture (fast learning on top of slow weights), which has been carried over to artificial
  agents (Kumaran, Hassabis & McClelland, 2016). Here the in-context examples play the fast
  part, but nothing is stored after the prompt ends.

### Moment 7 — Your own history predicts your slips (H4, and the inheritance check)

- **Alex:**
  - Some junctions trip up *every* visitor, roundabouts above all.
  - Others trip up only drivers from Arizona, because of *where Alex learned to drive*.
  - A London driving lesson helps, but the slips it leaves are still Alex's own.
- **The model:**
  - **confirmatory:** the base model's hesitation predicts where its instruction-tuned twin
    reverts, site by site (AUROC 0.76–0.96 in all 20 groups);
  - **exploratory:** the pooled base models of *other* families predict only about **half
    as well** (a median 46% of the signal above chance). The rest is inherited from the
    model's own base
    ([09 §3.1](09_conclusions_claim_strength_and_venues.md)).
- **The name for it:** *first-language transfer*. A learner's native language predicts many,
  not all, of their second-language errors (contrastive analysis: Lado, 1957). A Spanish
  speaker and a Japanese speaker make different English mistakes; some mistakes everyone
  makes.
- **In the brain:** each person's habits are written by *their own* learning history.
  Dopamine **prediction-error** signals from the midbrain (VTA and substantia nigra) train
  the striatum (Schultz, Dayan & Montague, 1997). Later teaching adds control on top; it
  does not rewrite the old habits.
- **In the model:** pretraining writes the habits, and instruction tuning is the later lesson.

### Moment 8 — Experience does not protect (scale)

- **Alex:** a driver with thirty years behind the wheel slips just like one with two. The
  habit is *more* automatic, not less.
- **The model:** 72B models revert as often as 0.5B ones. The pre-specified scale analysis
  finds no trend, and its intervals rule out a fall of more than about 4 points per tenfold
  increase in size.
- **The name for it:**
  - Stroop interference appears once reading becomes automatic, and never disappears in
    skilled adult readers (MacLeod, 1991);
  - *Einstellung*: experience with one solution blocks a simpler new one (Luchins, 1942).
- **In the brain:** with practice, control of a behaviour shifts toward the dorsolateral
  striatum. The habit becomes faster and harder to override (Graybiel, 2008; Dolan & Dayan,
  2013).

### Moment 9 — Fixing the car (H5)

- **Alex, option 1:** stickers on the three stalks Alex confuses most. It helps little: the
  other swapped controls still trap Alex.
- **Alex, option 2:** a vehicle with *completely* new controls, such as a joystick. There is
  no familiar action to fall into. Alex is slow and careful, but never *silently* does the
  old thing.
- **The model:**
  - respelling the 3 riskiest roles is no better than respelling 3 at random (43 of 100
    cells);
  - respelling *every* reassigned role into an unfamiliar alphabet cuts reversion at those
    sites from **48% to 16%**, and leaves **no silent errors**.
- **The name for it:** *Osgood's similarity paradox*. Interference is greatest when the
  situations look the same but the responses differ (Osgood, 1949). A *partly* changed
  system is the worst case, and a completely new one is easier.
- **The same effect, exploratory:** languages where only 25% of symbols changed were the
  hardest to adapt to.

### Moment 10 — Punctuation is quick to relearn; words are not (exploratory)

- **Alex:** learns a new switch in a day. But a word that changed meaning stays a trap for
  years. These are the *false friends*: Spanish *embarazada* means "pregnant", not
  "embarrassed"; German *Gift* means "poison".
- **The model:** punctuation (sigils) switches after about 1.3 examples (dom) and 3.2 (blk).
  Words used as verbs take about 6.6 and 11.4. In free generation, verbs revert most (29–43%
  of reached sites).
- **A careful note:** this matches the human pattern, but the study cannot say *why*. Roles
  also differ in length and frequency.

---

## 2. The worked site, in human terms

**Site:** `dom:d50s1:t011:T_TYPE_MESH:0`, from the development run (lexicon `d50s1`). Full
trace: [`EXPERIMENT_IN_ONE_FILE.md §3`](../sol_experiment_explained/EXPERIMENT_IN_ONE_FILE.md).

**The town's new sign rules:** the word **`light`** now means *mesh*, and the word **`mesh`**
now means *group*. Here `mesh` is a false friend: a real, valid word with a new meaning.

| moment | the model (Qwen2.5-Coder-0.5B) | M (nats) | in human terms |
|---|---|---:|---|
| no card | base, no table | −4.36 | "Of course it's `mesh`": 78× for the habit |
| card on the dashboard | base, with the table | −2.48 | reads the card, still 11.9× for the habit |
| after a driving lesson | instruct, with the table | −0.03 | torn: a coin flip at the junction |
| a few practice drives | base, examples added | crosses 0 at ~1.7 examples | "got it" |
| tired, a new road | base, 8 and 16 examples | below 0 again | relapse |
| a month later | base, 32 examples | above 0 | settled |

**Why the slip is dangerous.** Writing `mesh` here selects *groups* instead of meshes. The
program runs and no one is told. That is the wiper stalk, not a crash.

---

## 3. The brain map on one page

| in the model | in a person | main brain system | classic evidence | what we measured |
|---|---|---|---|---|
| pretrained weights (the prior) | habits; familiar word forms | **dorsolateral striatum** (putamen); **visual word form area** | Yin & Knowlton 2006; Tricomi et al. 2009; Dehaene & Cohen 2011 | base-model margins; 40–56% reversion |
| the token table in the prompt | a rule held in mind | **dorsolateral prefrontal cortex** | Miller & Cohen 2001; MacDonald et al. 2000 | +0.16 to +0.62 nats from the table |
| a margin near zero | conflict between two responses | **dorsal anterior cingulate** | Botvinick et al. 2001 | M = −0.03 at the worked site |
| *(nothing separate)* | a brake on the habitual response | **right inferior frontal gyrus**, pre-SMA, subthalamic nucleus | Aron et al. 2014 | reversion despite the rule |
| *(nothing; a parser catches only loud errors)* | noticing one's own error | **anterior cingulate** (error-related negativity) | Gehring et al. 1993 | silent errors by design |
| examples in the prompt (activations change, weights don't) | fast learning of new associations | **hippocampus** | McClelland et al. 1995; Kumaran et al. 2016 | switch after ~2 examples (among switchers) |
| relapse after a switch | spontaneous recovery, renewal | **ventromedial prefrontal cortex** holding the override | Bouton 2004; Milad & Quirk 2002 | 31% of switches fall back |
| the training signal (off during the test) | learning from prediction errors | **dopamine neurons** (VTA and substantia nigra) | Schultz et al. 1997 | the prior stays fixed during the test |
| base model → instruct model | first language → second language | a personal learning history | Lado 1957 | H4: AUROC 0.76–0.96; inheritance |

```
                  A PERSON                                  THE MODEL
   ┌───────────────────────────────────┐      ┌───────────────────────────────────┐
   │ rule:      prefrontal cortex      │      │ rule:      token table in prompt  │
   │ conflict:  anterior cingulate     │      │ conflict:  (no monitor)           │
   │ brake:     inferior frontal gyrus │      │ brake:     (none)                 │
   │ habit:     striatum, word areas   │      │ habit:     pretrained weights     │
   │ examples:  hippocampus            │      │ examples:  in-context only        │
   └───────────────────────────────────┘      └───────────────────────────────────┘
         separate systems negotiate                one forward pass settles it
```

**The one-line difference:** a person *negotiates* between habit and rule using separate
systems for conflict and braking, and can stop to think. The model must settle it in **one
computation**. That may be why the table helps only a little, and why a checker that turns
silent errors into loud ones is the strongest fix.

---

## 4. Simple experiments to feel it yourself (good for a talk)

1. **Stroop.** Name the ink colour, not the word: **RED** printed in blue ink, **GREEN**
   printed in red. Feel the pull (Moments 2–4).
2. **Swapped keys.** Swap two keys in your keyboard settings for 10 minutes. Count your
   slips at first, after practice, and when you are tired (Moments 4 and 6).
3. **Swapped built-ins.** In Python, run `print, len = len, print`, then write a short
   function. You will reach for the old meanings (the exact task of Miceli-Barone et al.,
   2023; Moment 7).
4. **The backwards bicycle.** A popular demonstration: a bicycle whose steering is reversed
   took one adult about eight months to learn, and riding a normal bike was briefly hard
   afterwards (Sandlin, *Smarter Every Day*, 2015). It is an anecdote, but it shows Moments
   1, 6 and 9 in one video.

---

## 5. Where the analogy breaks

| the analogy says | but |
|---|---|
| a habit system and a rule system | a transformer has no separate systems. Habit and rule meet in the same weights and the same forward pass |
| tiredness causes slips | the model is not tired. Greedy decoding gives the same answer every time |
| errors can be noticed | the model never notices; only a parser or a test can |
| practice | in-context examples are not practice. Nothing is stored after the prompt ends |
| experience | more parameters is not more years of driving |
| a driving lesson | instruction tuning changes the weights; a lesson changes a brain in very different ways |
| brain regions | we measured behaviour only. Nothing in this study is neural |

**So the safe claim is:** "the models show the behavioural signature of habit capture, partial
rule control and extinction with relapse, which in people involve these systems." Never
"the model has a striatum".

---

## 6. How to use this in the paper

**In an NLP or ML paper:** one paragraph in the discussion, no brain regions, three or four
citations. A draft:

> The pattern resembles well-known human phenomena. A strong, practised response captures
> behaviour despite an explicitly known rule, as in Stroop interference and capture errors
> (MacLeod, 1991; Norman, 1981). Interference is worst when the new system resembles the
> old (Osgood, 1949). Relearning does not erase the old response, which returns
> intermittently (Bouton, 2004). As with first-language transfer, where a model fails is
> predictable from its own learning history.

**In a CogSci paper:** this document is the frame. The strongest version adds a small human
study, with programmers given the same token table and the same collision sites, to measure
reversions and response times side by side with the models
([09 §5–6](09_conclusions_claim_strength_and_venues.md)).

---

## References

These are classic sources, cited from memory; check the details before citing. The two ML
papers were checked online on 2026-10-09.

- Aron, A. R., Robbins, T. W., & Poldrack, R. A. (2014). Inhibition and the right inferior frontal cortex: one decade on. *Trends in Cognitive Sciences, 18*(4), 177–185.
- Botvinick, M. M., Braver, T. S., Barch, D. M., Carter, C. S., & Cohen, J. D. (2001). Conflict monitoring and cognitive control. *Psychological Review, 108*(3), 624–652.
- Bouton, M. E. (2004). Context and behavioral processes in extinction. *Learning & Memory, 11*(5), 485–494.
- Dehaene, S., & Cohen, L. (2011). The unique role of the visual word form area in reading. *Trends in Cognitive Sciences, 15*(6), 254–262.
- Dolan, R. J., & Dayan, P. (2013). Goals and habits in the brain. *Neuron, 80*(2), 312–325.
- Gehring, W. J., Goss, B., Coles, M. G. H., Meyer, D. E., & Donchin, E. (1993). A neural system for error detection and compensation. *Psychological Science, 4*(6), 385–390.
- Graybiel, A. M. (2008). Habits, rituals, and the evaluative brain. *Annual Review of Neuroscience, 31*, 359–387.
- Kumaran, D., Hassabis, D., & McClelland, J. L. (2016). What learning systems do intelligent agents need? Complementary learning systems theory updated. *Trends in Cognitive Sciences, 20*(7), 512–534.
- Lado, R. (1957). *Linguistics Across Cultures*. University of Michigan Press.
- Luchins, A. S. (1942). Mechanization in problem solving: The effect of Einstellung. *Psychological Monographs, 54*(6).
- MacDonald, A. W., Cohen, J. D., Stenger, V. A., & Carter, C. S. (2000). Dissociating the role of the dorsolateral prefrontal and anterior cingulate cortex in cognitive control. *Science, 288*(5472), 1835–1838.
- MacLeod, C. M. (1991). Half a century of research on the Stroop effect: An integrative review. *Psychological Bulletin, 109*(2), 163–203.
- McClelland, J. L., McNaughton, B. L., & O'Reilly, R. C. (1995). Why there are complementary learning systems in the hippocampus and neocortex. *Psychological Review, 102*(3), 419–457.
- Miceli-Barone, A. V., Barez, F., Konstas, I., & Cohen, S. B. (2023). The Larger They Are, the Harder They Fail: Language Models do not Recognize Identifier Swaps in Python. *Findings of ACL 2023*. [ACL Anthology](https://aclanthology.org/2023.findings-acl.19)
- Milad, M. R., & Quirk, G. J. (2002). Neurons in medial prefrontal cortex signal memory for fear extinction. *Nature, 420*, 70–74.
- Miller, E. K., & Cohen, J. D. (2001). An integrative theory of prefrontal cortex function. *Annual Review of Neuroscience, 24*, 167–202.
- Norman, D. A. (1981). Categorization of action slips. *Psychological Review, 88*(1), 1–15.
- Norman, D. A. (2013). *The Design of Everyday Things* (revised ed.). Basic Books.
- Osgood, C. E. (1949). The similarity paradox in human learning: A resolution. *Psychological Review, 56*(3), 132–143.
- Reason, J. (1990). *Human Error*. Cambridge University Press.
- Schultz, W., Dayan, P., & Montague, P. R. (1997). A neural substrate of prediction and reward. *Science, 275*(5306), 1593–1599.
- Stroop, J. R. (1935). Studies of interference in serial verbal reactions. *Journal of Experimental Psychology, 18*(6), 643–662.
- Tricomi, E., Balleine, B. W., & O'Doherty, J. P. (2009). A specific role for posterior dorsolateral striatum in human habit learning. *European Journal of Neuroscience, 29*(11), 2225–2232.
- Wood, W., & Rünger, D. (2016). Psychology of habit. *Annual Review of Psychology, 67*, 289–314.
- Wu, Z., et al. (2024). Reasoning or Reciting? Exploring the Capabilities and Limitations of Language Models Through Counterfactual Tasks. *NAACL 2024*. [ACL Anthology](https://aclanthology.org/2024.naacl-long.102)
