# Project status

This repository is a work in progress. Code presence does not mean a stage has been executed successfully in AWS.

## Intended workflow

1. Generate synthetic retail data in local MySQL.
2. Extract the MySQL tables to JSON.
3. Upload the raw files to Amazon S3.
4. Transform the raw data with AWS Glue and PySpark.
5. Validate transformed data with data-quality checks.
6. Load analytical datasets into Amazon Redshift.
7. Orchestrate the workflow with Apache Airflow.

## Current known status from the reviewed project snapshot

- MySQL schema and data-generator scripts exist; the main generator needs to call all generators in the correct order.
- MySQL-to-JSON extraction and S3 upload scripts exist but require execution and validation.
- AWS Glue/PySpark ETL and data-quality code exist but need integration and AWS execution testing.
- Redshift schema and COPY SQL exist but loading is not yet validated; IAM role and output schemas must be configured.
- The Airflow DAG and accompanying SQL files were empty in the reviewed snapshot.
- End-to-end execution has not yet been demonstrated by this repository snapshot.

Update this status only after tests have actually been run.
