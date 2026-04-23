"""Central registry of Dataset URIs referenced across DAGs for data-aware scheduling."""

from __future__ import annotations

from airflow.datasets import Dataset

BRONZE_ORDERS_S3 = Dataset("s3://lakehouse-bronze/orders/")
BRONZE_ORDERS_AZ = Dataset("az://lakehouse/bronze/orders/")
BRONZE_ORDERS_GCS = Dataset("gs://lakehouse-bronze/orders/")

SILVER_ORDERS = Dataset("delta://silver/orders")
GOLD_ORDERS_DAILY = Dataset("delta://gold/orders_daily")

CDC_TOPIC_ORDERS = Dataset("kafka://cdc.public.orders")
CDC_TOPIC_CUSTOMERS = Dataset("kafka://cdc.public.customers")


ALL = [
    BRONZE_ORDERS_S3,
    BRONZE_ORDERS_AZ,
    BRONZE_ORDERS_GCS,
    SILVER_ORDERS,
    GOLD_ORDERS_DAILY,
    CDC_TOPIC_ORDERS,
    CDC_TOPIC_CUSTOMERS,
]
