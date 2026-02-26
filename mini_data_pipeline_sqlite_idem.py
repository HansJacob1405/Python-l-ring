import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any

from db_sales_idem import get_conn, init_db, insert_sales, summarize_by_product, dedupe_sales


REQUIRED_COLUMNS = {"date", "product", "quantity", "price"}


def read_sales_csv(file_path: Path) -> list[dict[str, str]]:
    with open(file_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        if reader.fieldnames is None:
            raise ValueError("CSV file has no header row.")

        missing = REQUIRED_COLUMNS - set(reader.fieldnames)
        if missing:
            missing_str = ", ".join(sorted(missing))
            raise ValueError(f"CSV missing required columns: {missing_str}")

        return list(reader)


def transform_sales(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    transformed: list[dict[str, Any]] = []

    for index, row in enumerate(rows, start=1):
        try:
            quantity = int(row["quantity"])
            price = float(row["price"])
        except ValueError:
            raise ValueError(
                f"Invalid numeric value in row {index}: "
                f"quantity='{row.get('quantity')}', price='{row.get('price')}'"
            )

        transformed.append(
            {
                "date": row["date"],
                "product": row["product"],
                "quantity": quantity,
                "price": price,
                "total": quantity * price,
            }
        )

    return transformed


def write_report_json(summary: dict[str, dict[str, float]], output_file: Path) -> None:
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=4)


def main() -> None:
    parser = argparse.ArgumentParser(description="Mini data pipeline: CSV -> SQLite -> JSON report (idempotent)")
    parser.add_argument("--input", default="sales.csv", help="Path to input CSV file")
    parser.add_argument("--output", default="report.json", help="Path to output JSON report")
    parser.add_argument("--db", default="sales.db", help="Path to SQLite database file")
    parser.add_argument(
        "--preview",
        type=int,
        default=0,
        help="Print first N rows from DB after insert (0 = no preview)",
    )
    parser.add_argument(
        "--dedupe",
        action="store_true",
        help="Remove duplicates from DB before creating UNIQUE index (useful if DB already has duplicates).",
    )

    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)
    db_path = Path(args.db)

    try:
        raw = read_sales_csv(input_path)
        transformed = transform_sales(raw)

        conn = get_conn(db_path)

        # Hvis DB allerede har dubletter fra tidligere runs, kan UNIQUE index fejle.
        # --dedupe rydder op først.
        if args.dedupe:
            deleted = dedupe_sales(conn)
            if deleted > 0:
                print(f"Deduped database: removed {deleted} duplicate rows.")

        init_db(conn)

        inserted = insert_sales(conn, transformed)
        summary = summarize_by_product(conn)
        write_report_json(summary, output_path)

        ignored = len(transformed) - inserted
        print(
            f"Inserted {inserted} rows into {db_path} (ignored {ignored} duplicates). "
            f"Report written to {output_path}."
        )

        if args.preview > 0:
            from db_sales import list_sales

            preview_rows = list_sales(conn, limit=args.preview)
            print("Preview rows:")
            for r in preview_rows:
                print(r)

    except FileNotFoundError:
        print(f"Error: Input file '{input_path}' not found.")
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(2)


if __name__ == "__main__":
    main()
