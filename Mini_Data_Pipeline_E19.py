import csv
import json
import argparse

def read_sales(file_path):
    required = {"date", "product", "quantity", "price"}

    with open(file_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        if reader.fieldnames is None:
            raise ValueError("CSV file has no header row.")

        missing = required - set(reader.fieldnames)
        if missing:
            missing_str = ", ".join(sorted(missing))
            raise ValueError(f"CSV missing required columns: {missing_str}")

        return list(reader)


def transform_sales(data):
    transformed = []

    for row in data:
        quantity = int(row["quantity"])
        price = float(row["price"])

        transformed.append({
            "date": row["date"],
            "product": row["product"],
            "quantity": quantity,
            "price": price,
            "total": quantity * price
        })

    return transformed


def summarize_by_product(data):
    summary = {}

    for row in data:
        product = row["product"]
        quantity = row["quantity"]
        total = row["total"]

        if product not in summary:
            summary[product] = {"quantity": 0, "revenue": 0.0}

        summary[product]["quantity"] += quantity
        summary[product]["revenue"] += total

    return summary


def write_report(summary, output_file):
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=4)


import sys


def main():
    parser = argparse.ArgumentParser(description="Generate sales report from a CSV file.")
    parser.add_argument("--input", default="sales.csv", help="Path to input CSV file")
    parser.add_argument("--output", default="report.json", help="Path to output JSON report")

    args = parser.parse_args()

    try:
        data = read_sales(args.input)
        data = transform_sales(data)
        summary = summarize_by_product(data)
        write_report(summary, args.output)

        print(f"Report written to {args.output}")

    except FileNotFoundError:
        print(f"Error: Input file '{args.input}' not found.")
        sys.exit(1)
    
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(2)


if __name__ == "__main__":
    main()
