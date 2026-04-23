from __future__ import annotations

import pytest

pytest.importorskip("airflow")

from include import datasets as ds  # noqa: E402


def test_registry_covers_expected_cloud_layers():
    # Airflow normalises URIs (strips trailing slashes for known schemes);
    # assert on the stable prefix rather than the verbatim URI.
    uris = {d.uri for d in ds.ALL}
    assert any(u.startswith("s3://lakehouse-bronze/orders") for u in uris)
    assert any(u.startswith("az://lakehouse/bronze/orders") for u in uris)
    assert any(u.startswith("gs://lakehouse-bronze/orders") for u in uris)
    assert any(u.startswith("delta://silver/orders") for u in uris)
    assert any(u.startswith("delta://gold/orders_daily") for u in uris)


def test_all_datasets_have_unique_uris():
    uris = [d.uri for d in ds.ALL]
    assert len(uris) == len(set(uris))
