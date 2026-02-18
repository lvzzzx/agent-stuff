---
name: delta-rs
description: Delta Lake workflows with the Rust-native delta-rs engine (Python and Rust). Use for reading/writing Delta tables, MERGE/UPSERT, schema evolution, time travel, partitioning, compaction, and vacuum.
license: https://github.com/delta-io/delta-rs/blob/main/LICENSE
metadata:
  skill-author: K-Dense Inc.
---

# Delta-rs

## Overview

Use this skill when a user needs Delta Lake operations through `delta-rs` (Python `deltalake` or Rust crate). This skill is optimized for practical data engineering workflows: ingest, upsert, time travel, table maintenance, and operational safety.

Use this skill for:
- Building or updating Delta tables from Pandas, Arrow, or Polars
- Incremental loads with MERGE/UPSERT patterns
- Schema evolution and partition design
- Time travel debugging and reproducibility
- Maintenance (`optimize`, `z_order`, `vacuum`) and table health checks

## Quick Start

### Python install

```bash
uv pip install "deltalake>=0.18" pyarrow pandas polars
```

### Minimal write + read

```python
import pandas as pd
from deltalake import DeltaTable, write_deltalake

path = "tmp/events_delta"
df = pd.DataFrame({"id": [1, 2], "event": ["open", "click"]})

write_deltalake(path, df, mode="overwrite")
dt = DeltaTable(path)
print(dt.to_pandas())
```

## Core Workflow

1. Decide table keys and partition columns before first write.
2. Use append-only writes for immutable events.
3. Use MERGE for mutable dimensions/facts.
4. Track schema changes explicitly (`schema_mode`).
5. Add maintenance cadence: compact then vacuum.
6. Use time travel for rollback/debugging.

## Common Tasks

### Write modes

- `mode="error"`: fail if table exists
- `mode="append"`: append new files/log entries
- `mode="overwrite"`: replace table or partitions (with predicate)
- `mode="ignore"`: skip if exists

### MERGE / UPSERT

Use `DeltaTable.merge(...)` with `when_matched_update` and `when_not_matched_insert` for CDC-style pipelines.

### Time travel

Read previous versions for reproducibility with `DeltaTable(path, version=...)`.

### Maintenance

- Compact small files: `dt.optimize.compact(...)`
- Improve locality: `dt.optimize.z_order([...])`
- Remove old files safely: `dt.vacuum(retention_hours=..., dry_run=True)` then real run

## Safety Guardrails

- Never run aggressive vacuum until retention policy is confirmed.
- Prefer dry runs before destructive operations.
- Ensure writers agree on schema and partitioning conventions.
- For overwrite operations, use predicates to avoid full-table replacement when unnecessary.

## Reference Files

Load only what is needed:

- `references/read-and-write.md` - Reads, writes, partitioning, schema evolution
- `references/merge-and-upsert.md` - MERGE patterns, SCD/CDC templates
- `references/maintenance-and-ops.md` - Optimize, z-order, vacuum, checkpoints, troubleshooting
- `references/delta-best-practices.md` - Official Delta Lake best-practice guidance adapted for delta-rs users
- `references/rust-usage.md` - Rust crate setup and idiomatic patterns

## Source Priority

When details are uncertain, prefer official docs in this order:
1. `https://delta-io.github.io/delta-rs/`
2. `https://delta-io.github.io/delta-rs/delta-lake-best-practices/`
3. `https://docs.rs/deltalake/`
4. `https://github.com/delta-io/delta-rs`
