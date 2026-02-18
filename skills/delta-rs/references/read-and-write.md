# Delta-rs Read and Write Guide

## Table of Contents
- Basic write/read
- Write modes
- Partitioning
- Schema evolution
- Predicate overwrite
- Time travel reads
- Interop notes (Arrow/Pandas/Polars)

## Basic write/read

```python
import pandas as pd
from deltalake import DeltaTable, write_deltalake

path = "data/orders_delta"
df = pd.DataFrame({"order_id": [1, 2], "amount": [100.0, 42.5]})

write_deltalake(path, df, mode="overwrite")
print(DeltaTable(path).to_pandas())
```

## Write modes

```python
write_deltalake(path, df, mode="append")
write_deltalake(path, df, mode="ignore")
write_deltalake(path, df, mode="error")
write_deltalake(path, df, mode="overwrite")
```

Use:
- `append` for immutable events
- `overwrite` for full reloads or controlled replacement

## Partitioning

```python
write_deltalake(
    path,
    df,
    mode="overwrite",
    partition_by=["event_date", "region"],
)
```

Guidance:
- Partition by low-to-medium cardinality columns.
- Avoid too many tiny partitions.
- Avoid partitioning on highly unique keys (for example UUIDs).

## Schema evolution

```python
write_deltalake(path, df_new, mode="append", schema_mode="merge")
```

- Use `schema_mode="merge"` to add compatible columns.
- Use `schema_mode="overwrite"` for controlled full schema replacement.
- Treat type narrowing or incompatible type changes as migrations, not casual appends.

## Predicate overwrite

```python
write_deltalake(
    path,
    df_one_day,
    mode="overwrite",
    predicate="event_date = '2026-02-18'",
)
```

Use predicate overwrite for deterministic partition/day replacement instead of full-table overwrite.

## Time travel reads

```python
from deltalake import DeltaTable

current = DeltaTable(path)
old = DeltaTable(path, version=current.version() - 1)

print(current.version())
print(old.to_pandas().head())
```

Prefer pinning versions in reproducibility-critical jobs.

## Interop notes

- `delta-rs` is Arrow-native; Arrow tables are ideal for performance.
- Pandas works directly via `write_deltalake` and `to_pandas`.
- Polars can read Delta through integrations and then continue with Polars lazy processing.
