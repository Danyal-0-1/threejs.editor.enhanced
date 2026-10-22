"""runtime/ — what keeps a run running.

    config.py     locations (from environment variables), Sol defaults, RunConfig, hashing
                                                                          from phase3_2/sol/src/p33
    shards.py     crash-safe storage: atomic shards, resume, deterministic merge
                                                                          from phase3_2/sol/src/p33
    preflight.py  refuse a GPU job that would waste its allocation       from phase3_2/sol/src/p33
    prefetch.py   download-only model staging, with pinned revisions      from phase3_2/sol/src/p33
"""
