from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip("airflow")

from airflow.exceptions import AirflowFailException  # noqa: E402

from plugins.operators.odcs_contract import ODCSContractValidationOperator  # noqa: E402

REPO = Path(__file__).resolve().parents[2]


def test_valid_contract_passes():
    op = ODCSContractValidationOperator(
        task_id="validate",
        contract_path=str(REPO / "configs" / "odcs_orders.yaml"),
        dataset_name="orders",
    )
    out = op.execute(context={})
    assert out["status"] == "ok"
    assert out["dataset"] == "orders"


def test_missing_contract_raises(tmp_path):
    op = ODCSContractValidationOperator(
        task_id="validate",
        contract_path=str(tmp_path / "does-not-exist.yaml"),
        dataset_name="orders",
    )
    with pytest.raises(AirflowFailException):
        op.execute(context={})


def test_missing_contract_skips_when_not_fatal(tmp_path):
    op = ODCSContractValidationOperator(
        task_id="validate",
        contract_path=str(tmp_path / "none.yaml"),
        dataset_name="orders",
        fail_on_breaking=False,
    )
    assert op.execute(context={})["status"] == "skipped"
