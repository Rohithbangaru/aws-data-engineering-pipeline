# from config.config import S3_BUCKET

# RAW_S3_PATH = f"s3a://{S3_BUCKET}/raw_data"
# PROCESSED_S3_PATH = f"s3a://{S3_BUCKET}/processed_data"

# TABLES = [
#     "customers",
#     "products",
#     "orders",
#     "order_items",
#     "payments"
# ]

import sys
from awsglue.utils import getResolvedOptions

args = getResolvedOptions(
    sys.argv,
    [
        "JOB_NAME",
        "S3_BUCKET"
    ]
)

JOB_NAME = args["JOB_NAME"]

S3_BUCKET = args["S3_BUCKET"]

RAW_S3_PATH = f"s3://{S3_BUCKET}/raw_data"

PROCESSED_S3_PATH = f"s3://{S3_BUCKET}/processed_data"

TABLES = [
    "customers",
    "products",
    "orders",
    "order_items",
    "payments"
]