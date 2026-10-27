"""Extract all MySQL tables into JSON files."""

from config.config import PROJECT_ROOT
from scripts.extract.mysql_extractor import extract_table

TABLES = ["customers", "products", "orders", "order_items", "payments"]

def main():
    raw_root = PROJECT_ROOT / "raw_data"
    for table in TABLES:
        extract_table(table, raw_root / table)
    print("\nAll tables extracted successfully.")

if __name__ == "__main__":
    main()
