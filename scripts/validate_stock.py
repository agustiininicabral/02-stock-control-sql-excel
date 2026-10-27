"""Validate stock movement CSVs and summarize current stock balances."""

import argparse
import csv
import json
from collections import defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRODUCT_COLUMNS = {"product_id", "sku", "product_name", "category", "unit_cost", "unit_price"}
MOVEMENT_COLUMNS = {"movement_id", "movement_date", "product_id", "warehouse", "movement_type", "quantity"}


def _read(path, required):
    if not path.is_file():
        return [], [f"Missing file: {path.name}"]
    with path.open(newline="", encoding="utf-8-sig") as stream:
        reader = csv.DictReader(stream)
        missing = required - set(reader.fieldnames or [])
        if missing:
            return [], [f"{path.name} missing columns: {', '.join(sorted(missing))}"]
        return list(reader), []


def validate_stock(data_dir):
    folder = Path(data_dir)
    products, errors = _read(folder / "products.csv", PRODUCT_COLUMNS)
    movements, movement_errors = _read(folder / "movements.csv", MOVEMENT_COLUMNS)
    errors.extend(movement_errors)
    if not products:
        errors.append("products.csv has no data rows")
    if not movements:
        errors.append("movements.csv has no data rows")

    product_ids = [row.get("product_id", "").strip() for row in products]
    movement_ids = [row.get("movement_id", "").strip() for row in movements]
    if len(product_ids) != len(set(product_ids)) or any(not value for value in product_ids):
        errors.append("product_id values must be non-empty and unique")
    if len(movement_ids) != len(set(movement_ids)) or any(not value for value in movement_ids):
        errors.append("movement_id values must be non-empty and unique")
    known_products = set(product_ids)

    for row in products:
        try:
            cost, price = float(row["unit_cost"]), float(row["unit_price"])
            if cost < 0 or price <= 0 or cost > price:
                errors.append(f"product {row.get('product_id', '?')}: invalid cost/price")
        except (KeyError, ValueError):
            errors.append(f"product {row.get('product_id', '?')}: invalid cost/price")

    balances = defaultdict(int)
    for row in movements:
        movement_id = row.get("movement_id", "?")
        if row.get("product_id", "") not in known_products:
            errors.append(f"movement {movement_id}: unknown product_id")
        if row.get("movement_type", "") not in {"IN", "OUT"}:
            errors.append(f"movement {movement_id}: movement_type must be IN or OUT")
        try:
            date.fromisoformat(row["movement_date"])
            quantity = int(row["quantity"])
            if quantity <= 0:
                errors.append(f"movement {movement_id}: quantity must be positive")
            sign = 1 if row["movement_type"] == "IN" else -1
            balances[(row["product_id"], row["warehouse"])] += sign * quantity
        except (KeyError, ValueError):
            errors.append(f"movement {movement_id}: invalid date or quantity")

    products_by_id = {row["product_id"]: row for row in products}
    stock_rows = []
    for (product_id, warehouse), stock in sorted(balances.items()):
        product = products_by_id.get(product_id, {})
        stock_rows.append({
            "product_id": product_id,
            "product_name": product.get("product_name", ""),
            "category": product.get("category", ""),
            "warehouse": warehouse,
            "stock_units": stock,
        })
    critical = [row for row in stock_rows if row["stock_units"] <= 20]
    negative = [row for row in stock_rows if row["stock_units"] < 0]
    return {
        "status": "PASS" if not errors else "FAIL",
        "row_counts": {"products": len(products), "movements": len(movements)},
        "failure_count": len(errors),
        "failures": errors,
        "stock_by_warehouse": stock_rows,
        "critical_stock": critical,
        "negative_balances": negative,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", default=str(ROOT / "data"))
    parser.add_argument("--out", default=str(ROOT / "reports" / "stock_quality_report.json"))
    args = parser.parse_args()
    report = validate_stock(args.data_dir)
    output = Path(args.out)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(
        f"{report['status']}: {report['row_counts']['movements']} movements; "
        f"{len(report['critical_stock'])} critical balances; "
        f"{len(report['negative_balances'])} negative balances"
    )
    for error in report["failures"][:30]:
        print(f"ERROR: {error}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
