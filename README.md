# Control de Stock Inteligente (SQL + Excel)

## Objetivo
Seguimiento de movimientos (IN/OUT) para calcular stock actual, identificar stock crítico y medir rotación.

## Stack
- SQL (PostgreSQL)
- Excel (tablas + gráfico)
- Dataset sintético incluido

## Cómo ejecutar (rápido)
1) Crear tablas: `sql/schema.sql`
2) Cargar `data/*.csv` a la DB (p.ej. con COPY)
3) Ejecutar consultas: `sql/queries.sql`
4) Abrir `excel/dashboard_stock.xlsx`

## Estructura
```
02-stock-control-sql-excel/
├── data/
├── excel/dashboard_stock.xlsx
└── sql/
```

## Tip
- Cambia el umbral de stock crítico (20) en `sql/queries.sql` según tu negocio.
