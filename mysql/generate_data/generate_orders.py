"""Generate orders until the configured target count is reached."""
import random
from datetime import datetime, timedelta

from config.config import RECORDS, get_connection

ORDER_STATUS = ["Delivered", "Shipped", "Cancelled", "Processing"]
STATUS_WEIGHTS = [70, 15, 5, 10]


def random_order_date():
    now = datetime.now()
    start = now - timedelta(days=365)
    return start + timedelta(seconds=random.randint(0, 365 * 24 * 60 * 60))


def generate_orders(target_count=None):
    target_count = RECORDS["orders"] if target_count is None else int(target_count)
    if target_count < 0:
        raise ValueError("target_count must be zero or greater")

    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM orders")
            existing_count = cursor.fetchone()[0]
            missing_count = max(target_count - existing_count, 0)
            if missing_count == 0:
                print(f"Orders already at target: {existing_count}/{target_count}; no rows added.")
                return 0

            cursor.execute("SELECT customer_id FROM customers")
            customer_ids = [row[0] for row in cursor.fetchall()]
            if not customer_ids:
                raise RuntimeError("Cannot generate orders: customers table is empty. Generate customers first.")

            query = "INSERT INTO orders (customer_id, order_date, status) VALUES (%s, %s, %s)"
            orders = [
                (
                    random.choice(customer_ids),
                    random_order_date(),
                    random.choices(ORDER_STATUS, weights=STATUS_WEIGHTS, k=1)[0],
                )
                for _ in range(missing_count)
            ]

            conn.begin()
            cursor.executemany(query, orders)
            conn.commit()
            print(f"Inserted {len(orders)} orders; total is now {existing_count + len(orders)}.")
            return len(orders)
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    generate_orders()
