from pathlib import Path
import sqlite3

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data_pipeline" / "data"

DATABASE_FILE = DATA_DIR / "books.db"
CLEAN_FILE = DATA_DIR / "books_clean.csv"


def run_query(connection, query):
    """Execute a SQL query and return the result as a DataFrame."""
    return pd.read_sql_query(query, connection)


def main():
    print("Starting SQL validation...")

    if not DATABASE_FILE.exists():
        raise FileNotFoundError(
            f"Database not found: {DATABASE_FILE}"
        )

    if not CLEAN_FILE.exists():
        raise FileNotFoundError(
            f"Clean CSV not found: {CLEAN_FILE}"
        )

    connection = sqlite3.connect(DATABASE_FILE)

    try:
        # ---------------------------------------------------------
        # 1. Row count
        # ---------------------------------------------------------
        row_count_query = """
        SELECT COUNT(*) AS row_count
        FROM books;
        """

        row_count_df = run_query(
            connection,
            row_count_query
        )

        row_count = int(
            row_count_df.loc[0, "row_count"]
        )

        print()
        print("1. ROW COUNT")
        print(row_count_df.to_string(index=False))

        # ---------------------------------------------------------
        # 2. Category count
        # ---------------------------------------------------------
        category_count_query = """
        SELECT
            category,
            COUNT(*) AS book_count
        FROM books
        GROUP BY category
        ORDER BY book_count DESC;
        """

        category_df = run_query(
            connection,
            category_count_query
        )

        print()
        print("2. BOOKS BY CATEGORY")
        print(category_df.to_string(index=False))

        # ---------------------------------------------------------
        # 3. Average price by category
        # ---------------------------------------------------------
        average_price_query = """
        SELECT
            category,
            ROUND(AVG(price_inr), 2) AS average_price_inr
        FROM books
        GROUP BY category
        ORDER BY average_price_inr DESC;
        """

        average_price_df = run_query(
            connection,
            average_price_query
        )

        print()
        print("3. AVERAGE PRICE BY CATEGORY")
        print(
            average_price_df.to_string(index=False)
        )

        # ---------------------------------------------------------
        # 4. Rating distribution
        # ---------------------------------------------------------
        rating_query = """
        SELECT
            rating,
            COUNT(*) AS book_count
        FROM books
        GROUP BY rating
        ORDER BY rating;
        """

        rating_df = run_query(
            connection,
            rating_query
        )

        print()
        print("4. RATING DISTRIBUTION")
        print(rating_df.to_string(index=False))

        # ---------------------------------------------------------
        # 5. Top 10 most expensive books
        # ---------------------------------------------------------
        expensive_query = """
        SELECT
            title,
            category,
            price_inr
        FROM books
        ORDER BY price_inr DESC
        LIMIT 10;
        """

        expensive_df = run_query(
            connection,
            expensive_query
        )

        print()
        print("5. TOP 10 MOST EXPENSIVE BOOKS")
        print(
            expensive_df.to_string(index=False)
        )

        # ---------------------------------------------------------
        # 6. SQL vs pandas row-count comparison
        # ---------------------------------------------------------
        clean_df = pd.read_csv(
            CLEAN_FILE,
            encoding="utf-8"
        )

        pandas_row_count = len(clean_df)

        print()
        print("6. SQL VS PANDAS ROW COUNT")
        print(
            f"SQL row count:    {row_count}"
        )
        print(
            f"Pandas row count: {pandas_row_count}"
        )

        if row_count != pandas_row_count:
            raise RuntimeError(
                "SQL and pandas row counts do not match."
            )

        # ---------------------------------------------------------
        # Final validation
        # ---------------------------------------------------------
        if row_count < 60:
            raise RuntimeError(
                "SQL validation failed: fewer than 60 rows."
            )

        if len(category_df) < 3:
            raise RuntimeError(
                "SQL validation failed: fewer than 3 categories."
            )

        print()
        print("SQL VALIDATION SUCCESSFUL")
        print(
            f"Verified {row_count} database rows."
        )
        print(
            f"Verified {len(category_df)} categories."
        )
        print(
            "SQL and pandas row counts match."
        )

    finally:
        connection.close()


if __name__ == "__main__":
    main()