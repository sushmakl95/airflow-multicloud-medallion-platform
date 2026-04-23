"""Shared SLA / failure / success callbacks."""

from __future__ import annotations

from typing import Any


def slack_on_failure(context: dict[str, Any]) -> None:
    task = context.get("task_instance")
    if task is None:
        return
    print(
        "[slack] :red_circle: DAG {} task {} failed (run_id={})".format(
            task.dag_id, task.task_id, context.get("run_id")
        )
    )


def datadog_on_sla_miss(*args: Any, **kwargs: Any) -> None:
    print("[datadog] sla_miss recorded")


def emit_openlineage_on_success(context: dict[str, Any]) -> None:
    print("[openlineage] success facet emitted")
