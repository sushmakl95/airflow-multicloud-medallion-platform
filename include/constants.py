"""Compile-time constants shared across DAGs."""

from __future__ import annotations

DEFAULT_ARGS = {
    "owner": "data-platform",
    "retries": 2,
    "retry_delay_minutes": 5,
    "email_on_failure": False,
    "depends_on_past": False,
}

LOCALSTACK_ENDPOINT = "http://localstack:4566"
AZURITE_ENDPOINT = "http://azurite:10000"
KAFKA_BOOTSTRAP = "redpanda:9092"
HIVE_METASTORE = "thrift://hive-metastore:9083"
MARQUEZ_URL = "http://marquez:5000"
DATAHUB_URL = "http://datahub:8080"

BRONZE_BUCKET = "lakehouse-bronze"
SILVER_WAREHOUSE = "s3://lakehouse-silver/"
GOLD_WAREHOUSE = "s3://lakehouse-gold/"

CDC_TABLES = ["orders", "customers", "order_lines"]
