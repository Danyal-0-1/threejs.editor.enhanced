"""scoring/ — one model's margin at one site.

    margins.py    THE scorer: M = log P(correct) - log P(competitor), from the first divergent
                  token, with an fp32 output head                         from phase3_2/src/phase3_2
    scorers.py    load one model, offline, from its pinned snapshot      from phase3_2/sol/src/p33
    fakes.py      a deterministic, GPU-free scorer for the tests         from phase3_2/sol/src/p33
    fertility.py  tokens per character, for every distinct tokenizer      from phase3_2/sol/src/p33
    scoring.py    Phase 3's forced-prefix scorer. The pipeline uses only its
                  interaction_did (for H2)                                from phase3/src/phase3
    models.py     Phase 3's language-model interface (scoring.py needs it) from phase3/src/phase3
"""
