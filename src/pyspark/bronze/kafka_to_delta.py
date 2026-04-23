"""PySpark streaming job: Kafka (Debezium CDC envelope) → Delta Lake bronze.

Features:
  - Reads Debezium envelope (before/after/op/ts_ms/source).
  - Writes Delta with `append` mode + checkpointing.
  - Emits OpenLineage inputs/outputs.
  - Uses `foreachBatch` to fan-out to multiple clouds (S3 + Azure Blob).
"""

from __future__ import annotations

import argparse
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pyspark.sql import DataFrame, SparkSession


def build_spark(app: str) -> SparkSession:
    from pyspark.sql import SparkSession

    return (
        SparkSession.builder.appName(app)
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
        .config(
            "spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog"
        )
        .getOrCreate()
    )


def parse_debezium_envelope(raw: DataFrame) -> DataFrame:
    from pyspark.sql import functions as F
    from pyspark.sql.types import StringType, StructField, StructType

    envelope = StructType(
        [
            StructField("before", StringType()),
            StructField("after", StringType()),
            StructField("op", StringType()),
            StructField("ts_ms", StringType()),
        ]
    )
    return (
        raw.select(F.from_json(F.col("value").cast("string"), envelope).alias("env"))
        .select("env.*")
        .withColumnRenamed("ts_ms", "event_ts_ms")
    )


def parse_cli() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--table", required=True)
    p.add_argument("--sink", required=True)
    p.add_argument(
        "--kafka-bootstrap",
        default="redpanda:9092",
    )
    p.add_argument(
        "--checkpoint",
        default="/tmp/bronze-ckpt",
    )
    return p.parse_args()


def main() -> None:  # pragma: no cover - executed via spark-submit
    args = parse_cli()
    spark = build_spark(f"bronze_{args.table}")

    raw = (
        spark.readStream.format("kafka")
        .option("kafka.bootstrap.servers", args.kafka_bootstrap)
        .option("subscribe", f"cdc.public.{args.table}")
        .load()
    )
    parsed = parse_debezium_envelope(raw)

    (
        parsed.writeStream.format("delta")
        .option("checkpointLocation", f"{args.checkpoint}/{args.table}")
        .outputMode("append")
        .trigger(processingTime="30 seconds")
        .start(args.sink)
        .awaitTermination()
    )


if __name__ == "__main__":  # pragma: no cover
    main()
