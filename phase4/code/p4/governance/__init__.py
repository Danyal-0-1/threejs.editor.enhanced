"""governance/ — what keeps a run honest.

    registry.py    every model the programme may touch, with its pair and GPU class
                                                                          from phase3_2/sol/src/p33
    splits.py      the registered split, the size ceiling, the freeze lock, unlock, drift check
                                                                          from phase3_2/sol/src/p33
    freeze.py      builds DEV_FREEZE.json from a complete development run  from phase3_2/sol/src/p33
    provenance.py  job manifests: git, Slurm, GPU and package identity on every shard
                                                                          from phase3_2/sol/src/p33
"""
