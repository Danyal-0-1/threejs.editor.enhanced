# Using the ASU RC LLM API ("Voyager") in Phase 4

ASU Research Computing serves many language models through one API, at no cost.

- **The Voyager portal** is where you create a key and see the models:
  [voyager.rc.asu.edu](https://voyager.rc.asu.edu).
- **The API** is OpenAI-compatible, at `https://openai.rc.asu.edu/v1`.

The models run on Research Computing hardware, so they need **no Sol GPU job**.

This page covers:

1. how the service works;
2. what it can and cannot measure for this experiment;
3. the steps to get the model list and the capability tables ready before any model is used
   in the experiment.

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

## 2. What it can and cannot measure here

| part of the experiment | what it needs | through this API |
|---|---|---|
| **Arm B**: free generation from natural-language requests, then reach and reversion given reach | chat completions | **every chat model** |
| **Arm A**: the margin M = log P(correct) − log P(familiar) at a decision site, from a forced prefix | the log-probability of given text: the prompt's own tokens | **only models whose `/v1/completions` returns prompt log-probabilities** (`echo` with `logprobs`, or vLLM's `prompt_logprobs`). The docs do not say which ones; the probe below finds out |
| first-token diagnostics | `top_logprobs` on generated tokens | models whose server returns them (probe) |
| **H4**: the base model predicts its instruct twin | a base checkpoint *and* its instruct twin | only where both are served. Most served models are instruction-tuned |
| **H5**: repair arms | Arm A margins | as Arm A |

**Three differences from Phase 3.3's own scoring on Sol:**

- **No pinned revision.** A served model can change without notice. So record the `/v1/models`
  snapshot and the dates of the requests, and report this as a limitation.
- **No fp32 head.** Phase 3.3 computed the output layer in fp32 because the outcome is a margin's
  sign. Behind an API, the server's precision is what you get.
- **The server's tokenizer.** Margins are summed over the server's tokens. That is fine, as long
  as both candidates are scored the same way.

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
# from the repository root (the tool needs only Python 3, no extra packages)
run/.venv/bin/python phase4/code/tools/voyager_models.py list
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

For each model the probe sends four tiny requests:

- chat;
- chat with `top_logprobs`;
- a plain completion;
- a completion asking for the prompt's own log-probabilities.

It uses a **neutral prompt** ("The capital of France is"), never the experiment's materials, so
the models stay unseen. It writes:

- `probe_<date>.md`: whether each model can serve Arm B and Arm A;
- `probe_<date>.json`: the raw checks.

### Step 5 — Decide, then register

1. Read the two tables and choose the models for Phase 4, and their role.
2. Write the choice into [`../PREREGISTRATION.md`](../PREREGISTRATION.md):
   - §2, the split: a served model was never scored in Phase 3.3, so it can be a held-out model;
   - §9, the API models.
3. Then come the code steps, made once the study is chosen:
   - registry entries for API models (no weights, no base/instruct pair unless both are served);
   - an API scorer for Arm B, and for Arm A where prompt log-probabilities exist;
   - the model snapshot recorded in every run's manifest.

Until the preregistration registers them, the pipeline's split classifies these models as
held-out, so they cannot be scored by accident.

---

## Laptop or Sol?

**Both work, because the API is reachable from anywhere.**

- **The list and the probe** take minutes: run them wherever is convenient.
- **Long experiment runs** belong in a Sol CPU job, so the laptop can sleep and the results sit
  next to the other Sol results. That needs the key in `~/.config/asu-rc/` on Sol too (step 2,
  done on Sol).

---

Sources: [LLM API Access](https://docs.rc.asu.edu/ai/api) ·
[Getting started with AI](https://docs.rc.asu.edu/ai/getting-started) ·
[Chat completions](https://docs.rc.asu.edu/ai/api/chat) ·
[Verdicts](https://docs.rc.asu.edu/ai/api/verdicts) ·
[Limits and errors](https://docs.rc.asu.edu/ai/api/limits-and-errors) (read on 2026-10-22).
