"""Delta maintenance: OPTIMIZE + VACUUM + Z-ORDER."""

from __future__ import annotations


def generate_sql(table: str, zorder_cols: list[str], retention_hours: int = 168) -> list[str]:
    zorder = ", ".join(zorder_cols)
    return [
        f"OPTIMIZE {table} ZORDER BY ({zorder})",
        f"VACUUM {table} RETAIN {retention_hours} HOURS",
    ]


def main() -> None:  # pragma: no cover
    print(generate_sql("delta.`s3://lakehouse-gold/orders_daily/`", ["ds", "country"]))


if __name__ == "__main__":  # pragma: no cover
    main()
