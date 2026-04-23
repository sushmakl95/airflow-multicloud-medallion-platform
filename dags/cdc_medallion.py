"""DAG: cdc_medallion.

End-to-end CDC → medallion pipeline. Showcases:
  - TaskFlow API with typed @task functions
  - Task groups per layer (bronze / silver / gold)
  - Dynamic task mapping across CDC tables
  - Outlets producing Dataset updates for downstream DAGs
  - SLA definitions + custom callbacks
  - on_failure / sla_miss callbacks
"""

from __future__ import annotations

from datetime import datetime, timedelta

from airflow.decorators import dag, task, task_group
from airflow.models.baseoperator import chain
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator

from include import datasets as ds
from include.callbacks import (
    datadog_on_sla_miss,
    emit_openlineage_on_success,
    slack_on_failure,
)
from include.constants import (
    BRONZE_BUCKET,
    CDC_TABLES,
    DEFAULT_ARGS,
    GOLD_WAREHOUSE,
    SILVER_WAREHOUSE,
)

default_args = {
    "owner": DEFAULT_ARGS["owner"],
    "retries": DEFAULT_ARGS["retries"],
    "retry_delay": timedelta(minutes=DEFAULT_ARGS["retry_delay_minutes"]),
    "depends_on_past": False,
    "sla": timedelta(hours=2),
    "on_failure_callback": slack_on_failure,
    "on_success_callback": emit_openlineage_on_success,
}


@dag(
    dag_id="cdc_medallion",
    description="Debezium CDC → Kafka → PySpark medallion → Delta Lake (multi-cloud bronze)",
    start_date=datetime(2026, 1, 1),
    schedule="@hourly",
    catchup=False,
    default_args=default_args,
    max_active_runs=1,
    sla_miss_callback=datadog_on_sla_miss,
    tags=["medallion", "cdc", "delta", "kafka", "multicloud"],
    params={"run_table": None, "dry_run": False},
)
def cdc_medallion():
    start = EmptyOperator(task_id="start")

    @task
    def resolve_tables(params: dict) -> list[str]:
        if params and params.get("run_table"):
            return [params["run_table"]]
        return CDC_TABLES

    tables = resolve_tables()

    @task_group(group_id="bronze")
    def bronze_group(table: str):
        BashOperator(
            task_id="kafka_to_s3",
            bash_command=(
                "spark-submit --packages io.delta:delta-spark_2.12:3.1.0 "
                "src/pyspark/bronze/kafka_to_delta.py "
                f"--table {table} --sink s3a://{BRONZE_BUCKET}/{table}/"
            ),
            outlets=[ds.BRONZE_ORDERS_S3],
        )
        BashOperator(
            task_id="kafka_to_abs",
            bash_command=(
                "spark-submit src/pyspark/bronze/kafka_to_delta.py "
                f"--table {table} --sink abfss://lakehouse@azurite/{table}/"
            ),
            outlets=[ds.BRONZE_ORDERS_AZ],
        )

    bronze_mapped = bronze_group.expand(table=tables)

    @task_group(group_id="silver")
    def silver_group():
        return BashOperator(
            task_id="bronze_to_silver",
            bash_command=(
                "spark-submit --packages io.delta:delta-spark_2.12:3.1.0 "
                "src/pyspark/silver/bronze_to_silver.py "
                f"--warehouse {SILVER_WAREHOUSE}"
            ),
            outlets=[ds.SILVER_ORDERS],
        )

    @task_group(group_id="gold")
    def gold_group():
        return BashOperator(
            task_id="silver_to_gold",
            bash_command=(
                "spark-submit src/pyspark/gold/silver_to_gold.py " f"--warehouse {GOLD_WAREHOUSE}"
            ),
            outlets=[ds.GOLD_ORDERS_DAILY],
        )

    @task_group(group_id="dq")
    def dq_group():
        BashOperator(
            task_id="great_expectations",
            bash_command="great_expectations checkpoint run silver_orders_checkpoint",
        )
        BashOperator(
            task_id="soda_core",
            bash_command="soda scan -d gold_warehouse -c src/ge/soda/config.yml src/ge/soda/checks.yml",
        )

    @task
    def emit_lineage_summary() -> dict:
        return {"bronze_tables": CDC_TABLES, "status": "ok"}

    end = EmptyOperator(task_id="end")

    chain(
        start,
        tables,
        bronze_mapped,
        silver_group(),
        dq_group(),
        gold_group(),
        emit_lineage_summary(),
        end,
    )


dag = cdc_medallion()
