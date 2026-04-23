from __future__ import annotations

import pytest

pytest.importorskip("airflow")

from plugins.operators.azure_blob_upload import AzureBlobUploadOperator  # noqa: E402


def test_azure_blob_upload_returns_blob_uri(monkeypatch):
    monkeypatch.setenv(
        "AZURE_STORAGE_CONNECTION_STRING", "DefaultEndpointsProtocol=http;AccountName=x"
    )
    op = AzureBlobUploadOperator(
        task_id="up",
        local_path="/tmp/x.parquet",
        container="lakehouse",
        blob_name="bronze/orders/2026-04-23/x.parquet",
    )
    uri = op.execute(context={})
    assert uri == "az://lakehouse/bronze/orders/2026-04-23/x.parquet"
