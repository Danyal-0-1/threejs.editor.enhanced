# Using the ASU RC LLM API ("Voyager") in Phase 4

ASU Research Computing serves many language models through one API, at no cost.

- **The Voyager portal** is where you create a key and see the models:
  [voyager.rc.asu.edu](https://voyager.rc.asu.edu).
- **The API** is OpenAI-compatible, at `https://openai.rc.asu.edu/v1`.

The models run on Research Computing hardware, so they need **no Sol GPU job**.

This page covers:

1. how the service works;
2. what it measured on 2026-10-22: **36 models serve both arms of the experiment**;
3. the steps to get the model list and the capability tables, before any model is used in the
   experiment;
4. how a served model runs in the pipeline.

---

## 1. How it works

All of this is from Research Computing's documentation (the sources are at the end).

**Your key:**

- one per person, created in the Voyager portal under **Keys → AI LLM → Create API key**;
- shown **once**, so copy it at once;
- the portal's **Rotate** button replaces it in seconds;
- older keys go through a gateway that is being retired, so rotate them.

**Where it works:**

- the API works **from anywhere**, on or off campus, without the VPN;
- only the portal itself needs the ASU network or the SSLVPN.

**The model list:** `GET /v1/models`. For each model it gives its id, type, context window, and
whether it supports tools, vision, structured output and reasoning, plus its deprecation status.
The portal shows the same list under **AI LLM → LLMs**.

**Endpoints used here:**

| endpoint | what it does |
|---|---|
| `POST /v1/chat/completions` | chat. `temperature`, `top_p`, `max_tokens`, `stop`, `n`, `logprobs` and `top_logprobs` are passed to the model server as sent |
| `POST /v1/completions` | a plain prompt, with no chat template |

**Other endpoints:** `/responses`, `/messages` (Anthropic-style), `/embeddings` and `/verdicts`.
`/verdicts` returns typed answers with probabilities taken from the first token of fixed labels,
so it cannot compare two given continuations.

**Limits:**

- a per-minute token budget: `429`, then wait one minute;
- a fair queue: after 5 minutes waiting, `503`;
- a request may run for 60 minutes at most;
- 4–8 parallel requests per model is the advised starting point;
- retry `502`, `503` and `504` with backoff.

**Data:**

- prompts are **not** passed to any commercial provider;
- the gateway keeps a usage record (key, model, token counts, status, timing) for 180 days, but
  not the text.

---

## 2. What it measured on 2026-10-22

The probe (step 4) asked every text model what the experiment needs, with neutral prompts only.
The tables are [`configs/voyager/models_2026-10-22.md`](configs/voyager/models_2026-10-22.md)
(the 52 models) and [`configs/voyager/probe_2026-10-22.md`](configs/voyager/probe_2026-10-22.md)
(what each can measure).

**The result: 36 models serve both arms, measured exactly as Phase 3.3 measured.**

- 52 models are listed. 39 are text models, and 42 were probed, because five of the 39 are
  families whose instruct and thinking members were probed separately.
- 37 returned what Arm A needs, and 38 what Arm B needs.
- 36 are now in the registry. Left out:
  - glm-5-3-spec: the same deployment as glm-5-3 answered;
  - laguna-s-2-1: Arm B only, because its prompt log-probabilities were incomplete;
  - glm-5-2, kimi-k2-7-code and qwen3-vl-32b-instruct / -thinking: they did not answer that day.

| part of the experiment | what it needs | through the API |
|---|---|---|
| **Arm A**: the margin M = log P(correct) − log P(familiar) at a decision site | every prompt token's id and log-probability, with no special tokens added | **36 models**, through `/v1/completions` with `prompt_logprobs: 0`, `return_token_ids` and `add_special_tokens: false`: Phase 3.3's raw-text protocol |
| **Arm B**: greedy generation from a raw prompt | the generated text | **the same 36**. Each gave the same text twice |
| fertility | the served tokenizer | the same 36 (the API counts the tokens) |
| **H4**: a base model predicts its instruct twin | a base model *and* its instruct twin | **none**: every served model is post-trained |
| **H5**: repair the roles the base twin finds risky | the base twin's Arm A risk | **none**, for the same reason. The pipeline leaves served models out of H5 |

**Four differences from Phase 3.3's scoring on Sol, all recorded on every row:**

1. **Rounded logits.** For 33 of the 36, every test margin was a whole multiple of 1/8, 1/16 or
   1/32 nats: the server rounds its logits to bf16. Phase 3.3 computed its output layer in fp32
   to avoid exactly this (defect P33-002). So a margin nearer zero than that step has an
   unreliable sign, and exact ties occur. In Phase 3.3's held-out run, 2.5% of margins were
   within 0.0625 nats of zero and 5.1% within 0.125. Three models do not round: beam-1-0,
   deepseek-v4-1-flash and muse-spark-open. Rows: `fp32_head = False`, and `tie`.
2. **Quantized weights.** Many are served in fp8 or mxfp4 (`dtype` on every row). The model
   measured is the quantized one.
3. **No revision.** The pin is the deployment that answered: `<served name>@<system_fingerprint>`.
   - Every answer is checked against it. A cell that gets an answer from another deployment
     fails, instead of mixing the two.
   - Three models send no fingerprint (granite41-30b, minimax-m2-7, qwen-agentworld-35b-a3b), so
     for them only the name is checked.
4. **No base twins** (above).

**Also measured:**

- each model gave the same margins twice, bit for bit;
- five models add a beginning-of-text token by default (devstral2-123b, gemma4-31b-it, the two
  llama4 models and muse-glimmer-30b). Scoring turns it off, as Phase 3.3 did.

**Throughput.** A pair takes three requests, sent at once: about 0.9 s per pair at 200 tokens
(qwen3-coder-30b-a3b-instruct). At Phase 3.3's sizes (about 9,100 Arm A pairs, 4,000 ladder pairs
and 370 generations per model), that is roughly 4 hours per model. Models run in parallel, as
array tasks.

---

## 3. Step by step

### Step 1 — Create your key (once)

1. Connect to the ASU SSLVPN, unless you are on campus.
2. Open [voyager.rc.asu.edu](https://voyager.rc.asu.edu) and sign in with your ASURITE.
3. Go to your profile, then **Keys → AI LLM → Create API key**. Copy the key now; it is shown once.

### Step 2 — Store it on each machine that will call the API (laptop and/or Sol)

```bash
mkdir -p ~/.config/asu-rc && chmod 700 ~/.config/asu-rc
( umask 077; cat > ~/.config/asu-rc/llm_api_key )      # paste the key, press Enter, then Ctrl-D
chmod 600 ~/.config/asu-rc/llm_api_key
```

**Where the key never goes:**

- the repository;
- a results folder;
- a job script;
- the command line.

Typing it on the command line puts it in your shell history and the process list. The tool
refuses a key file that others can read.

### Step 3 — Get the list of models

```bash
# on the laptop, from the repository root (the tool needs only Python 3, no extra packages)
run/.venv/bin/python phase4/code/tools/voyager_models.py list

# on Sol, from ~/phase4_experiment_sol/repo, with the environment's Python (the one every job uses)
../env/bin/python phase4/code/tools/voyager_models.py list
```

This writes two files to `phase4/code/configs/voyager/`:

- `models_<date>.md`: one row per model, with its type, context window and capabilities;
- `models_<date>.json`: the raw list.

Neither contains the key.

### Step 4 — Find out what each model can measure

```bash
run/.venv/bin/python phase4/code/tools/voyager_models.py probe              # every text model
run/.venv/bin/python phase4/code/tools/voyager_models.py probe --models ID,ID
```

For each model the probe sends about 14 small requests:

- **Arm A's protocol:** the prompt's token ids and log-probabilities with special tokens off; then
  three one-word contrasts scored from the first divergent token, one of them twice (are the
  margins repeatable, and are they rounded?);
- **Arm B's protocol:** greedy text from `def add(a, b):`, twice;
- chat, and chat with `top_logprobs`.

A model that does not answer within a minute (twice) is recorded as such, and the probe moves on.
The prompts are **neutral** (a sentence about a river, and `def add`), never the experiment's
materials, so the models stay unseen. It writes:

- `probe_<date>.md`: what each model can serve, its margin step and the deployment that answered;
- `probe_<date>.json`: the raw checks.

### Step 5 — Decide, then register

1. Read the two tables and choose the models for Phase 4, and their role.
2. Write the choice into [`../PREREGISTRATION.md`](../PREREGISTRATION.md):
   - §2, the split: a served model was never scored in Phase 3.3, so it can be a held-out model;
   - §9, the served models, and the questions listed there.
3. Write the roles into `p4/governance/splits.py` in the same commit: development models into
   `DEV_MODELS`; and, for a model above 72B, a new `MAX_SIZE_B`.

Until then, the pipeline's split classifies these models as held-out (or forbidden, above 72B),
so they cannot be scored by accident.

---

## 4. Running a served model in the pipeline

The code is in place ([`README.md`](README.md), section "Models served by the ASU RC API"). A served
model is named `asu-rc/<served name>` in a run config, like any other model:

```bash
cd ~/phase4_experiment_sol/repo/phase4/code/sol && source sol.env && source env/activate.sh
$P4_PY ../run.py prefetch --config ../configs/<a Phase 4 config>.json   # pins every model, served ones too
$P4_PY ../run.py dev init --config ../configs/<a Phase 4 config>.json --run dev-<date>
bash submit.sh dev_arm_a_api dev-<date>       # one CPU array task per served model
bash submit.sh arm_b_api dev-<date>
```

- **The pin** is the deployment that answered at `prefetch`. Pin at the start of a run, not
  weeks before: if the deployment changes, preflight and the scorer refuse, and a new run with a
  new pin is needed. That is deliberate: a run never mixes two deployments.
- **On Sol** the key must be in `~/.config/asu-rc/llm_api_key` there too (step 2, done on Sol).
  Sol's compute nodes have reached the internet before: Phase 3.3's prefetch jobs downloaded from
  Hugging Face.
- **The `_api` jobs** request 2 CPUs and 8 GB for 24 hours, and no GPU.

---

## Laptop or Sol?

**Both work, because the API is reachable from anywhere.**

- **The list and the probe** take minutes. The laptop is simplest: the tables land in the
  checkout you commit from. They hold no key, so they can be committed as the record of what was
  served that day, and Sol gets them with `git pull`.
- **Long experiment runs** belong in a Sol CPU job, so the laptop can sleep and the results sit
  next to the other Sol results. That needs the key in `~/.config/asu-rc/` on Sol too (step 2,
  done on Sol).

---

Sources: [LLM API Access](https://docs.rc.asu.edu/ai/api) ·
[Getting started with AI](https://docs.rc.asu.edu/ai/getting-started) ·
[Chat completions](https://docs.rc.asu.edu/ai/api/chat) ·
[Verdicts](https://docs.rc.asu.edu/ai/api/verdicts) ·
[Limits and errors](https://docs.rc.asu.edu/ai/api/limits-and-errors) (read on 2026-10-22).
