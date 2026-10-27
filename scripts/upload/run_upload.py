"""Upload extracted JSON files to S3 and verify their existence."""

import boto3
from config.config import PROJECT_ROOT, S3_BUCKET, AWS_REGION
from scripts.upload.s3_uploader import upload_file

TABLES = ["customers", "products", "orders", "order_items", "payments"]

def main():
    if not S3_BUCKET:
        raise ValueError("Set S3_BUCKET in your .env file.")

    raw_root = PROJECT_ROOT / "raw_data"
    s3 = boto3.client("s3", region_name=AWS_REGION)

    for table in TABLES:
        local_file = raw_root / table / f"{table}.json"
        if not local_file.exists():
            raise FileNotFoundError(f"{local_file} not found. Run extraction first.")
        s3_key = f"raw_data/{table}/{table}.json"
        upload_file(local_file, s3_key)
        s3.head_object(Bucket=S3_BUCKET, Key=s3_key)
        print(f"Verified: {s3_key}")

    print("\nPhase 3 completed successfully.")

if __name__ == "__main__":
    main()
