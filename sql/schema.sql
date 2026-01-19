CREATE TABLE IF NOT EXISTS dim_product (
  product_id   INT PRIMARY KEY,
  sku          TEXT NOT NULL UNIQUE,
  product_name TEXT NOT NULL,
  category     TEXT NOT NULL,
  unit_cost    NUMERIC(10,2) NOT NULL,
  unit_price   NUMERIC(10,2) NOT NULL
);

CREATE TABLE IF NOT EXISTS fact_movement (
  movement_id   INT PRIMARY KEY,
  movement_date DATE NOT NULL,
  product_id    INT NOT NULL REFERENCES dim_product(product_id),
  warehouse     TEXT NOT NULL,
  movement_type TEXT NOT NULL CHECK (movement_type IN ('IN','OUT')),
  quantity      INT NOT NULL CHECK (quantity > 0)
);

CREATE INDEX IF NOT EXISTS idx_fact_movement_date ON fact_movement(movement_date);
CREATE INDEX IF NOT EXISTS idx_fact_movement_product ON fact_movement(product_id);