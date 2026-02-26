import sqlite3
from pathlib import Path
from typing import Any

DEFAULT_DB_PATH = Path("sales.db")


def get_conn(db_path: Path = DEFAULT_DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            product TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            total REAL NOT NULL
        );
        """
    )

    # Normal indeks
    conn.execute("CREATE INDEX IF NOT EXISTS idx_sales_product ON sales(product);")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_sales_date ON sales(date);")

    # Idempotency: Unique constraint via unique index
    # Vi bruger date+product+quantity+price som naturlig nøgle for en "salgsrække".
    # (Du kan ændre nøglen senere, hvis du får et rigtigt transaction_id felt.)
    try:
        conn.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS ux_sales_natural_key
            ON sales(date, product, quantity, price);
            """
        )
    except sqlite3.IntegrityError as e:
        # Det sker, hvis der allerede ligger dubletter i tabellen.
        raise ValueError(
            "Cannot create UNIQUE index because the database already contains duplicates. "
            "Either delete sales.db (start fresh), or deduplicate the table first."
        ) from e

    conn.commit()


def insert_sales(conn: sqlite3.Connection, rows: list[dict[str, Any]]) -> int:
    """
    Insert transformed sales rows into DB idempotently.
    Duplicate rows (same date, product, quantity, price) will be ignored.
    Each row must contain: date, product, quantity, price, total
    """
    before = conn.total_changes

    conn.executemany(
        """
        INSERT OR IGNORE INTO sales (date, product, quantity, price, total)
        VALUES (?, ?, ?, ?, ?)
        """,
        [(r["date"], r["product"], r["quantity"], r["price"], r["total"]) for r in rows],
    )
    conn.commit()

    after = conn.total_changes
    return after - before


def summarize_by_product(conn: sqlite3.Connection) -> dict[str, dict[str, float]]:
    cur = conn.execute(
        """
        SELECT
            product,
            SUM(quantity) AS quantity,
            SUM(total) AS revenue
        FROM sales
        GROUP BY product
        ORDER BY product;
        """
    )
    summary: dict[str, dict[str, float]] = {}
    for row in cur.fetchall():
        summary[row["product"]] = {
            "quantity": int(row["quantity"]),
            "revenue": float(row["revenue"]),
        }
    return summary


def list_sales(conn: sqlite3.Connection, limit: int = 10) -> list[dict[str, Any]]:
    cur = conn.execute(
        """
        SELECT date, product, quantity, price, total
        FROM sales
        ORDER BY date, id
        LIMIT ?;
        """,
        (limit,),
    )
    return [dict(r) for r in cur.fetchall()]


def dedupe_sales(conn: sqlite3.Connection) -> int:
    """
    Remove duplicate rows, keeping the lowest id for each natural key.
    Returns how many rows were deleted.
    """
    before = conn.total_changes

    conn.execute(
        """
        DELETE FROM sales
        WHERE id NOT IN (
            SELECT MIN(id)
            FROM sales
            GROUP BY date, product, quantity, price
        );
        """
    )
    conn.commit()

    after = conn.total_changes
    return after - before
