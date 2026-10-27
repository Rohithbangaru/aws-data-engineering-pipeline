"""Create the project database and source tables from the versioned SQL schema."""
from pathlib import Path

import pymysql

from config.config import MYSQL_CONFIG

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = PROJECT_ROOT / "mysql" / "schema" / "create_tables.sql"


def initialize_database():
    connection = pymysql.connect(
        host=MYSQL_CONFIG["host"],
        port=MYSQL_CONFIG["port"],
        user=MYSQL_CONFIG["user"],
        password=MYSQL_CONFIG["password"],
        autocommit=True,
        charset="utf8mb4",
    )
    try:
        with connection.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{MYSQL_CONFIG['database']}`")
            cursor.execute(f"USE `{MYSQL_CONFIG['database']}`")
            if not SCHEMA_PATH.is_file():
                raise FileNotFoundError(f"MySQL schema file was not found: {SCHEMA_PATH}")
            sql_script = SCHEMA_PATH.read_text(encoding="utf-8")
            statements = [statement.strip() for statement in sql_script.split(";") if statement.strip()]
            for statement in statements:
                # The schema is a trusted, version-controlled SQL file.
                cursor.execute(statement)
        print(f"Database '{MYSQL_CONFIG['database']}' initialized successfully.")
    finally:
        connection.close()


if __name__ == "__main__":
    initialize_database()
