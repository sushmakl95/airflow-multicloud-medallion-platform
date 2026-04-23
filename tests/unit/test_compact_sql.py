from __future__ import annotations

from src.pyspark.maintenance.compact import generate_sql


def test_generate_sql_includes_zorder_and_vacuum():
    sql = generate_sql("silver.orders", ["ds", "country"])
    assert any("ZORDER BY (ds, country)" in s for s in sql)
    assert any("VACUUM silver.orders RETAIN" in s for s in sql)
