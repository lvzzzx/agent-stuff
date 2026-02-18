# Delta-rs Rust Usage

## Table of Contents
- Add crate
- Open table
- Read Arrow batches
- Write patterns
- Operational guidance

## Add crate

```toml
[dependencies]
deltalake = "latest"
tokio = { version = "1", features = ["macros", "rt-multi-thread"] }
```

Check docs.rs for exact feature flags needed by your object store and runtime.

## Open table

```rust
use deltalake::open_table;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let table = open_table("./data/orders_delta").await?;
    println!("version={}", table.version());
    Ok(())
}
```

## Read Arrow batches

Use the crate's DataFusion/Arrow integrations for query execution and scans, especially for selective reads and analytics.

## Write patterns

In Rust services:
- Stage Arrow RecordBatches.
- Write in bounded batch sizes.
- Keep schema stable and explicit.
- Record resulting table version for downstream consumers.

## Operational guidance

- Prefer idempotent ingest design (checkpointed source offsets).
- Keep object store credentials out of source and inject via env/secret manager.
- Include retry strategy for transient object-store/network failures.
- Run periodic compaction and retention tasks as separate jobs.
