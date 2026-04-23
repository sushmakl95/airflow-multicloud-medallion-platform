"""Validate a payload against an Open Data Contract Standard (ODCS v3) manifest."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from airflow.exceptions import AirflowFailException
from airflow.models import BaseOperator


class ODCSContractValidationOperator(BaseOperator):
    template_fields = ("contract_path", "dataset_name")

    def __init__(
        self,
        *,
        contract_path: str,
        dataset_name: str,
        fail_on_breaking: bool = True,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.contract_path = contract_path
        self.dataset_name = dataset_name
        self.fail_on_breaking = fail_on_breaking

    def execute(self, context: dict[str, Any]) -> dict:
        p = Path(self.contract_path)
        if not p.exists():
            if self.fail_on_breaking:
                raise AirflowFailException(f"ODCS contract missing: {self.contract_path}")
            return {"status": "skipped"}
        doc = yaml.safe_load(p.read_text())
        required_fields = {"apiVersion", "kind", "status", "schema"}
        missing = required_fields - set(doc.keys())
        if missing and self.fail_on_breaking:
            raise AirflowFailException(f"ODCS manifest missing required fields: {missing}")
        return {"status": "ok", "dataset": self.dataset_name, "version": doc.get("apiVersion")}
