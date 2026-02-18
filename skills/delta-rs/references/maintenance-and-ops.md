# Delta-rs Maintenance and Operations

## Table of Contents
- Table health model
- Small-file management
- Z-order optimization
- Vacuum and retention
- Metadata and history
- Troubleshooting checklist

## Table health model

Delta performance degrades with too many small files and excessive log growth. A healthy table has:
- Reasonable file sizes
- Predictable partition layout
- Retention policy that matches recovery needs

## Small-file management

```python
from deltalake import DeltaTable

dt = DeltaTable("data/events_delta")
result = dt.optimize.compact()
print(result)
```

Run compaction on hot partitions or recent data ranges as part of routine maintenance.

## Z-order optimization

```python
dt.optimize.z_order(["customer_id", "event_date"])
```

Use on frequently-filtered columns to improve data skipping. Choose a small set of high-value columns.

## Vacuum and retention

```python
# Dry run first
stale_files = dt.vacuum(retention_hours=168, dry_run=True)
print(len(stale_files))

# Real delete after validation
dt.vacuum(retention_hours=168, dry_run=False)
```

Guidance:
- Align retention with SLA and rollback requirements.
- Never vacuum aggressively on tables requiring long lookback or delayed readers.
- Prefer explicit retention values over defaults in production jobs.

## Metadata and history

Use table metadata and version history for audits and incident debugging.

- Record table version after write/merge.
- Track operation metrics and row-count checks.
- Keep job metadata (run id, source window, write mode).

## Troubleshooting checklist

1. Unexpected duplicates: verify MERGE key uniqueness in source.
2. Missing data after overwrite: inspect overwrite predicate.
3. Read performance regressions: inspect file counts and run compaction.
4. Time travel failures: check retention and vacuum policy.
5. Schema errors: verify `schema_mode`, column types, and nullability.
