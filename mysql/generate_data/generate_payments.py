"""Create one payment for each order that does not have a payment yet."""
import random

from config.config import get_connection

PAYMENT_METHODS = ["UPI", "Credit Card", "Debit Card", "Net Banking", "Wallet"]


def generate_payments():
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT
                    o.order_id,
                    o.order_date,
                    o.status,
                    SUM(oi.quantity * oi.unit_price) AS order_amount,
                    COUNT(oi.order_item_id) AS item_count
                FROM orders AS o
                LEFT JOIN order_items AS oi ON oi.order_id = o.order_id
                LEFT JOIN payments AS p ON p.order_id = o.order_id
                WHERE p.payment_id IS NULL
                GROUP BY o.order_id, o.order_date, o.status
                ORDER BY o.order_id
            """)
            unpaid_orders = cursor.fetchall()
            if not unpaid_orders:
                print("Every existing order already has a payment; no rows added.")
                return 0

            missing_items = [row[0] for row in unpaid_orders if row[4] == 0]
            if missing_items:
                sample_ids = ", ".join(map(str, missing_items[:10]))
                raise RuntimeError(
                    "Cannot generate payments because some orders have no order items. "
                    f"Generate order items first. Example order IDs: {sample_ids}"
                )

            insert_query = """
                INSERT INTO payments
                    (order_id, payment_method, payment_status, payment_date, amount)
                VALUES (%s, %s, %s, %s, %s)
            """
            batch = []
            for order_id, order_date, order_status, amount, _item_count in unpaid_orders:
                payment_status = "Failed" if order_status == "Cancelled" else "Success"
                batch.append((
                    order_id,
                    random.choice(PAYMENT_METHODS),
                    payment_status,
                    order_date,
                    amount,
                ))

            conn.begin()
            cursor.executemany(insert_query, batch)
            conn.commit()
            print(f"Inserted {len(batch)} payments; one payment per previously unpaid order.")
            return len(batch)
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    generate_payments()
