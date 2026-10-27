from glue.utils.spark_session import create_spark_session
from glue.jobs.transformations import *
import os
os.environ["HADOOP_HOME"] = r"C:\hadoop"
os.environ["PATH"] += os.pathsep + r"C:\hadoop\bin"
local_raw_path=f"{os.getcwd()}/raw_data"
local_processed_path=f"{os.getcwd()}/processed_data"

def main():

    spark = create_spark_session()

    # ---------- Read ----------
    customers = read_json_table(spark,local_raw_path, "customers")
    products = read_json_table(spark, local_raw_path, "products")
    orders = read_json_table(spark, local_raw_path, "orders")
    order_items = read_json_table(spark, local_raw_path, "order_items")
    payments = read_json_table(spark, local_raw_path, "payments")

    validate_dataframe(customers, "Customers")

    # ---------- Transform ----------
    customers = clean_customers(customers)

    customer_orders = build_customer_orders(customers,orders)

    order_revenue = build_order_revenue(orders,order_items,payments)

    daily_sales = build_daily_sales(order_revenue)

    product_performance = build_product_performance(products,order_items)

    # top_customers = rank_customers(order_revenue,orders)

    # ---------- Optimize ----------
    customer_orders = customer_orders.repartition(8)
    product_performance = product_performance.coalesce(2)
    # top_customers = top_customers.coalesce(1)

    # ---------- Write ----------
    write_parquet(customer_orders,f"{local_processed_path}/customer_orders")

    write_partitioned_parquet(daily_sales,f"{local_processed_path}/daily_sales",["year", "month"])

    write_parquet(product_performance,f"{local_processed_path}/product_performance")

    # write_parquet(top_customers,f"{local_processed_path}/top_customers")

    spark.stop()


if __name__ == "__main__":
    main()

import sys