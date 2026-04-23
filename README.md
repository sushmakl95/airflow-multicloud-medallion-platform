# airflow-multicloud-medallion-platform

Production-grade **Apache Airflow 2.9** orchestrator driving an end-to-end medallion data platform across **three clouds** (AWS via LocalStack, Azure via Azurite, GCP via fake-gcs-server). Debezium-based CDC → Kafka → PySpark + Scala-Spark medallion → Delta Lake on Hive Metastore → Great Expectations DQ → **OpenLineage** → Marquez + **DataHub** catalog.

![CI](https://github.com/sushmakl95/airflow-multicloud-medallion-platform/actions/workflows/ci.yml/badge.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Airflow](https://img.shields.io/badge/airflow-2.9+-red)
![Python](https://img.shields.io/badge/python-3.11-informational)

---

## Architecture

```mermaid
flowchart LR
    subgraph Sources["📥 Sources"]
        PG[(Postgres OLTP<br/>orders / customers)]
        MY[(MySQL OLTP<br/>inventory)]
        API[[REST API<br/>partner feed]]
        CSV[[CSV drops<br/>catalog]]
    end

    subgraph Ingest["🌀 Real-time CDC"]
        DBZ[Debezium Connectors<br/>PG + MySQL]
        KC[Kafka Connect]
        KFK{{Apache Kafka<br/>Redpanda}}
        DLT[dlt loader<br/>API + CSV]
    end

    subgraph MultiCloud["☁️ Multi-cloud Bronze landing"]
        S3[(AWS S3<br/>via LocalStack)]
        ABS[(Azure Blob<br/>via Azurite)]
        GCS[(GCS<br/>via fake-gcs-server)]
    end

    subgraph Transform["⚙️ Medallion (Spark)"]
        BZ[Bronze Delta<br/>PySpark]
        SV[Silver Delta<br/>PySpark + Scala UDFs]
        GD[Gold Delta<br/>PySpark]
        HMS[(Hive Metastore<br/>+ Iceberg catalog)]
    end

    subgraph DQ["✅ Quality"]
        GE[Great Expectations]
        SOD[Soda Core]
    end

    subgraph Orch["🎯 Airflow 2.9"]
        DAG1[DAG: cdc_medallion<br/>TaskFlow + Datasets]
        DAG2[DAG: api_ingest<br/>DynamicTaskMapping]
        DAG3[DAG: hourly_micro_batch<br/>Deferrable sensors]
        DAG4[DAG: backfill<br/>KubernetesPodOperator]
    end

    subgraph Obs["🔍 Observability"]
        OL[OpenLineage emitter]
        MQ[Marquez]
        DH[DataHub catalog]
        ES[Elementary]
    end

    subgraph Consume["📊 Consume"]
        TRN[Trino]
        SUP[Superset]
    end

    PG --> DBZ
    MY --> DBZ
    DBZ --> KC --> KFK
    API --> DLT
    CSV --> DLT
    DLT --> S3
    KFK --> BZ
    BZ --> S3
    BZ --> ABS
    BZ --> GCS
    BZ --> SV --> GD
    SV --> HMS
    GD --> HMS
    HMS --> TRN --> SUP
    GE -. tests .-> SV
    GE -. tests .-> GD
    SOD -. tests .-> GD
    DAG1 -. drives .-> KFK
    DAG1 -. drives .-> BZ
    DAG1 -. drives .-> SV
    DAG1 -. drives .-> GD
    DAG2 -. drives .-> DLT
    DAG3 -. drives .-> SV
    DAG4 -. drives .-> BZ
    BZ -. lineage .-> OL
    SV -. lineage .-> OL
    GD -. lineage .-> OL
    OL --> MQ
    OL --> DH
```

Full **sequence diagrams** in [`docs/architecture.md`](docs/architecture.md).

---

## Tech highlights

| Capability | Tools |
|---|---|
| **Orchestration** | Airflow 2.9 (TaskFlow, datasets, dynamic task mapping, task groups, pools, SLAs, deferrable sensors, KubernetesPodOperator, callbacks) |
| **CDC** | Debezium 2.6 connectors for Postgres + MySQL |
| **Streaming** | Kafka (Redpanda), Kafka Connect |
| **Ingestion** | dlt (data load tool) for API + CSV paths |
| **Transformation** | PySpark 3.5, Scala-Spark (SBT) custom UDFs, Delta Lake |
| **Catalog** | Hive Metastore, Iceberg REST catalog (Nessie), AWS Glue via LocalStack |
| **Data Quality** | Great Expectations 0.18, Soda Core |
| **Lineage** | OpenLineage emitter → Marquez + DataHub |
| **Multi-cloud** | AWS S3 (LocalStack), Azure Blob (Azurite), GCS (fake-gcs-server) |
| **Query** | Trino (Starburst OSS), Superset |
| **Legacy pattern** | Hive + Sqoop ingestion demo (documented & scripted) |
| **Languages** | Python, **Scala** (Spark UDFs), **Java** (custom operator), SQL, Shell |
| **IaC** | Terraform + Terraform CDK |
| **CI/CD** | GitHub Actions (lint + DAG import + unit tests + JSON validate), Jenkinsfile, GitLab CI |

---

## Quickstart

```bash
make install
make lint              # ruff + black + yamllint
make test              # DAG import + helper unit tests
make compose-up        # full stack (LocalStack + Azurite + Kafka + Airflow + Marquez)
make airflow-ui        # http://localhost:8080
make trigger-cdc       # trigger cdc_medallion DAG
make marquez-ui        # http://localhost:3000
make datahub-ui        # http://localhost:9002
```

---

## Project layout

```
airflow-multicloud-medallion-platform/
├── .github/workflows/ci.yml
├── Makefile, Jenkinsfile, .gitlab-ci.yml, docker-compose.yml
├── docs/                    # architecture, runbook, lineage guide
├── airflow/
│   ├── dags/                # 4 DAGs showcasing different Airflow 2.9 features
│   ├── plugins/
│   │   ├── operators/       # custom operators (Delta merge, Azure, ODCS contract)
│   │   ├── sensors/         # deferrable sensors
│   │   ├── hooks/           # Azurite, Nessie, Marquez hooks
│   │   └── lineage/         # OpenLineage backend config
│   └── include/             # shared helpers used by DAGs
├── src/
│   ├── pyspark/             # bronze/silver/gold PySpark jobs
│   ├── scala/               # Scala-Spark module (SBT) with UDFs
│   ├── debezium/            # connector JSON configs (PG, MySQL)
│   ├── dlt/                 # dlt pipelines for API + CSV
│   ├── ge/                  # Great Expectations project
│   ├── hive/                # metastore bootstrap SQL
│   └── sqoop/               # legacy Sqoop commands (documented)
├── infra/
│   ├── terraform/           # HCL — buckets, metastore, Marquez backend
│   └── azurite/             # Azurite config + containers seed
├── tests/
│   ├── unit/                # pure-python tests
│   └── dags/                # Airflow DagBag import tests (no docker)
├── scripts/                 # bootstrap, seed, trigger
├── configs/                 # OpenMetadata, Great Expectations, Soda, Trino
└── data/samples/
```

---

## Zero-cost posture

Every cloud in the architecture has a free local substitute (LocalStack, Azurite, fake-gcs-server, Redpanda, Marquez, DataHub). Production configs for each cloud are committed verbatim and documented in `docs/cloud-parity.md`.

## License

MIT.
