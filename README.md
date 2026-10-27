# AWS Retail Data Engineering Pipeline

> **Work in progress:** this repository is being completed in stages. The components listed below are not yet verified as a fully working end-to-end pipeline.

## Project goal

Build a batch analytics pipeline using synthetic retail data: local MySQL → JSON extraction → Amazon S3 raw layer → AWS Glue/PySpark transformations → S3 Parquet outputs → Amazon Redshift analytics, orchestrated by Apache Airflow.

## Planned technology stack

- Python, MySQL, pandas, Faker
- Amazon S3, AWS Glue, PySpark, Amazon Redshift
- Apache Airflow (planned local Docker setup)
- SQL and data-quality validation

## Repository layout

- `config/`: shared local configuration
- `mysql/`: source schema and synthetic-data generators
- `scripts/`: database initialization, extraction and upload entry points
- `glue/`: Glue ETL jobs, transformations and quality checks
- `local_processing/`: local ETL development code
- `red_shift/`: warehouse schema and load SQL
- `airflow/`: planned DAG and orchestration SQL
- `docs/`: project status and implementation notes

## Local setup (initial)

1. Create and activate a Python virtual environment.
2. Install dependencies with `python -m pip install -r requirements.txt`.
3. Copy `.env.example` to `.env` and configure local MySQL and your S3 bucket.
4. Configure AWS credentials using an AWS CLI profile or another supported AWS credential provider. Do not add AWS access keys to source files.
5. Initialize the local MySQL schema: `python -m scripts.initialize_database`.
6. Generate the synthetic dataset: `python -m mysql.generate_data.generate_data_main`. The command fills missing rows up to the configured targets and can be rerun. Use `--reset` only when you intentionally want to delete and rebuild all generated rows.

See [`docs/PHASE_2_REPORT.md`](docs/PHASE_2_REPORT.md) for source-data generation behavior and reset safeguards. The Airflow Docker configuration, warehouse loading instructions and verified end-to-end evidence will be added as those stages are completed.

## Security

Never commit `.env`, passwords, AWS access keys, IAM secrets, or private data. Use least-privilege IAM roles/policies. If a secret was committed previously, rotate it and clean the Git history before making the repository public.

## Project status

See [`docs/PROJECT_STATUS.md`](docs/PROJECT_STATUS.md) for the current known implementation status. A file existing in the repository is not proof that the corresponding AWS stage has been successfully executed.
