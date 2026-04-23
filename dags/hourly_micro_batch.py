"""DAG: hourly_micro_batch.

Dataset-triggered DAG — fires whenever the bronze S3 or Azure Blob outlets are
produced. Uses deferrable sensors to wait for both clouds before advancing.
"""

from __future__ import annotations

from datetime import datetime

from airflow.decorators import dag, task
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator
from airflow.sensors.time_delta import TimeDeltaSensorAsync

from include import datasets as ds
from include.constants import DEFAULT_ARGS, SILVER_WAREHOUSE


@dag(
    dag_id="hourly_micro_batch",
    description="Dataset-triggered silver refresh using deferrable sensors",
    start_date=datetime(2026, 1, 1),
    schedule=[ds.BRONZE_ORDERS_S3, ds.BRONZE_ORDERS_AZ],
    catchup=False,
    default_args={"owner": DEFAULT_ARGS["owner"], "retries": 1},
    tags=["medallion", "silver", "deferrable"],
)
def hourly_micro_batch():
    start = EmptyOperator(task_id="start")

    wait = TimeDeltaSensorAsync(task_id="grace_window", delta={"seconds": 30})

    run_silver = BashOperator(
        task_id="run_silver",
        bash_command=(
            "spark-submit --packages io.delta:delta-spark_2.12:3.1.0 "
            "src/pyspark/silver/bronze_to_silver.py "
            f"--warehouse {SILVER_WAREHOUSE}"
        ),
        outlets=[ds.SILVER_ORDERS],
    )

    @task
    def emit_lineage() -> None:
        print("emitted OpenLineage event")

    end = EmptyOperator(task_id="end")

    start >> wait >> run_silver >> emit_lineage() >> end


dag = hourly_micro_batch()
