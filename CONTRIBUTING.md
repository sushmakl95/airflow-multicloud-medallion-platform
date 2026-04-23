# Contributing

## Dev setup
```bash
python -m venv .venv && source .venv/Scripts/activate
pip install -r requirements-dev.txt
```

## Before pushing
```bash
make ci
```

Which runs: ruff + yamllint + DAG import + unit tests + JSON validation.

## Adding a new DAG
1. Create `airflow/dags/<name>.py`.
2. Add a DagBag import test: DAG must load in under 2 seconds with no exceptions.
3. Add DAG tags (team/domain).
4. Register any new Dataset URIs in `airflow/include/datasets.py`.
