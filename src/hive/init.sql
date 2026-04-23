CREATE DATABASE IF NOT EXISTS bronze LOCATION 's3a://lakehouse-bronze/';
CREATE DATABASE IF NOT EXISTS silver LOCATION 's3a://lakehouse-silver/';
CREATE DATABASE IF NOT EXISTS gold   LOCATION 's3a://lakehouse-gold/';

CREATE TABLE IF NOT EXISTS silver.orders (
    order_id    STRING,
    customer_id STRING,
    country     STRING,
    currency    STRING,
    placed_at   TIMESTAMP,
    total       DECIMAL(18,2),
    email_hash  STRING,
    ds          DATE
)
USING DELTA
PARTITIONED BY (ds)
LOCATION 's3a://lakehouse-silver/orders/';

CREATE TABLE IF NOT EXISTS gold.orders_daily (
    ds               DATE,
    country          STRING,
    currency         STRING,
    orders           BIGINT,
    gmv              DECIMAL(18,2),
    unique_customers BIGINT,
    computed_at      TIMESTAMP
)
USING DELTA
PARTITIONED BY (ds, country)
LOCATION 's3a://lakehouse-gold/orders_daily/';
