
import os
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

from dotenv import load_dotenv
import boto3
from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
# config={}
# with open(".env", "r") as f:
#     for line in f:
#         if line.startswith("#") or not line.strip():
#             continue
#         key, value = line.strip().split("=", 1)
#         config[key] = value


PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")

BUCKET = os.environ["S3_BUCKET"]
REGION = os.getenv("AWS_REGION", "ap-south-1")
GLUE_JOB_NAME = os.environ["GLUE_JOB_NAME"]
REDSHIFT_DATABASE = os.environ["REDSHIFT_DATABASE"]
REDSHIFT_DB_USER = os.environ["REDSHIFT_DB_USER"]
REDSHIFT_IAM_ROLE_ARN = os.environ["REDSHIFT_IAM_ROLE_ARN"]

WORKGROUP = os.getenv("REDSHIFT_WORKGROUP_NAME", "").strip()
CLUSTER_ID = os.getenv("REDSHIFT_CLUSTER_ID", "").strip()

if bool(WORKGROUP) == bool(CLUSTER_ID):
    raise ValueError(
        "Set exactly one of REDSHIFT_WORKGROUP_NAME "
        "or REDSHIFT_CLUSTER_ID in .env."
    )


def extract_and_upload():
    # Run your existing scripts from the project root.
    subprocess.run(
        [sys.executable, "-m", "scripts.extract.run_extraction"],
        cwd=PROJECT_ROOT,
        check=True,
    )

    subprocess.run(
        [sys.executable, "-m", "scripts.upload.run_upload"],
        cwd=PROJECT_ROOT,
        check=True,
    )


def run_glue_etl():
    glue = boto3.client("glue", region_name=REGION)

    response = glue.start_job_run(
        JobName=GLUE_JOB_NAME,
        Arguments={"--S3_BUCKET": BUCKET},
    )
    run_id = response["JobRunId"]
    print(f"Started Glue job: {run_id}")

    while True:
        response = glue.get_job_run(
            JobName=GLUE_JOB_NAME,
            RunId=run_id,
        )
        status = response["JobRun"]["JobRunState"]
        print(f"Glue job status: {status}")

        if status == "SUCCEEDED":
            print("Glue ETL completed successfully.")
            return

        if status in ("FAILED", "STOPPED", "TIMEOUT", "ERROR", "EXPIRED"):
            raise RuntimeError(
                f"Glue job ended with status {status}"
            )

        time.sleep(30)



def load_redshift():
    client = boto3.client("redshift-data", region_name=REGION)

    workgroup = os.environ["REDSHIFT_WORKGROUP_NAME"]
    secret_arn = os.environ["REDSHIFT_SECRET_ARN"]

    tables = [
        "customer_orders",
        "daily_sales",
        "product_performance",
        "top_customers",
    ]

    for table in tables:
        sql = f"""
        TRUNCATE TABLE retail_dw.{table};

        COPY retail_dw.{table}
        FROM 's3://{BUCKET}/processed_data/{table}/'
        IAM_ROLE '{REDSHIFT_IAM_ROLE_ARN}'
        FORMAT AS PARQUET;
        """

        response = client.execute_statement(
            WorkgroupName=workgroup,
            Database=REDSHIFT_DATABASE,
            SecretArn=secret_arn,
            Sql=sql,
        )

        statement_id = response["Id"]
        print(f"Loading {table}: {statement_id}")

        while True:
            result = client.describe_statement(Id=statement_id)
            status = result["Status"]

            if status == "FINISHED":
                print(f"Loaded {table} successfully.")
                break

            if status in ("FAILED", "ABORTED"):
                raise RuntimeError(
                    f"Redshift load failed for {table}: "
                    f"{result.get('Error', status)}"
                )

            time.sleep(5)



with DAG(
    dag_id="aws_retail_data_pipeline",
    description="MySQL to S3 to Glue to Redshift",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    default_args={
        "owner": "data-engineering",
        "retries": 1,
        "retry_delay": timedelta(minutes=2),
    },
    tags=["aws", "pyspark", "redshift"],
) as dag:

    extract_upload = PythonOperator(
        task_id="extract_mysql_and_upload_to_s3",
        python_callable=extract_and_upload,
    )

    glue_etl = PythonOperator(
        task_id="run_glue_etl",
        python_callable=run_glue_etl,
    )

    redshift_load = PythonOperator(
        task_id="load_redshift_tables",
        python_callable=load_redshift,
    )

    extract_upload >> glue_etl >> redshift_load
