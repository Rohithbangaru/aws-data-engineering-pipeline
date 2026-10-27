AWS Retail Data Engineering Pipeline

An end-to-end batch data engineering project that moves synthetic retail data from a local MySQL database into Amazon S3, transforms it with AWS Glue and PySpark, and prepares analytical datasets for Amazon Redshift. Apache Airflow is used to orchestrate the workflow.


Project Overview
The pipeline demonstrates common data engineering tasks: relational source data generation, extraction, raw data storage, distributed transformations, data quality validation, warehouse loading, and workflow orchestration.

Technology Stack
- Python — source-data generation, extraction, S3 uploads, and orchestration support
- MySQL — relational source database
- Amazon S3 — raw JSON and transformed Parquet storage
- AWS Glue / PySpark — batch transformation and aggregation
- Amazon Redshift — analytical warehouse tables
- Apache Airflow — task dependencies, retries, and workflow scheduling/triggering
- Docker Compose — local Airflow runtime

Data Model and Outputs
The source system contains five tables:
- customers
- products
- orders
- order_items
- payments
The generated dataset used during development contained approximately 95,695 rows in total

