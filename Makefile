SHELL := bash
PY := python

.PHONY: help install lint test ci compose-up compose-down airflow-ui marquez-ui datahub-ui trigger-cdc clean

help:
	@echo "install      - install python + airflow test deps"
	@echo "lint         - ruff + black --check + yamllint"
	@echo "test         - DAG import tests + pure-python unit tests"
	@echo "ci           - lint + test (matches GH Actions)"
	@echo "compose-up   - full stack"
	@echo "airflow-ui   - print link"
	@echo "marquez-ui   - print link"
	@echo "trigger-cdc  - trigger the cdc_medallion DAG"
	@echo "clean        - remove build artifacts"

install:
	$(PY) -m pip install -U pip
	$(PY) -m pip install -r requirements-dev.txt

lint:
	ruff check .
	black --check airflow src tests
	yamllint .

test:
	pytest tests/ -v

ci: lint test

compose-up:
	docker compose up -d

compose-down:
	docker compose down -v

airflow-ui:
	@echo "Airflow UI: http://localhost:8080 (airflow/airflow)"

marquez-ui:
	@echo "Marquez:   http://localhost:3000"

datahub-ui:
	@echo "DataHub:   http://localhost:9002 (datahub/datahub)"

trigger-cdc:
	docker compose exec airflow airflow dags trigger cdc_medallion

clean:
	rm -rf .pytest_cache .ruff_cache build dist
	find . -type d -name __pycache__ -exec rm -rf {} +
