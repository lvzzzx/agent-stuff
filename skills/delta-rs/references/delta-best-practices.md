# Delta Lake Best Practices (delta-rs)

Source: https://delta-io.github.io/delta-rs/delta-lake-best-practices/

## Table of Contents
- Keep data and transaction log healthy
- Use strong table layout and partition design
- Prefer incremental and idempotent writes
- Avoid unsafe overwrite and retention settings
- Operate with observability and reproducibility

## Keep data and transaction log healthy

- Control small-file growth with periodic compaction.
- Keep maintenance separate from ingest workloads.
- Use predictable retention settings and document them per table tier.
- Treat optimize + vacuum as scheduled data platform operations, not ad-hoc commands.

## Use strong table layout and partition design

- Choose partition columns with practical cardinality; avoid highly unique partitions.
- Favor commonly-filtered dimensions for data skipping and z-order candidate columns.
- Revisit layout decisions if query patterns shift significantly.

## Prefer incremental and idempotent writes

- Prefer append for immutable events.
- Use MERGE for mutable datasets keyed by stable business identifiers.
- Deduplicate each incoming batch by merge key before merge execution.
- Record source offsets/watermarks and resulting table version for replay-safe pipelines.

## Avoid unsafe overwrite and retention settings

- Use predicate overwrite for bounded replacements (for example one date partition).
- Require dry-run checks before vacuum in production jobs.
- Keep retention long enough for rollback, delayed readers, and audit windows.
- Do not force short retention without explicit operational sign-off.

## Operate with observability and reproducibility

- Log every write mode, predicate, and merge condition in job telemetry.
- Capture Delta table version after writes/merges for downstream traceability.
- Add simple quality checks after critical operations (row count deltas, key uniqueness).
- For debugging/regressions, pin reads by table version to make results reproducible.

## Practical checklist before production rollout

1. Partition strategy reviewed for cardinality and access patterns.
2. Merge keys and dedupe logic validated.
3. Compaction and vacuum cadence documented.
4. Retention policy aligned with data recovery requirements.
5. Monitoring includes table version, operation metrics, and validation checks.
