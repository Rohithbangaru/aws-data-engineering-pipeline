"""Create 1-4 distinct product lines for each order that has no items yet."""
import random

from config.config import get_connection


def generate_order_items():
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT o.order_id
                FROM orders AS o
                LEFT JOIN order_items AS oi ON oi.order_id = o.order_id
                WHERE oi.order_item_id IS NULL
                ORDER BY o.order_id
            """)
            orders_without_items = [row[0] for row in cursor.fetchall()]
            if not orders_without_items:
                print("Every existing order already has order items; no rows added.")
                return 0

            cursor.execute("SELECT product_id, price FROM products ORDER BY product_id")
            products = cursor.fetchall()
            if not products:
                raise RuntimeError("Cannot generate order items: products table is empty. Generate products first.")

            insert_query = """
                INSERT INTO order_items (order_id, product_id, quantity, unit_price)
                VALUES (%s, %s, %s, %s)
            """
            batch = []
            for order_id in orders_without_items:
                item_count = random.randint(1, min(4, len(products)))
                for product_id, price in random.sample(products, item_count):
                    batch.append((order_id, product_id, random.randint(1, 5), price))

            conn.begin()
            cursor.executemany(insert_query, batch)
            conn.commit()
            print(f"Inserted {len(batch)} order items across {len(orders_without_items)} previously unitemized orders.")
            return len(batch)
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    generate_order_items()
