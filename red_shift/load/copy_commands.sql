
-- Load customer orders
TRUNCATE TABLE retail_dw.customer_orders;

COPY retail_dw.customer_orders
FROM 's3://YOUR_BUCKET_NAME/processed_data/customer_orders/'
IAM_ROLE 'arn:aws:iam::YOUR_ACCOUNT_ID:role/YOUR_REDSHIFT_IAM_ROLE'
FORMAT AS PARQUET;

-- Load daily sales
TRUNCATE TABLE retail_dw.daily_sales;

COPY retail_dw.daily_sales
FROM 's3://YOUR_BUCKET_NAME/processed_data/daily_sales/'
IAM_ROLE 'arn:aws:iam::YOUR_ACCOUNT_ID:role/YOUR_REDSHIFT_IAM_ROLE'
FORMAT AS PARQUET;

-- Load product performance
TRUNCATE TABLE retail_dw.product_performance;

COPY retail_dw.product_performance
FROM 's3://YOUR_BUCKET_NAME/processed_data/product_performance/'
IAM_ROLE 'arn:aws:iam::YOUR_ACCOUNT_ID:role/YOUR_REDSHIFT_IAM_ROLE'
FORMAT AS PARQUET;

-- Load top customers
TRUNCATE TABLE retail_dw.top_customers;

COPY retail_dw.top_customers
FROM 's3://YOUR_BUCKET_NAME/processed_data/top_customers/'
IAM_ROLE 'arn:aws:iam::YOUR_ACCOUNT_ID:role/YOUR_REDSHIFT_IAM_ROLE'
FORMAT AS PARQUET;
