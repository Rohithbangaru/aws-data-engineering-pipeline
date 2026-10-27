"""Generate products until the configured target count is reached."""
import random

from faker import Faker

from config.config import RECORDS, get_connection

fake = Faker("en_IN")

CATEGORIES = {
    "Electronics": ["Samsung", "Apple", "Sony", "LG"],
    "Clothing": ["Nike", "Adidas", "Puma", "Levis"],
    "Grocery": ["Nestle", "Amul", "Britannia"],
    "Home": ["IKEA", "Philips"],
    "Books": ["Penguin", "HarperCollins"],
    "Sports": ["Yonex", "Decathlon"],
}


def generate_products(target_count=None):
    target_count = RECORDS["products"] if target_count is None else int(target_count)
    if target_count < 0:
        raise ValueError("target_count must be zero or greater")

    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM products")
            existing_count = cursor.fetchone()[0]
            missing_count = max(target_count - existing_count, 0)
            if missing_count == 0:
                print(f"Products already at target: {existing_count}/{target_count}; no rows added.")
                return 0

            query = """
                INSERT INTO products
                    (product_name, category, brand, price, stock_quantity)
                VALUES (%s, %s, %s, %s, %s)
            """
            products = []
            for _ in range(missing_count):
                category = random.choice(list(CATEGORIES))
                brand = random.choice(CATEGORIES[category])
                products.append((
                    fake.word().capitalize(),
                    category,
                    brand,
                    round(random.uniform(50, 5000), 2),
                    random.randint(20, 1000),
                ))

            conn.begin()
            cursor.executemany(query, products)
            conn.commit()
            print(f"Inserted {len(products)} products; total is now {existing_count + len(products)}.")
            return len(products)
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    generate_products()
