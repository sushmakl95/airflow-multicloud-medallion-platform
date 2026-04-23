"""Helper for composing OpenLineage transport configuration."""

from __future__ import annotations

from typing import TypedDict


class OLTransportConfig(TypedDict):
    type: str
    url: str


def http_transport(url: str) -> OLTransportConfig:
    return {"type": "http", "url": url}


def marquez_backend(marquez_url: str, namespace: str = "airflow-multicloud") -> dict:
    return {
        "transport": http_transport(marquez_url),
        "namespace": namespace,
        "producer": "airflow-multicloud-medallion",
    }
