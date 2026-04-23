"""dlt (data load tool) pipeline for partner REST APIs.

Demonstrates:
  - Incremental extraction via `merge_key` / `primary_key`
  - Schema contract enforcement
  - Parquet+Delta destination (S3 / Azure)
"""

from __future__ import annotations

from collections.abc import Iterable


def partner_records(partner: str, cursor: str | None = None) -> Iterable[dict]:
    # In production, this iterates pages from the partner API. For demo, we
    # yield a few synthetic rows so the pipeline is unit-testable.
    base = 0 if cursor is None else int(cursor)
    for i in range(10):
        yield {
            "partner": partner,
            "order_id": f"{partner}-{base + i:08d}",
            "total": 19.99 + i,
            "placed_at": "2026-04-23T10:00:00Z",
        }


def compile_pipeline_spec() -> dict:
    return {
        "pipeline_name": "partner_api",
        "destination": "filesystem",
        "dataset_name": "partner_bronze",
        "write_disposition": "append",
        "primary_key": "order_id",
        "file_format": "parquet",
    }
