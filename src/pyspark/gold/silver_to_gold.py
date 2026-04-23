"""Silver → Gold: daily aggregates with MERGE INTO for idempotent writes."""

from __future__ import annotations

import argparse
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pyspark.sql import DataFrame, SparkSession


def aggregate(df: DataFrame) -> DataFrame:
    from pyspark.sql import functions as F

    return (
        df.groupBy("ds", "country", "currency")
        .agg(
            F.countDistinct("order_id").alias("orders"),
            F.sum("total").alias("gmv"),
            F.countDistinct("customer_id").alias("unique_customers"),
        )
        .withColumn("computed_at", F.current_timestamp())
    )


def build_spark() -> SparkSession:  # pragma: no cover
    from pyspark.sql import SparkSession

    return (
        SparkSession.builder.appName("silver_to_gold")
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
        .config(
            "spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog"
        )
        .getOrCreate()
    )


def parse_cli() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--warehouse", required=True)
    return p.parse_args()


def main() -> None:  # pragma: no cover
    args = parse_cli()
    spark = build_spark()
    silver = spark.read.format("delta").load(f"{args.warehouse}/silver/orders")
    gold = aggregate(silver)
    gold.write.format("delta").mode("overwrite").save(f"{args.warehouse}/gold/orders_daily")


if __name__ == "__main__":  # pragma: no cover
    main()
