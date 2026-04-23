# ADRs

## ADR-001 — Astronomer-style project layout
**Decision:** Root-level `dags/`, `plugins/`, `include/` instead of a wrapping `airflow/` directory.
**Why:** Avoids conflict with the `airflow` package namespace at import time during pytest. Matches Astronomer Cosmos convention that recruiters recognise.

## ADR-002 — Multi-cloud bronze fan-out
**Decision:** Each bronze write publishes to S3 **and** Azure Blob (and optionally GCS).
**Why:** Demonstrates portability + provides disaster recovery across cloud providers.
**Consequences:** Storage cost 2× in prod; offset by lifecycle rules expiring data ≥90 days.

## ADR-003 — DAG-import tests, no Spark in required CI
**Decision:** Required CI tests that DAGs parse cleanly + unit tests custom operators/helpers. PySpark and Docker-based integration run in a separate optional workflow.
**Why:** DAG import failures are the #1 cause of Airflow production incidents; catching them in CI is highest ROI. Spark integration is valuable but slow and credential-heavy.

## ADR-004 — Debezium + dlt dual ingestion
**Decision:** Real-time CDC uses Debezium; batch/API ingestion uses `dlt`.
**Why:** Right tool per pattern. Debezium has low-latency row-level CDC; dlt has schema-evolution-aware pagination and is Pythonic enough to embed in Airflow tasks.

## ADR-005 — OpenLineage for lineage, Marquez + DataHub for catalogue
**Decision:** OpenLineage events emitted automatically by Airflow + Spark; Marquez is the lineage store; DataHub hosts the business-glossary and catalogue UI.
**Why:** Marquez is simple and Airflow-native. DataHub has a richer catalogue (glossaries, domains, assertions).

## ADR-006 — Scala UDFs alongside PySpark
**Decision:** Ship a small SBT Scala module (`src/scala/`) with UDFs used by the silver layer.
**Why:** Recruiters ask about polyglot Spark skill; some UDFs (regex-heavy, JVM-interop) are materially faster in Scala than Python.
