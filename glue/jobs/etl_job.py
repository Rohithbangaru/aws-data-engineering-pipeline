
import sys

from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from pyspark.sql import functions as F
from pyspark.sql.window import Window


# Job parameters
args = getResolvedOptions(sys.argv, ["JOB_NAME", "S3_BUCKET"])
bucket = args["S3_BUCKET"]

raw_path = f"s3://{bucket}/raw_data"
output_path = f"s3://{bucket}/processed_data"

# Start Glue and Spark
sc = SparkContext.getOrCreate()
glue_context = GlueContext(sc)
spark = glue_context.spark_session

job = Job(glue_context)
job.init(args["JOB_NAME"], args)


# Read the JSON datasets
def read_table(name):
    return (
        spark.read
        .option("multiline", "true")
        .json(f"{raw_path}/{name}/{name}.json")
    )


customers = read_table("customers").dropDuplicates(["customer_id"])
products = read_table("products").dropDuplicates(["product_id"])
orders = read_table("orders").dropDuplicates(["order_id"])
items = read_table("order_items").dropDuplicates(["order_item_id"])
payments = read_table("payments").dropDuplicates(["payment_id"])


# Clean order dates and text fields
orders = (
    orders
    .withColumn(
        "order_date",
        F.to_timestamp(
            F.regexp_replace(
                F.regexp_replace("order_date", "T", " "),
                "Z$", ""
            )
        )
    )
    .withColumn("status", F.initcap(F.trim("status")))
)

customers = customers.withColumn(
    "customer_id", F.col("customer_id").cast("long")
)

# 1. Customer orders — keep the exact Redshift target columns
customer_orders = (
    orders
    .join(customers.select("customer_id"), "customer_id", "inner")
    .select("order_id", "customer_id", "order_date", "status")
)

# Only successful payments count as paid revenue
successful_payments = (
    payments
    .filter(F.upper(F.trim("payment_status")) == "SUCCESS")
    .select(
        "order_id",
        F.col("amount").cast("decimal(18,2)").alias("amount")
    )
)

paid_orders = orders.join(successful_payments, "order_id", "inner")

# 2. Daily sales
daily_sales = (
    paid_orders
    .withColumn("order_day", F.to_date("order_date"))
    .groupBy("order_day")
    .agg(
        F.sum("amount").cast("decimal(18,2)").alias("daily_revenue")
    )
    .withColumn("year", F.year("order_day"))
    .withColumn("month", F.month("order_day"))
    .select("order_day", "daily_revenue", "year", "month")
)

# 3. Product performance — units sold in successfully paid orders
product_performance = (
    items
    .join(successful_payments.select("order_id"), "order_id", "inner")
    .join(products, "product_id", "inner")
    .groupBy("product_id", "product_name", "category")
    .agg(F.sum("quantity").cast("long").alias("units_sold"))
    .select("product_id", "product_name", "category", "units_sold")
)

# 4. Customer spending and ranking
top_customers = (
    paid_orders
    .groupBy("customer_id")
    .agg(
        F.sum("amount").cast("decimal(18,2)").alias("total_spent")
    )
    .withColumn(
        "customer_rank",
        F.dense_rank().over(
            Window.orderBy(F.col("total_spent").desc())
        )
    )
    .select("customer_id", "total_spent", "customer_rank")
)

# Write the four datasets as Snappy-compressed Parquet
datasets = {
    "customer_orders": customer_orders,
    "daily_sales": daily_sales,
    "product_performance": product_performance,
    "top_customers": top_customers,
}

for name, df in datasets.items():
    count = df.count()

    if count == 0:
        raise ValueError(f"{name} contains no records.")

    (
        df.write
        .mode("overwrite")
        .option("compression", "snappy")
        .parquet(f"{output_path}/{name}")
    )

    print(f"Written {name}: {count:,} rows")

job.commit()
print("Phase 4 Glue ETL completed successfully.")
