
import sys

from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from pyspark.sql import functions as F


args = getResolvedOptions(sys.argv, ["JOB_NAME", "S3_BUCKET"])
output_path = f"s3://{args['S3_BUCKET']}/processed_data"

sc = SparkContext.getOrCreate()
glue_context = GlueContext(sc)
spark = glue_context.spark_session

job = Job(glue_context)
job.init(args["JOB_NAME"], args)

failures = []


def check_dataset(name, required_columns, key_column):
    df = spark.read.parquet(f"{output_path}/{name}")
    row_count = df.count()

    print(f"\nChecking {name}: {row_count:,} rows")

    if row_count == 0:
        failures.append(f"{name}: dataset is empty")
        return

    # Check required columns for null values
    for column in required_columns:
        if df.filter(F.col(column).isNull()).limit(1).count():
            failures.append(f"{name}: null values in {column}")
        else:
            print(f"PASS: {column} has no null values")

    # Check duplicate business keys
    duplicates = (
        df.groupBy(key_column)
        .count()
        .filter(F.col("count") > 1)
        .limit(1)
        .count()
    )

    if duplicates:
        failures.append(f"{name}: duplicate {key_column} values")
    else:
        print(f"PASS: {key_column} has no duplicates")

    numeric_rules = {
        "daily_sales": ("daily_revenue", False),
        "product_performance": ("units_sold", True),
        "top_customers": ("total_spent", False),
        "top_customers_rank": ("customer_rank", True),
    }

    rule = numeric_rules.get(name)

    if rule:
        column, must_be_positive = rule
        condition = F.col(column) <= 0 if must_be_positive else F.col(column) < 0

        if df.filter(
            F.col(column).isNull() | condition
        ).limit(1).count():
            failures.append(f"{name}: invalid values in {column}")
        else:
            print(f"PASS: {column} values are valid")


# Dataset, required fields, unique business key
checks = [
    ("customer_orders", ["order_id", "customer_id", "order_date"], "order_id"),
    ("daily_sales", ["order_day", "daily_revenue"], "order_day"),
    ("product_performance", ["product_id", "units_sold"], "product_id"),
    ("top_customers", ["customer_id", "total_spent", "customer_rank"], "customer_id"),
]

for dataset, columns, key in checks:
    check_dataset(dataset, columns, key)

print("\nDATA QUALITY SUMMARY")

if failures:
    for failure in failures:
        print(f"FAIL: {failure}")

    raise RuntimeError(
        f"Data quality failed: {len(failures)} issue(s) found."
    )

print("PASS: all data quality checks completed successfully.")
job.commit()
