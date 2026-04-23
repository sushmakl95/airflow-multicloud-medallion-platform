from __future__ import annotations

import pytest

pytest.importorskip("airflow")

from plugins.operators.delta_merge import DeltaMergeOperator  # noqa: E402


def test_generated_merge_sql_contains_keys_and_source():
    op = DeltaMergeOperator(
        task_id="merge_silver_orders",
        target_table="silver.orders",
        source_query="SELECT * FROM staging.orders",
        merge_keys=["order_id"],
    )
    sql = op.execute(context={})
    assert "MERGE INTO silver.orders" in sql
    assert "SELECT * FROM staging.orders" in sql
    assert "t.order_id = s.order_id" in sql
    assert "WHEN MATCHED THEN UPDATE SET *" in sql
