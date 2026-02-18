# Delta-rs MERGE and UPSERT Patterns

## Table of Contents
- Why MERGE
- Canonical upsert pattern
- CDC pattern (insert/update/delete)
- SCD Type 1 template
- Operational checks

## Why MERGE

Use MERGE when target rows may already exist and keys are stable. This avoids duplicate keys and supports deterministic updates.

## Canonical upsert pattern

```python
import pyarrow as pa
from deltalake import DeltaTable

path = "data/customers_delta"
dt = DeltaTable(path)

source = pa.table(
    {
        "customer_id": [1, 3],
        "name": ["Alice A.", "Carol"],
        "updated_at": ["2026-02-18", "2026-02-18"],
    }
)

(
    dt.merge(
        source=source,
        predicate="target.customer_id = source.customer_id",
        source_alias="source",
        target_alias="target",
    )
    .when_matched_update(
        updates={
            "name": "source.name",
            "updated_at": "source.updated_at",
        }
    )
    .when_not_matched_insert(
        updates={
            "customer_id": "source.customer_id",
            "name": "source.name",
            "updated_at": "source.updated_at",
        }
    )
    .execute()
)
```

## CDC pattern (insert/update/delete)

Assume source includes `op` in `{I,U,D}`.

- `when_matched_delete` for deletes.
- `when_matched_update` for updates.
- `when_not_matched_insert` for inserts.

Ensure one source row per key per batch before MERGE to avoid ambiguous outcomes.

## SCD Type 1 template

- Keep one current row per business key.
- MERGE updates mutable attributes in-place.
- Insert rows when keys are new.

For SCD Type 2, use explicit `valid_from`, `valid_to`, and `is_current` fields and a two-step approach (expire + insert).

## Operational checks

Before MERGE:
- Deduplicate source keys.
- Validate key nullability and type alignment.
- Confirm expected update/insert cardinality.

After MERGE:
- Validate row counts and key uniqueness.
- Record version and merge metrics for observability.
