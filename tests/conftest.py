"""Pytest conftest: configure Airflow-compatible PYTHONPATH for DAG import tests."""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# Airflow puts dags_folder, plugins_folder, and PYTHONPATH roots in sys.path;
# emulate that here so `from include import ...` resolves cleanly.
for p in [ROOT, ROOT / "dags", ROOT / "plugins", ROOT / "include"]:
    sp = str(p)
    if sp not in sys.path:
        sys.path.insert(0, sp)

os.environ.setdefault("AIRFLOW__CORE__LOAD_EXAMPLES", "False")
os.environ.setdefault("AIRFLOW__CORE__UNIT_TEST_MODE", "True")
os.environ.setdefault("AIRFLOW_HOME", str(ROOT / ".airflow_home"))
