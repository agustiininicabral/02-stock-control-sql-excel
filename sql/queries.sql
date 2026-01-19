-- 1) Stock actual por producto y depósito (IN - OUT)
WITH signed AS (
  SELECT product_id,
         warehouse,
         CASE WHEN movement_type='IN' THEN quantity ELSE -quantity END AS qty_signed
  FROM fact_movement
)
SELECT p.product_name, s.warehouse, SUM(s.qty_signed) AS stock_units
FROM signed s
JOIN dim_product p ON p.product_id = s.product_id
GROUP BY 1,2
ORDER BY 3 ASC;

-- 2) Stock crítico (umbral configurable)
WITH stock AS (
  SELECT product_id,
         SUM(CASE WHEN movement_type='IN' THEN quantity ELSE -quantity END) AS stock_units
  FROM fact_movement
  GROUP BY 1
)
SELECT p.product_name, p.category, stock.stock_units
FROM stock
JOIN dim_product p ON p.product_id = stock.product_id
WHERE stock.stock_units <= 20
ORDER BY stock.stock_units ASC;

-- 3) Rotación (salidas) últimos 30 días
SELECT p.product_name,
       SUM(m.quantity) AS units_out_30d
FROM fact_movement m
JOIN dim_product p ON p.product_id = m.product_id
WHERE m.movement_type = 'OUT'
  AND m.movement_date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY 1
ORDER BY units_out_30d DESC
LIMIT 15;