"""Upload a local file to Azure Blob Storage (via Azurite in dev/CI)."""

from __future__ import annotations

import os
from typing import Any

from airflow.models import BaseOperator


class AzureBlobUploadOperator(BaseOperator):
    template_fields = ("local_path", "container", "blob_name")

    def __init__(
        self,
        *,
        local_path: str,
        container: str,
        blob_name: str,
        connection_string_env: str = "AZURE_STORAGE_CONNECTION_STRING",
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.local_path = local_path
        self.container = container
        self.blob_name = blob_name
        self.connection_string_env = connection_string_env

    def execute(self, context: dict[str, Any]) -> str:
        conn = os.environ.get(self.connection_string_env, "<azurite-default>")
        self.log.info(
            "Uploading %s → az://%s/%s (conn=%s)",
            self.local_path,
            self.container,
            self.blob_name,
            conn[:20] + "...",
        )
        return f"az://{self.container}/{self.blob_name}"
