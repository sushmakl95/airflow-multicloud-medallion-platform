from __future__ import annotations

from plugins.sensors.kafka_offset_sensor import Offset, advanced_enough


def test_advances_when_delta_ge_threshold():
    base = [Offset("t", 0, 100), Offset("t", 1, 100)]
    curr = [Offset("t", 0, 200), Offset("t", 1, 200)]
    assert advanced_enough(curr, base, min_records=100) is True


def test_does_not_advance_when_delta_small():
    base = [Offset("t", 0, 100)]
    curr = [Offset("t", 0, 110)]
    assert advanced_enough(curr, base, min_records=100) is False


def test_handles_missing_partition_in_baseline():
    base = []
    curr = [Offset("t", 5, 50)]
    assert advanced_enough(curr, base, min_records=10) is True
