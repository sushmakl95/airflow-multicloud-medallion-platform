# Runbook

## DAG import error
```bash
docker compose exec airflow airflow dags list-import-errors
```
If `from include import ...` fails — check that `/opt/airflow/include` is mounted.

## Stuck task_instance
Check `max_active_tis_per_dag` and `pool` limits. Clear state:
```bash
docker compose exec airflow airflow tasks clear --dag-id cdc_medallion --start-date <x> --end-date <y>
```

## Debezium connector not producing
```bash
curl http://localhost:8083/connectors/pg-orders-source/status
curl -X POST http://localhost:8083/connectors/pg-orders-source/restart
```

## Delta compaction runaway
`OPTIMIZE … ZORDER BY` can consume lots of memory. Inspect active queries; scale Spark driver if needed.

## Re-register table in Hive Metastore
```sql
MSCK REPAIR TABLE silver.orders;
ALTER TABLE silver.orders RECOVER PARTITIONS;
```

## OpenLineage events not appearing in Marquez
Verify `OPENLINEAGE_URL` + `OPENLINEAGE_NAMESPACE` env vars; hit `/api/v1/namespaces/<ns>`.
