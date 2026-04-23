#!/usr/bin/env bash
set -euo pipefail

echo "[bootstrap] bringing stack up"
docker compose up -d
echo "[bootstrap] waiting for airflow"
sleep 20
echo "[bootstrap] creating kafka topics"
docker compose exec -T redpanda rpk topic create cdc.public.orders cdc.public.customers cdc.public.order_lines 2>/dev/null || true
echo "[bootstrap] registering Debezium connectors"
curl -s -X POST -H "Content-Type: application/json" \
  --data @src/debezium/register-postgres.json \
  http://localhost:8083/connectors || true
echo "[bootstrap] done"
