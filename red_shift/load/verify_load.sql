
SELECT 'customer_orders' AS table_name, COUNT(*) AS row_count
FROM retail_dw.customer_orders

UNION ALL

SELECT 'daily_sales', COUNT(*)
FROM retail_dw.daily_sales

UNION ALL

SELECT 'product_performance', COUNT(*)
FROM retail_dw.product_performance

UNION ALL

SELECT 'top_customers', COUNT(*)
FROM retail_dw.top_customers;
