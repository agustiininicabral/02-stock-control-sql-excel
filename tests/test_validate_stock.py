from __future__ import annotations

import csv
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from validate_stock import validate_stock  # noqa: E402


class StockValidationTests(unittest.TestCase):
    def test_repository_dataset_passes_and_produces_balances(self) -> None:
        report = validate_stock(ROOT / "data")
        self.assertEqual(report["status"], "PASS", report["failures"][:10])
        self.assertGreater(report["row_counts"]["movements"], 0)
        self.assertGreater(len(report["stock_by_warehouse"]), 0)
        self.assertTrue(all(row["stock_units"] <= 20 for row in report["critical_stock"]))

    def test_duplicate_movement_id_is_detected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            for source in (ROOT / "data").glob("*.csv"):
                shutil.copy(source, folder / source.name)
            path = folder / "movements.csv"
            with path.open(newline="", encoding="utf-8") as stream:
                rows = list(csv.DictReader(stream))
            rows[1]["movement_id"] = rows[0]["movement_id"]
            with path.open("w", newline="", encoding="utf-8") as stream:
                writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
                writer.writeheader()
                writer.writerows(rows)
            report = validate_stock(folder)

        self.assertTrue(any("movement_id values" in error for error in report["failures"]))

    def test_unknown_product_and_invalid_movement_type_are_detected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            for source in (ROOT / "data").glob("*.csv"):
                shutil.copy(source, folder / source.name)
            path = folder / "movements.csv"
            with path.open(newline="", encoding="utf-8") as stream:
                rows = list(csv.DictReader(stream))
            rows[0]["product_id"] = "999999"
            rows[1]["movement_type"] = "TRANSFER"
            with path.open("w", newline="", encoding="utf-8") as stream:
                writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
                writer.writeheader()
                writer.writerows(rows)
            report = validate_stock(folder)

        self.assertTrue(any("unknown product_id" in error for error in report["failures"]))
        self.assertTrue(any("movement_type" in error for error in report["failures"]))


if __name__ == "__main__":
    unittest.main()
