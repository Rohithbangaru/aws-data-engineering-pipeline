"""Extract a MySQL table into a JSON file."""

import pandas as pd
from config.config import get_connection
from pathlib import Path


def extract_table(table_name, output_folder):
    connection = get_connection()

    try:
        df = pd.read_sql_query(
            f"SELECT * FROM `{table_name}`",
            connection
        )

        Path(output_folder).mkdir(parents=True, exist_ok=True)

        output_file = f"{output_folder}/{table_name}.json"

        df.to_json(
            output_file,
            orient="records",
            indent=2,
            date_format="iso"
        )

        print(f"Extracted {table_name}: {len(df)} rows")

    finally:
        connection.close()