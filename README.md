# Control de Stock — SQL + Excel

Proyecto de portfolio para analizar movimientos de inventario, calcular saldos por producto y depósito, detectar stock crítico y revisar salidas recientes. Los datos son sintéticos.

![Stock validation CI](https://github.com/agustiininicabral/02-stock-control-sql-excel/actions/workflows/ci.yml/badge.svg)

## Dataset

- `data/products.csv`: catálogo de productos con SKU, categoría, costo y precio.
- `data/movements.csv`: movimientos IN/OUT con fecha, producto, depósito y cantidad.
- `excel/dashboard_stock.xlsx`: dashboard de Excel de demostración.
- `sql/schema.sql`: dimensiones, movimientos, restricciones e índices.
- `sql/queries.sql`: saldo por depósito, stock crítico y unidades de salida de los últimos 30 días.

Cada fila de movements.csv representa un movimiento de inventario. El saldo se calcula como entradas menos salidas.

## Validación local

Requiere Python 3.12 o posterior y no necesita dependencias externas:

```powershell
python scripts/validate_stock.py
python -m unittest discover -s tests -v
```

El validador comprueba columnas, IDs únicos, fechas, tipos de movimiento IN/OUT, cantidades positivas y referencias a productos existentes. Genera `reports/stock_quality_report.json` con saldos por producto/depósito, stock crítico (20 unidades o menos) y saldos negativos.

Un saldo negativo se informa como un problema de inventario para investigar, pero no se oculta ni se trata automáticamente como un error estructural: puede indicar movimientos faltantes, errores de carga o una política de stock negativo que debe revisarse.

GitHub Actions ejecuta las pruebas y publica el reporte como artefacto temporal.

## Ejecutar en PostgreSQL

1. Crear una base de datos vacía.
2. Ejecutar `sql/schema.sql`.
3. Importar `data/products.csv` a `dim_product` y `data/movements.csv` a `fact_movement`, respetando los nombres de columna.
4. Ejecutar las consultas de `sql/queries.sql`.

La consulta de rotación usa sintaxis de PostgreSQL (`CURRENT_DATE - INTERVAL '30 days'`). Para otro motor SQL, adaptá la expresión de fechas.

## Interpretación de KPIs

- **Stock actual:** suma de entradas menos salidas por producto y depósito.
- **Stock crítico:** saldo igual o menor al umbral configurado en la consulta.
- **Rotación:** unidades que salieron en los últimos 30 días; es un indicador de movimiento, no una tasa formal de rotación de inventario.

El umbral de 20 unidades es ilustrativo y debe ajustarse según la demanda y el tiempo de reposición del negocio. El dataset no incluye lead time, stock de seguridad ni órdenes de compra.

## Licencia

MIT. Consultá [LICENSE](LICENSE).
