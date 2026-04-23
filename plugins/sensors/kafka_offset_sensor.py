"""Deferrable sensor: waits until Kafka end-offset advances by ≥ min_records.

In production this would subclass BaseSensorOperator + Trigger. For the demo
we keep the logic pure-Python so it's unit-testable without Airflow runtime.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Offset:
    topic: str
    partition: int
    offset: int


def advanced_enough(
    current: list[Offset],
    baseline: list[Offset],
    min_records: int,
) -> bool:
    """Return True if total delta offset ≥ min_records."""
    base = {(o.topic, o.partition): o.offset for o in baseline}
    delta = 0
    for c in current:
        delta += max(0, c.offset - base.get((c.topic, c.partition), 0))
    return delta >= min_records
