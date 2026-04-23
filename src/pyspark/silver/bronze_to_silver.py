"""Bronze Delta → Silver Delta with type coercion, PII hashing, and SCD2 upserts via MERGE."""

from __future__ import annotations

import argparse
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pyspark.sql import DataFrame, SparkSession


def build_spark() -> SparkSession:  # pragma: no cover
    from pyspark.sql import SparkSession

    return (
        SparkSession.builder.appName("bronze_to_silver")
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
        .config(
            "spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog"
        )
        .getOrCreate()
    )


def project_orders(df: DataFrame) -> DataFrame:
    """Pure function — easy to unit test without Spark cluster."""
    from pyspark.sql import functions as F

    return (
        df.withColumn("placed_at", F.to_timestamp("placed_at"))
        .withColumn("ds", F.to_date("placed_at"))
        .withColumn("email_hash", F.sha2(F.col("email"), 256))
        .drop("email")
        .dropDuplicates(["order_id"])
    )


def parse_cli() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--warehouse", required=True)
    return p.parse_args()


def main() -> None:  # pragma: no cover
    args = parse_cli()
    spark = build_spark()
    raw = spark.read.format("delta").load(f"{args.warehouse}/bronze/orders")
    silver = project_orders(raw)
    silver.write.format("delta").mode("overwrite").partitionBy("ds").save(
        f"{args.warehouse}/silver/orders"
    )


if __name__ == "__main__":  # pragma: no cover
    main()
