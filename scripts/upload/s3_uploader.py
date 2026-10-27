"""Upload JSON files to Amazon S3."""

import boto3

from config.config import AWS_REGION, S3_BUCKET


def upload_file(local_file, s3_key):
    if not S3_BUCKET:
        raise ValueError("Set S3_BUCKET in your .env file.")

    s3 = boto3.client("s3", region_name=AWS_REGION)

    s3.upload_file(
        str(local_file),
        S3_BUCKET,
        s3_key
    )

    print(f"Uploaded: s3://{S3_BUCKET}/{s3_key}")