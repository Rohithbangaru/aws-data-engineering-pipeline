
CREATE SCHEMA IF NOT EXISTS retail_dw;

CREATE TABLE IF NOT EXISTS retail_dw.customer_orders (
    order_id BIGINT,
    customer_id BIGINT,
    order_date TIMESTAMP,
    status VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS retail_dw.daily_sales (
    order_day DATE,
    daily_revenue DECIMAL(18,2),
    year INT,
    month INT
);

CREATE TABLE IF NOT EXISTS retail_dw.product_performance (
    product_id BIGINT,
    product_name VARCHAR(255),
    category VARCHAR(100),
    units_sold BIGINT
);

CREATE TABLE IF NOT EXISTS retail_dw.top_customers (
    customer_id BIGINT,
    total_spent DECIMAL(18,2),
    customer_rank INT
);
