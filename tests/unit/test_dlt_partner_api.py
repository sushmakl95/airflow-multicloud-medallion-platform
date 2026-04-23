from __future__ import annotations

from src.dlt.partner_api import compile_pipeline_spec, partner_records


def test_partner_records_yields_stable_shape():
    rows = list(partner_records("acme"))
    assert len(rows) == 10
    assert {r["partner"] for r in rows} == {"acme"}
    assert all("order_id" in r for r in rows)


def test_pipeline_spec_has_required_keys():
    spec = compile_pipeline_spec()
    assert spec["pipeline_name"] == "partner_api"
    assert spec["primary_key"] == "order_id"
    assert spec["file_format"] == "parquet"
