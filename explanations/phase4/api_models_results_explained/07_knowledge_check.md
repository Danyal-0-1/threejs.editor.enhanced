# 07 — Knowledge check: the served-model run

> Questions only, no answers. Each section names the documents that answer it. If you can answer
> a section without opening them, you understand that part of the run.

---

## A. What kind of evidence this is (`01 §1`, `06`)

1. Why is `dev-20261023a` a development run, and what in the code enforces that a held-out run
   cannot happen yet?
2. Name two sentences you could write in the paper about these nine models, and one you could not.
3. The nine models are now in `DEV_MODELS`. What would a confirmatory test with them need instead
   of new models?

## B. Serving and pinning (`01 §2`, `03 §4`)

4. What exactly is pinned for a served model, and where is it checked?
5. What happens, row by row, if the server is redeployed in the middle of a cell?
6. Three listed models send no `system_fingerprint`. What can the pipeline no longer detect for
   them?
7. Why do the three OLMo 3 models share one `tokenizer_id`, and what does that buy in the
   OLMo 3 32B Instruct–Think comparison?

## C. The measurement through an API (`01 §3`, `03 §10`, `04 §8`)

8. Which three requests does one pair cost, and which fields of the answer does the margin use?
9. Why must `add_special_tokens` be false, and which served models would be affected otherwise?
10. In the traced site, why is `merged` true although both candidates are one token long?
11. The sums start at index `k`. What goes wrong if they start at `k − 1`?

## D. Rounding and batching (`01 §4–5`, Tables A1–A2)

12. Why can a served model produce an exact tie, when Phase 3.3 never did?
13. Why does the pipeline count a tie as *not* reverted, and what would counting it change?
14. The probe found margins repeatable to the bit. Why did the run not?
15. Which is more robust to batching noise: one site's margin or a model's reversion rate? Why?
16. Using Table A2, how often would re-running the whole run flip a site between reverted and not?
17. Gemma 4's re-scored margins changed by up to 10.7 nats on the same pinned deployment. What
    does that do to its reversion rate, to its rule-effect interval, and to any single site?

## E. The results (`00`, `02`)

18. How do the served models' reversion rates with the table compare with Phase 3.3's 21 models'
    40–56%, and with its ten instruct models' 40–53%?
19. Does the table help every served model? How do you read "helps" against "is enough"?
20. Does Qwen3.5 from 27B to 397B show a size trend? Why is total parameters a questionable axis
    here?
21. How many worked examples does a served model need to switch, compared with Phase 3.3's models?
22. The pipeline reports 9.44 examples for OLMo 3 7B Instruct in `dom`; exact arithmetic gives
    7.27. Why, and why is fixing it a decision about Phase 3.3 as well (`02 §3`, `08 §6`)?

## F. Generation (`01 §10`, `00 §7`, Table 5)

23. Why did OLMo 3 (and, 48 times, Qwen3.5 397B) produce empty programs, and why does that not
    affect their Arm A margins?
24. Why would changing Arm B to a chat format for OLMo 3 now be a mistake, and what would be the
    right way to do it?
25. Reach and reversion given reach are never multiplied. Why?

## G. The run itself (`03 §7–9`, `08 §1`)

26. What did the first launch's stuck socket show, and why was the service not to blame?
27. Why did reusing one connection per thread fix it?
28. Why was DeepSeek run two, then three, cells at a time, and why not more?
29. A job manifest of the first launch says `RUNNING`. Are its cells valid? How do you know?

## H. The paper (`06`)

30. Where in the paper do these results belong, and with which label?
31. Which three limitations must be stated next to any served-model number?
32. Design the confirmatory test: which material is held out, which models, which criterion?
