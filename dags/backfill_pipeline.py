"""DAG: backfill_pipeline.

Manual-trigger DAG accepting {date_from, date_to}, building a dense date list
and fanning out dynamic tasks per date for bronze→silver backfill.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta

from airflow.decorators import dag, task
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator

from include.constants import DEFAULT_ARGS


@dag(
    dag_id="backfill_pipeline",
    description="Historical backfill orchestration with dynamic task mapping over date range",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    default_args={
        "owner": DEFAULT_ARGS["owner"],
        "retries": 1,
        "retry_delay": timedelta(minutes=2),
    },
    params={"date_from": "2026-01-01", "date_to": "2026-01-07"},
    tags=["backfill", "operations"],
)
def backfill_pipeline():
    start = EmptyOperator(task_id="start")

    @task
    def generate_dates(params: dict) -> list[str]:
        d_from = date.fromisoformat(params["date_from"])
        d_to = date.fromisoformat(params["date_to"])
        days = (d_to - d_from).days + 1
        return [(d_from + timedelta(days=i)).isoformat() for i in range(days)]

    @task(max_active_tis_per_dag=5)
    def backfill_date(d: str) -> dict:
        return {"date": d, "status": "ok"}

    dates = generate_dates()
    results = backfill_date.expand(d=dates)

    compaction = BashOperator(
        task_id="compact_delta",
        bash_command="spark-submit src/pyspark/maintenance/compact.py",
    )

    end = EmptyOperator(task_id="end")

    start >> dates >> results >> compaction >> end


dag = backfill_pipeline()
