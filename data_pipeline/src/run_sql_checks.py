from pathlib import Path
import sqlite3

import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATABASE_FILE = (
    PROJECT_ROOT
    / "data_pipeline"
    / "data"
    / "books.db"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data_pipeline"
    / "outputs"
    / "sql_results"
)


# ============================================================
# HELPERS
# ============================================================

def run_query(connection, query):
    """Execute SQL and return the result as a pandas DataFrame."""
    return pd.read_sql_query(query, connection)


def save_query_result(name, query, dataframe):
    """Save SQL query and its output."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    sql_file = OUTPUT_DIR / f"{name}.sql"
    csv_file = OUTPUT_DIR / f"{name}.csv"

    sql_file.write_text(
        query.strip() + "\n",
        encoding="utf-8"
    )

    dataframe.to_csv(
        csv_file,
        index=False,
        encoding="utf-8"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("Starting SQL validation...")
    print()

    # --------------------------------------------------------
    # DATABASE CHECK
    # --------------------------------------------------------

    if not DATABASE_FILE.exists():
        raise FileNotFoundError(
            f"Database not found: {DATABASE_FILE}"
        )

    connection = sqlite3.connect(DATABASE_FILE)

    try:

        # ----------------------------------------------------
        # VERIFY REQUIRED TABLES
        # ----------------------------------------------------

        tables_df = pd.read_sql_query(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
              AND name IN ('books', 'categories')
            ORDER BY name;
            """,
            connection
        )

        required_tables = {"books", "categories"}
        actual_tables = set(tables_df["name"])

        if not required_tables.issubset(actual_tables):
            raise AssertionError(
                "Required normalized tables 'books' and "
                "'categories' were not found."
            )

        # ====================================================
        # 1. SELECT
        # ====================================================

        row_count_query = """
        SELECT COUNT(*) AS row_count
        FROM books;
        """

        row_count_df = run_query(
            connection,
            row_count_query
        )

        print("1. ROW COUNT")
        print(row_count_df.to_string(index=False))
        print()

        save_query_result(
            "01_row_count",
            row_count_query,
            row_count_df
        )

        # ====================================================
        # 2. JOIN + GROUP BY + ORDER BY
        # ====================================================

        category_count_query = """
        SELECT
            c.category_name AS category,
            COUNT(b.book_id) AS book_count
        FROM categories AS c
        JOIN books AS b
            ON c.category_id = b.category_id
        GROUP BY
            c.category_id,
            c.category_name
        ORDER BY
            book_count DESC;
        """

        category_df = run_query(
            connection,
            category_count_query
        )

        print("2. BOOKS BY CATEGORY")
        print(category_df.to_string(index=False))
        print()

        save_query_result(
            "02_books_by_category",
            category_count_query,
            category_df
        )

        # ====================================================
        # 3. WHERE + ORDER BY
        # ====================================================

        high_rating_query = """
        SELECT
            b.title,
            c.category_name AS category,
            b.rating,
            b.price_inr
        FROM books AS b
        JOIN categories AS c
            ON b.category_id = c.category_id
        WHERE b.rating >= 4
        ORDER BY
            b.rating DESC,
            b.price_inr DESC;
        """

        high_rating_df = run_query(
            connection,
            high_rating_query
        )

        print("3. HIGH-RATED BOOKS USING WHERE + ORDER BY")
        print(high_rating_df.head(10).to_string(index=False))
        print()

        save_query_result(
            "03_high_rated_books",
            high_rating_query,
            high_rating_df
        )

        # ====================================================
        # 4. DISTINCT
        # ====================================================

        distinct_category_query = """
        SELECT DISTINCT
            category_name AS category
        FROM categories
        ORDER BY category;
        """

        distinct_category_df = run_query(
            connection,
            distinct_category_query
        )

        print("4. DISTINCT CATEGORIES")
        print(distinct_category_df.to_string(index=False))
        print()

        save_query_result(
            "04_distinct_categories",
            distinct_category_query,
            distinct_category_df
        )

        # ====================================================
        # 5. WHERE + IN + LIMIT
        # ====================================================

        rating_query = """
        SELECT
            b.title,
            c.category_name AS category,
            b.rating,
            b.price_inr
        FROM books AS b
        JOIN categories AS c
            ON b.category_id = c.category_id
        WHERE b.rating IN (4, 5)
        ORDER BY
            b.rating DESC,
            b.price_inr DESC
        LIMIT 10;
        """

        rating_df = run_query(
            connection,
            rating_query
        )

        print("5. HIGH-RATED BOOKS USING WHERE + IN + LIMIT")
        print(rating_df.to_string(index=False))
        print()

        save_query_result(
            "05_high_rated_books_in",
            rating_query,
            rating_df
        )

        # ====================================================
        # 6. BETWEEN + ORDER BY + LIMIT
        # ====================================================

        price_range_query = """
        SELECT
            b.title,
            c.category_name AS category,
            b.price_inr
        FROM books AS b
        JOIN categories AS c
            ON b.category_id = c.category_id
        WHERE b.price_inr BETWEEN 2000 AND 5000
        ORDER BY
            b.price_inr DESC
        LIMIT 10;
        """

        price_range_df = run_query(
            connection,
            price_range_query
        )

        print("6. BOOKS BETWEEN INR 2000 AND INR 5000")
        print(price_range_df.to_string(index=False))
        print()

        save_query_result(
            "06_price_between",
            price_range_query,
            price_range_df
        )

        # ====================================================
        # 7. REQUIRED JOIN QUERY
        # ====================================================

        join_query = """
        SELECT
            b.title,
            c.category_name AS category,
            b.price_gbp,
            b.price_inr,
            b.rating,
            b.in_stock
        FROM books AS b
        JOIN categories AS c
            ON b.category_id = c.category_id
        ORDER BY
            b.rating DESC,
            b.price_inr DESC
        LIMIT 10;
        """

        join_df = run_query(
            connection,
            join_query
        )

        print("7. JOIN QUERY — TOP RATED BOOKS")
        print(join_df.to_string(index=False))
        print()

        save_query_result(
            "07_join_top_rated_books",
            join_query,
            join_df
        )

        # ====================================================
        # 8. PANDAS read_sql + pandas.merge
        # ====================================================

        print("8. PANDAS read_sql VS PANDAS merge")
        print()

        # Read both normalized tables using pd.read_sql()
        books_df = pd.read_sql(
            "SELECT * FROM books;",
            connection
        )

        categories_df = pd.read_sql(
            "SELECT * FROM categories;",
            connection
        )

        # Reproduce the SQL JOIN using pandas.merge()
        pandas_merge_df = pd.merge(
            books_df,
            categories_df,
            on="category_id",
            how="inner"
        )

        pandas_merge_df = pandas_merge_df[
            [
                "title",
                "category_name",
                "price_gbp",
                "price_inr",
                "rating",
                "in_stock"
            ]
        ].rename(
            columns={
                "category_name": "category"
            }
        )

        pandas_merge_df = (
            pandas_merge_df
            .sort_values(
                by=["rating", "price_inr"],
                ascending=[False, False]
            )
            .head(10)
            .reset_index(drop=True)
        )

        sql_comparison_df = (
            join_df
            .reset_index(drop=True)
        )

        # Make column order identical
        pandas_merge_df = pandas_merge_df[
            sql_comparison_df.columns
        ]

        # Normalize numeric values before comparison
        for column in ["price_gbp", "price_inr"]:
            sql_comparison_df[column] = (
                sql_comparison_df[column]
                .astype(float)
                .round(2)
            )

            pandas_merge_df[column] = (
                pandas_merge_df[column]
                .astype(float)
                .round(2)
            )

        # Normalize boolean/integer stock representation
        sql_comparison_df["in_stock"] = (
            sql_comparison_df["in_stock"]
            .astype(int)
        )

        pandas_merge_df["in_stock"] = (
            pandas_merge_df["in_stock"]
            .astype(int)
        )

        equivalent = sql_comparison_df.equals(
            pandas_merge_df
        )

        print("SQL JOIN RESULT:")
        print(
            sql_comparison_df
            .to_string(index=False)
        )

        print()
        print("PANDAS MERGE RESULT:")
        print(
            pandas_merge_df
            .to_string(index=False)
        )

        print()
        print(
            "SQL JOIN and pandas.merge() equivalent:",
            equivalent
        )

        if not equivalent:
            raise AssertionError(
                "SQL JOIN result and pandas.merge() "
                "result do not match."
            )

        # Save side-by-side comparison
        comparison_df = pd.concat(
            [
                sql_comparison_df.add_prefix("sql_"),
                pandas_merge_df.add_prefix("pandas_")
            ],
            axis=1
        )

        save_query_result(
            "08_sql_vs_pandas_merge",
            join_query,
            comparison_df
        )

        # ====================================================
        # FINAL VALIDATION
        # ====================================================

        database_rows = int(
            row_count_df.loc[0, "row_count"]
        )

        category_count = len(
            distinct_category_df
        )

        if database_rows < 60:
            raise AssertionError(
                f"Only {database_rows} books found. "
                "At least 60 are required."
            )

        if category_count < 3:
            raise AssertionError(
                f"Only {category_count} categories found. "
                "At least 3 are required."
            )

        print()
        print("=" * 60)
        print("SQL VALIDATION SUCCESSFUL")
        print("=" * 60)

        print(
            f"Verified {database_rows} database rows."
        )

        print(
            f"Verified {category_count} categories."
        )

        print()
        print(
            "SQL clauses demonstrated:"
        )

        print(
            "SELECT / WHERE / ORDER BY / LIMIT / "
            "DISTINCT / IN / BETWEEN / JOIN"
        )

        print()
        print("pd.read_sql(): VERIFIED")
        print("pd.merge(): VERIFIED")
        print("SQL JOIN and pandas.merge(): MATCH")

        print()
        print(
            f"SQL outputs saved to: {OUTPUT_DIR}"
        )

    finally:
        connection.close()


if __name__ == "__main__":
    main()