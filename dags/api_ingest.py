"""DAG: api_ingest.

Dynamic task mapping over partner APIs. Uses dlt under the hood (see src/dlt/).
"""

from __future__ import annotations

from datetime import datetime, timedelta

from airflow.decorators import dag, task
from airflow.operators.empty import EmptyOperator

from include import datasets as ds
from include.callbacks import slack_on_failure
from include.constants import DEFAULT_ARGS


@dag(
    dag_id="api_ingest_dynamic",
    description="dlt-based partner API ingestion with DynamicTaskMapping",
    start_date=datetime(2026, 1, 1),
    schedule="@hourly",
    catchup=False,
    default_args={
        "owner": DEFAULT_ARGS["owner"],
        "retries": 3,
        "retry_delay": timedelta(minutes=2),
        "on_failure_callback": slack_on_failure,
    },
    tags=["ingestion", "dlt", "api"],
)
def api_ingest_dynamic():
    start = EmptyOperator(task_id="start")

    @task
    def enumerate_partners() -> list[dict]:
        return [
            {"name": "acme", "url": "https://api.acme.io/orders", "rate_limit_qps": 5},
            {"name": "globex", "url": "https://api.globex.com/v2", "rate_limit_qps": 10},
            {"name": "initech", "url": "https://api.initech.biz", "rate_limit_qps": 3},
            {"name": "umbrella", "url": "https://api.umbrella.io", "rate_limit_qps": 20},
        ]

    @task(max_active_tis_per_dag=4, pool="api_ingest_pool")
    def ingest_partner(partner: dict) -> dict:
        return {
            "partner": partner["name"],
            "records": 1234,
            "rate_limit_qps": partner["rate_limit_qps"],
        }

    @task
    def summarise(runs: list[dict]) -> dict:
        total = sum(r["records"] for r in runs)
        return {"total_records": total, "partners": len(runs)}

    partners = enumerate_partners()
    ingested = ingest_partner.expand(partner=partners)
    summary = summarise(ingested)

    write_bronze = EmptyOperator(task_id="write_bronze", outlets=[ds.BRONZE_ORDERS_S3])
    end = EmptyOperator(task_id="end")

    start >> partners >> ingested >> summary >> write_bronze >> end


dag = api_ingest_dynamic()
