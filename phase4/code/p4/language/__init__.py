"""language/ — the language as the experiment uses it.

    backends.py   the two grammar families: `dom` (the Phase 1/2 syntax, jQuery-style chaining)
                  and `blk` (a block syntax added in Phase 3.2)               from phase3_2/src/phase3_2
    templates.py  the 80 programs, built as IR and rendered in each family   from phase3_2/src/phase3_2
    deltafam.py   the family of respelled lexicons, by remap density and seed
                  (d25s1 ... d75s3a)                                          from phase3_2/src/phase3_2

The language library underneath (phi-maps, transpiler, canonical IR, the grammar and its test
programs) is in ../../dsl/ (see dsl/README.md).
"""
