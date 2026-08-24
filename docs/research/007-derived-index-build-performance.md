# Derived Index Build Performance

**Issue:** #17, *Profile and reduce Derived Index build time*  
**Measured:** 2026-08-24  
**Corpus fingerprint:** `9f98ab26832e8f80c9a9a9133807a416e1d9b0ff94458523ea2226854b424e83`

## Environment

- macOS 26.5.2 on `arm64`
- Python 3.12.12
- uv 0.10.9
- local embedding model `BAAI/bge-small-en-v1.5`
- 259 Knowledge Sources and 1,957 Evidence Passages
- model files already present locally; synchronization performed no model download

Peak memory is not reported: the available `/usr/bin/time -l` run completed the
index successfully but its macOS accounting step could not read the required
`sysctl` value in the execution environment. The report retains the reliable
wall-clock and stage measurements rather than recording an unverified estimate.

## Reproduction

From the repository root, use the documented commands:

```bash
uv run endurance-kb build-index
uv run endurance-kb status
```

For a cold-index measurement, use a missing index or an incompatible schema so
no source can be reused. Run `build-index` again without changing the corpus for
the warm incremental measurement. The command prints source/passage work counts
and timings for manifest hashing, chunking, model setup, embedding, vector
insertion, SQLite/FTS work, validation, and atomic replacement.

## Results

| Build | Sources reused/rebuilt | Passages reused/embedded | Wall time |
| --- | ---: | ---: | ---: |
| Original full rebuild | 0 / 259 | 0 / 1,957 | 612.84 s |
| Incremental implementation, fresh schema | 0 / 259 | 0 / 1,957 | 600.54 s |
| Incremental implementation, unchanged corpus | 259 / 0 | 1,957 / 0 | 0.75 s |

The fresh implementation run spent 599.52 seconds in the embedding pipeline,
0.53 seconds chunking, 0.18 seconds on SQLite work, and 0.17 seconds validating.
Embedding therefore accounted for 99.8% of the fresh build and was the measured
bottleneck. Reusing unchanged passages and their vectors reduced the recurring
build from 600.54 seconds to 0.75 seconds, roughly an 801x speedup on this corpus
and environment. The final warm run spent 0.03 seconds inserting reused vectors,
0.35 seconds on SQLite/FTS work, and 0.12 seconds validating the completed index.

The optimization retains content-digest freshness, full temporary-database
validation, and atomic replacement. Filesystem modification time is not used as
an authoritative change signal.
