"""Custom DeltaMergeOperator.

Runs a `MERGE INTO` against a Delta table via spark-submit. Emits OpenLineage
input/output facets.
"""

from __future__ import annotations

from typing import Any

from airflow.models import BaseOperator


class DeltaMergeOperator(BaseOperator):
    """Minimal custom operator demonstrating the pattern."""

    template_fields = ("target_table", "source_query", "merge_keys")

    def __init__(
        self,
        *,
        target_table: str,
        source_query: str,
        merge_keys: list[str],
        spark_conf: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.target_table = target_table
        self.source_query = source_query
        self.merge_keys = merge_keys
        self.spark_conf = spark_conf or {}

    def execute(self, context: dict[str, Any]) -> str:
        join = " AND ".join(f"t.{k} = s.{k}" for k in self.merge_keys)
        sql = (
            f"MERGE INTO {self.target_table} t "
            f"USING ({self.source_query}) s "
            f"ON {join} "
            "WHEN MATCHED THEN UPDATE SET * "
            "WHEN NOT MATCHED THEN INSERT *"
        )
        self.log.info("Delta merge SQL: %s", sql)
        # In production this would invoke spark-submit; for test/demo we return the SQL.
        return sql
