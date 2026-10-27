from pyspark.sql import *
from pyspark.sql.functions import *
from pyspark.sql.window import Window
from pyspark.sql.functions import sum as spark_sum


# ---------- Read ----------

def read_json_table(spark, base_path, table_name) -> DataFrame:
    return (
        spark.read
        .option("multiline", "true")
        .json(f"{base_path}/{table_name}")
    )


# ---------- Validation ----------

def validate_dataframe(df, name):
    print(f"\n{name}")
    print(f"Rows: {df.count()}")
    print(f"Columns: {len(df.columns)}")
    df.show(3, truncate=False)


# ---------- Cleaning ----------

def clean_customers(customers):
    return (
        customers
        .withColumn("first_name", initcap(trim(col("first_name"))))
        .withColumn("last_name", initcap(trim(col("last_name"))))
        .withColumn("city", initcap(trim(col("city"))))
        .dropDuplicates(["customer_id"])
    )


# ---------- Business Transformations ----------

def build_customer_orders(customers, orders):
    return (
        orders.alias("o")
        .join(
            broadcast(customers.alias("c")),
            col("o.customer_id") == col("c.customer_id"),
            "inner"
        )
        .select(
            col("o.order_id"),
            col("o.order_date"),
            col("o.status"),
            col("c.customer_id"),
            col("c.first_name"),
            col("c.last_name"),
            col("c.city")
        )
    )


def build_order_revenue(orders, order_items, payments):
    revenue = (
        order_items
        .groupBy("order_id")
        .agg(
            spark_sum(
                col("quantity") * col("unit_price")
            ).alias("order_total")
        )
    )

    return (
        orders
        .join(revenue, "order_id")
        .join(payments, "order_id")
    )


def build_daily_sales(order_revenue):
    return (
        order_revenue
        .withColumn("order_day", to_date(col("order_date")))
        .groupBy("order_day")
        .agg(
            spark_sum("order_total").alias("daily_revenue")
        )
        .withColumn("year", year("order_day"))
        .withColumn("month", month("order_day"))
        .orderBy("order_day")
    )


def build_product_performance(products, order_items):
    return (
        order_items
        .join(products, "product_id")
        .groupBy(
            "product_id",
            "product_name",
            "category"
        )
        .agg(
            spark_sum("quantity").alias("units_sold")
        )
        .orderBy(col("units_sold").desc())
    )


def rank_customers(order_revenue, orders):
    spending = (
        orders
        .join(order_revenue, "order_id")
        .groupBy("customer_id")
        .agg(
            spark_sum("order_total").alias("total_spent")
        )
    )

    window = Window.orderBy(col("total_spent").desc())

    return spending.withColumn(
        "customer_rank",
        dense_rank().over(window)
    )


# ---------- Writing ----------

def write_parquet(df, output_path, mode="overwrite"):
    (
        df.write
        .mode(mode)
        .option("compression", "snappy")
        .parquet(output_path)
    )


def write_partitioned_parquet(
    df,
    output_path,
    partitions
):
    (
        df.write
        .mode("overwrite")
        .option("compression", "snappy")
        .partitionBy(*partitions)
        .parquet(output_path)
    )