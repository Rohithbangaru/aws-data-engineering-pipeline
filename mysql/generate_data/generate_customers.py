from uuid import uuid4

from faker import Faker

from config.config import RECORDS, get_connection

fake = Faker("en_IN")


def generate_customers(target_count=None):
    target_count = RECORDS["customers"] if target_count is None else int(target_count)
    if target_count < 0:
        raise ValueError("target_count must be zero or greater")

    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM customers")
            existing_count = cursor.fetchone()[0]
            missing_count = max(target_count - existing_count, 0)
            if missing_count == 0:
                print(f"Customers already at target: {existing_count}/{target_count}; no rows added.")
                return 0

            query = """
                INSERT INTO customers
                    (first_name, last_name, email, phone, city, state, country, signup_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            customers = []
            for _ in range(missing_count):
                # The UUID suffix avoids collisions with emails from previous runs.
                email = f"{fake.user_name()}.{uuid4().hex[:12]}@example.com"
                customers.append((
                    fake.first_name(),
                    fake.last_name(),
                    email,
                    fake.phone_number()[:20],
                    fake.city(),
                    fake.state(),
                    "India",
                    fake.date_between(start_date="-3y", end_date="today"),
                ))

            conn.begin()
            cursor.executemany(query, customers)
            conn.commit()
            print(f"Inserted {len(customers)} customers; total is now {existing_count + len(customers)}.")
            return len(customers)
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    generate_customers()
