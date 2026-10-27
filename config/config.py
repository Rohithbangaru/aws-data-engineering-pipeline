"""Shared configuration for local scripts and Airflow."""

import os
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")

# Docker Compose sets host.docker.internal. If scripts are run directly on
# the host, translate that Docker-only hostname back to localhost.
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost").strip()
if MYSQL_HOST == "host.docker.internal" and not Path("/.dockerenv").exists():
    MYSQL_HOST = "localhost"

MYSQL_CONFIG = {
    "host": MYSQL_HOST,
    "port": int(os.getenv("MYSQL_PORT", "3306")),
    "database": os.getenv("MYSQL_DATABASE", "aws_data_engineering_project"),
    "user": os.getenv("MYSQL_USER", "root"),
    "password": os.getenv("MYSQL_PASSWORD", ""),
}

S3_BUCKET = os.getenv("S3_BUCKET", "").strip()
AWS_REGION = os.getenv("AWS_REGION", "ap-south-1").strip()
RECORDS = {
    "customers": int(os.getenv("CUSTOMER_RECORDS", "5000")),
    "products": int(os.getenv("PRODUCT_RECORDS", "500")),
    "orders": int(os.getenv("ORDER_RECORDS", "20000")),
}

def get_connection():
    if not MYSQL_CONFIG["password"]:
        raise RuntimeError(
            "MYSQL_PASSWORD is missing. Check the project-root .env file."
        )
    import pymysql
    return pymysql.connect(
        host=MYSQL_CONFIG["host"],
        port=MYSQL_CONFIG["port"],
        user=MYSQL_CONFIG["user"],
        password=MYSQL_CONFIG["password"],
        database=MYSQL_CONFIG["database"],
        autocommit=True,
    )
