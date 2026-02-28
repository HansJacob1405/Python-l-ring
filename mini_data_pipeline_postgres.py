import argparse
import csv
import json
import sys
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Any

from db_sales_pg import get_conn, init_db, insert_sales, summarize_by_product

REQUIRED_COLUMNS = {"date", "product", "quantity", "price"}


def read_sales_csv(file_path: Path) -> list[dict[str, str]]:
    with open(file_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        if reader.fieldnames is None:
            raise ValueError("CSV file has no header row.")

        missing = REQUIRED_COLUMNS - set(reader.fieldnames)
        if missing:
            raise ValueError(f"CSV missing required columns: {', '.join(sorted(missing))}")

        return list(reader)


def transform_sales(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    transformed: list[dict[str, Any]] = []

    for index, row in enumerate(rows, start=1):
        try:
            d = date.fromisoformat(row["date"])
        except ValueError:
            raise ValueError(f"Invalid date in row {index}: date='{row.get('date')}' (expected YYYY-MM-DD)")

        try:
            quantity = int(row["quantity"])
            price = Decimal(row["price"])
        except Exception:
            raise ValueError(
                f"Invalid numeric value in row {index}: "
                f"quantity='{row.get('quantity')}', price='{row.get('price')}'"
            )

        total = price * quantity
        transformed.append(
            {
                "date": d,
                "product": row["product"],
                "quantity": quantity,
                "price": price,
                "total": total,
            }
        )

    return transformed


def write_report_json(summary: dict[str, dict[str, float]], output_file: Path) -> None:
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=4)


def main() -> None:
    parser = argparse.ArgumentParser(description="Mini data pipeline: CSV -> PostgreSQL -> JSON report (idempotent)")
    parser.add_argument("--input", default="sales.csv", help="Path to input CSV file")
    parser.add_argument("--output", default="report.json", help="Path to output JSON report")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    try:
        raw = read_sales_csv(input_path)
        transformed = transform_sales(raw)

        conn = get_conn()
        init_db(conn)

        inserted = insert_sales(conn, transformed)
        ignored = len(transformed) - inserted

        summary = summarize_by_product(conn)
        write_report_json(summary, output_path)

        print(f"Inserted {inserted} rows (ignored {ignored} duplicates). Report written to {output_path}.")

    except FileNotFoundError:
        print(f"Error: Input file '{input_path}' not found.")
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(2)


if __name__ == "__main__":
    main()