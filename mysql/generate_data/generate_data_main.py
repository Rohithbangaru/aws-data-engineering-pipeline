"""Run the synthetic retail data generators in dependency order.

Default mode fills missing rows up to configured target counts and is safe to rerun.
Use --reset only when you intentionally want to delete all generated rows first.
"""
import argparse

from config.config import RECORDS, get_connection
from mysql.generate_data.generate_customers import generate_customers
from mysql.generate_data.generate_products import generate_products
from mysql.generate_data.generate_orders import generate_orders
from mysql.generate_data.generate_order_items import generate_order_items
from mysql.generate_data.generate_payments import generate_payments

RESET_TABLES_IN_ORDER = ("payments", "order_items", "orders", "products", "customers")


def reset_generated_data():
    """Delete all data from project tables and reset their AUTO_INCREMENT values."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            conn.begin()
            for table in RESET_TABLES_IN_ORDER:
                # Table names come from this constant, not user input.
                cursor.execute(f"DELETE FROM {table}")
            conn.commit()
            for table in reversed(RESET_TABLES_IN_ORDER):
                cursor.execute(f"ALTER TABLE {table} AUTO_INCREMENT = 1")
        print("Existing rows deleted and AUTO_INCREMENT values reset.")
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def print_summary():
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            for table in ("customers", "products", "orders", "order_items", "payments"):
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"{table:12} {count:>8,}")
    finally:
        conn.close()


def main():
    # parser = argparse.ArgumentParser(description="Generate synthetic retail data in local MySQL.")
    # parser.add_argument(
    #     "--reset",
    #     action="store_true",
    #     help="Delete all rows from the five project tables before generating data.",
    # )
    # parser.add_argument(
    #     "--yes",
    #     action="store_true",
    #     help="Skip the confirmation prompt; only valid together with --reset.",
    # )
    # args = parser.parse_args()

    # if args.yes and not args.reset:
    #     parser.error("--yes can only be used together with --reset")

    # if args.reset:
    #     if not args.yes:
    #         confirmation = input(
    #             "WARNING: this deletes all rows in customers, products, orders, order_items, and payments. "
    #             "Type RESET to continue: "
    #         )
    #         if confirmation.strip() != "RESET":
    #             print("Reset cancelled; no data was deleted.")
    #             return
    #     reset_generated_data()

    print("Generating customers...")
    generate_customers(RECORDS["customers"])

    print("Generating products...")
    generate_products(RECORDS["products"])

    print("Generating orders...")
    generate_orders(RECORDS["orders"])

    print("Generating order items...")
    generate_order_items()

    print("Generating payments...")
    generate_payments()

    print("\nFinal record counts:")
    print_summary()
    print("\nData generation completed.")


if __name__ == "__main__":
    main()
