#!/usr/bin/env bash
# Legacy Sqoop pattern (documented). In this repo we replaced Sqoop with Debezium
# CDC + dlt; this script is preserved for teams that still run Sqoop-based ingest.

set -euo pipefail

sqoop import \
  --connect jdbc:mysql://mysql:3306/inventory \
  --username debezium --password debezium \
  --table products \
  --target-dir s3a://lakehouse-bronze/inventory/products/ \
  --as-parquetfile \
  --split-by product_id \
  --m 4 \
  --direct

sqoop import \
  --connect jdbc:mysql://mysql:3306/inventory \
  --username debezium --password debezium \
  --table stock_levels \
  --target-dir s3a://lakehouse-bronze/inventory/stock_levels/ \
  --as-parquetfile \
  --incremental lastmodified \
  --check-column updated_at \
  --last-value "$(date -d '1 hour ago' +%F\ %T)"
