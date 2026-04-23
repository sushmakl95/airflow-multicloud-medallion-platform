"""Assert all DAGs import cleanly with no exceptions and carry the required metadata."""

from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip("airflow")

from airflow.models import DagBag  # noqa: E402

DAG_FOLDER = Path(__file__).resolve().parents[2] / "dags"


@pytest.fixture(scope="module")
def dagbag() -> DagBag:
    return DagBag(dag_folder=str(DAG_FOLDER), include_examples=False)


def test_no_import_errors(dagbag: DagBag):
    assert not dagbag.import_errors, dagbag.import_errors


def test_expected_dags_present(dagbag: DagBag):
    expected = {
        "cdc_medallion",
        "api_ingest_dynamic",
        "hourly_micro_batch",
        "backfill_pipeline",
    }
    assert expected.issubset(set(dagbag.dag_ids)), f"missing: {expected - set(dagbag.dag_ids)}"


def test_every_dag_has_owner_and_tags(dagbag: DagBag):
    for dag_id, dag in dagbag.dags.items():
        assert dag.tags, f"{dag_id} has no tags"
        assert dag.default_args.get("owner"), f"{dag_id} has no owner"
