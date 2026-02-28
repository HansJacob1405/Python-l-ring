import os
from typing import Any

import psycopg


def get_conn() -> psycopg.Connection:
    """
    Reads connection string from env var DATABASE_URL, e.g.
    postgresql://postgres:postgres@localhost:5432/salesdb
    """
    dsn = os.environ.get("DATABASE_URL")
    if not dsn:
        raise ValueError(
            "DATABASE_URL is not set. Example:\n"
            "  set DATABASE_URL=postgresql://postgres:postgres@localhost:5432/salesdb"
        )
    return psycopg.connect(dsn)


def init_db(conn: psycopg.Connection) -> None:
    """
    Creates table + unique constraint for idempotent import.
    Natural key: (date, product, quantity, price)
    """
    with conn.cursor() as cur:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS sales (
                id BIGSERIAL PRIMARY KEY,
                date DATE NOT NULL,
                product TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                price NUMERIC(12,2) NOT NULL,
                total NUMERIC(12,2) NOT NULL,
                CONSTRAINT ux_sales_natural_key UNIQUE (date, product, quantity, price)
            );
            """
        )
        cur.execute("CREATE INDEX IF NOT EXISTS idx_sales_product ON sales(product);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_sales_date ON sales(date);")
    conn.commit()


def insert_sales(conn: psycopg.Connection, rows: list[dict[str, Any]]) -> int:
    """
    Idempotent insert: duplicates ignored via ON CONFLICT DO NOTHING.
    Returns number of inserted rows (not including duplicates).
    """
    sql = """
        INSERT INTO sales (date, product, quantity, price, total)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (date, product, quantity, price) DO NOTHING;
    """
    inserted = 0
    with conn.cursor() as cur:
        for r in rows:
            cur.execute(sql, (r["date"], r["product"], r["quantity"], r["price"], r["total"]))
            # rowcount is 1 if inserted, 0 if conflicted/ignored
            inserted += cur.rowcount
    conn.commit()
    return inserted


def summarize_by_product(conn: psycopg.Connection) -> dict[str, dict[str, float]]:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT product,
                   SUM(quantity) AS quantity,
                   SUM(total) AS revenue
            FROM sales
            GROUP BY product
            ORDER BY product;
            """
        )
        summary: dict[str, dict[str, float]] = {}
        for product, quantity, revenue in cur.fetchall():
            summary[product] = {"quantity": int(quantity), "revenue": float(revenue)}
        return summary