"""Configuration defaults for the Glue ETL job.

The Glue job should receive S3_BUCKET as a job argument or environment setting
when deployed. The empty default intentionally prevents accidental use of a
personal bucket when this code is copied to another environment.
"""
import os

S3_BUCKET = os.getenv("S3_BUCKET", "").strip()
if not S3_BUCKET:
    # Keep imports possible during local inspection; the job entry point should
    # validate this value before attempting to read or write S3 paths.
    RAW_S3_PATH = ""
    PROCESSED_S3_PATH = ""
else:
    RAW_S3_PATH = f"s3://{S3_BUCKET}/raw_data"
    PROCESSED_S3_PATH = f"s3://{S3_BUCKET}/processed_data"

TABLES = ["customers", "products", "orders", "order_items", "payments"]
