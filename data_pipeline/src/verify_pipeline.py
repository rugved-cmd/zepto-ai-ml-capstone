from pathlib import Path
import sqlite3

import numpy as np
import pandas as pd


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data_pipeline" / "data"
OUTPUT_DIR = PROJECT_ROOT / "data_pipeline" / "outputs" / "sql_results"

RAW_FILE = DATA_DIR / "books_raw.csv"
CLEAN_FILE = DATA_DIR / "books_clean.csv"
DATABASE_FILE = DATA_DIR / "books.db"

EXCHANGE_RATE = 105.50


# ============================================================
# REQUIRED COLUMNS
# ============================================================

RAW_COLUMNS = {
    "title",
    "price",
    "star_rating",
    "availability",
    "category",
}

CLEAN_COLUMNS = {
    "title",
    "price_gbp",
    "price_inr",
    "rating",
    "in_stock",
    "category",
}


# ============================================================
# HELPER
# ============================================================

def check_file(path):
    if not path.exists():
        raise FileNotFoundError(f"Required file not found: {path}")


# ============================================================
# 1. VERIFY RAW DATA
# ============================================================

def verify_raw_data():
    check_file(RAW_FILE)

    df = pd.read_csv(RAW_FILE)

    assert RAW_COLUMNS.issubset(df.columns), (
        "Raw dataset is missing required columns. "
        f"Required: {sorted(RAW_COLUMNS)}. "
        f"Found: {list(df.columns)}"
    )

    assert len(df) >= 60, (
        f"Raw dataset contains only {len(df)} rows. "
        "At least 60 are required."
    )

    assert df["category"].nunique() >= 3, (
        "Raw dataset must contain at least 3 categories."
    )

    assert df["title"].notna().all()
    assert df["price"].notna().all()
    assert df["star_rating"].notna().all()
    assert df["availability"].notna().all()
    assert df["category"].notna().all()

    print(
        f"PASS — {len(df)} raw rows, "
        f"{df['category'].nunique()} categories."
    )

    return df


# ============================================================
# 2. VERIFY CLEAN DATA
# ============================================================

def verify_clean_data():
    check_file(CLEAN_FILE)

    df = pd.read_csv(CLEAN_FILE)

    assert CLEAN_COLUMNS.issubset(df.columns), (
        "Cleaned dataset is missing required columns. "
        f"Required: {sorted(CLEAN_COLUMNS)}. "
        f"Found: {list(df.columns)}"
    )

    assert len(df) >= 60
    assert df["category"].nunique() >= 3

    # Numeric types
    assert pd.api.types.is_numeric_dtype(df["price_gbp"])
    assert pd.api.types.is_numeric_dtype(df["price_inr"])
    assert pd.api.types.is_numeric_dtype(df["rating"])

    # Rating must be 1–5
    assert df["rating"].between(1, 5).all(), (
        "Rating contains values outside 1–5."
    )

    # Stock must be boolean-like
    stock_values = set(df["in_stock"].dropna().unique())

    assert stock_values.issubset({True, False, 0, 1}), (
        f"Unexpected in_stock values: {stock_values}"
    )

    assert df["title"].notna().all()
    assert df["price_gbp"].notna().all()
    assert df["price_inr"].notna().all()
    assert df["rating"].notna().all()
    assert df["in_stock"].notna().all()
    assert df["category"].notna().all()

    print(
        f"PASS — {len(df)} clean rows, "
        f"{df['category'].nunique()} categories."
    )

    return df


# ============================================================
# 3. VERIFY GBP → INR CONVERSION
# ============================================================

def verify_price_conversion(df):
    expected = (
        df["price_gbp"].astype(float) * EXCHANGE_RATE
    ).round(2)

    actual = df["price_inr"].astype(float).round(2)

    expected_paise = np.rint(expected.to_numpy() * 100).astype(np.int64)
    actual_paise = np.rint(actual.to_numpy() * 100).astype(np.int64)

    assert np.array_equal(
        expected_paise,
        actual_paise
    ), (
        "GBP-to-INR conversion does not match "
        "the required 105.50 exchange rate."
    )

    print(
        "PASS — Every price matches "
        "1 GBP = INR 105.50."
    )


# ============================================================
# 4. VERIFY SQLITE DATABASE
# ============================================================

def verify_database():
    check_file(DATABASE_FILE)

    connection = sqlite3.connect(DATABASE_FILE)

    try:
        tables = pd.read_sql_query(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            ORDER BY name;
            """,
            connection
        )

        table_names = set(tables["name"])

        assert "categories" in table_names, (
            "categories table is missing."
        )

        assert "books" in table_names, (
            "books table is missing."
        )

        # ----------------------------------------------------
        # Verify categories
        # ----------------------------------------------------

        categories = pd.read_sql_query(
            """
            SELECT
                category_id,
                category_name
            FROM categories
            ORDER BY category_id;
            """,
            connection
        )

        assert len(categories) >= 3

        assert categories["category_name"].is_unique, (
            "category_name must be UNIQUE."
        )

        # ----------------------------------------------------
        # Verify books
        # ----------------------------------------------------

        books = pd.read_sql_query(
            """
            SELECT
                book_id,
                title,
                price_gbp,
                price_inr,
                rating,
                in_stock,
                category_id
            FROM books;
            """,
            connection
        )

        assert len(books) >= 60

        # ----------------------------------------------------
        # Verify PK/FK relationship
        # ----------------------------------------------------

        foreign_key_check = pd.read_sql_query(
            """
            SELECT
                b.book_id,
                b.category_id
            FROM books b
            LEFT JOIN categories c
                ON b.category_id = c.category_id
            WHERE c.category_id IS NULL;
            """,
            connection
        )

        assert foreign_key_check.empty, (
            "Found books with invalid category foreign keys."
        )

        # ----------------------------------------------------
        # Verify price conversion in database
        # ----------------------------------------------------

        expected = (
            books["price_gbp"].astype(float) * EXCHANGE_RATE
        ).round(2)

        actual = books["price_inr"].astype(float).round(2)

        expected_paise = np.rint(
            expected.to_numpy() * 100
        ).astype(np.int64)

        actual_paise = np.rint(
            actual.to_numpy() * 100
        ).astype(np.int64)

        assert np.array_equal(
            expected_paise,
            actual_paise
        ), (
            "Database price conversion does not match "
            "1 GBP = INR 105.50."
        )

        print(
            f"PASS — Database contains {len(books)} "
            f"verified rows."
        )

        print(
            f"PASS — Database contains "
            f"{len(categories)} categories."
        )

        print(
            "PASS — SQLite schema uses "
            "categories → books PRIMARY KEY / FOREIGN KEY."
        )

        return books, categories

    finally:
        connection.close()


# ============================================================
# 5. VERIFY SQL OUTPUTS
# ============================================================

def verify_sql_outputs():
    check_file(DATABASE_FILE)

    connection = sqlite3.connect(DATABASE_FILE)

    try:
        # SELECT + WHERE + ORDER BY + LIMIT
        query_1 = """
        SELECT
            b.title,
            c.category_name AS category,
            b.rating,
            b.price_inr
        FROM books b
        JOIN categories c
            ON b.category_id = c.category_id
        WHERE b.rating >= 4
        ORDER BY b.rating DESC, b.price_inr DESC
        LIMIT 10;
        """

        result_1 = pd.read_sql_query(
            query_1,
            connection
        )

        assert len(result_1) > 0

        # DISTINCT
        query_2 = """
        SELECT DISTINCT category_name AS category
        FROM categories
        ORDER BY category;
        """

        result_2 = pd.read_sql_query(
            query_2,
            connection
        )

        assert len(result_2) >= 3

        # IN
        query_3 = """
        SELECT
            b.title,
            c.category_name AS category,
            b.rating,
            b.price_inr
        FROM books b
        JOIN categories c
            ON b.category_id = c.category_id
        WHERE b.rating IN (4, 5)
        ORDER BY b.rating DESC, b.price_inr DESC
        LIMIT 10;
        """

        result_3 = pd.read_sql_query(
            query_3,
            connection
        )

        assert len(result_3) > 0

        # BETWEEN
        query_4 = """
        SELECT
            b.title,
            c.category_name AS category,
            b.price_inr
        FROM books b
        JOIN categories c
            ON b.category_id = c.category_id
        WHERE b.price_inr BETWEEN 2000 AND 5000
        ORDER BY b.price_inr DESC
        LIMIT 10;
        """

        result_4 = pd.read_sql_query(
            query_4,
            connection
        )

        assert len(result_4) > 0

        # JOIN
        query_5 = """
        SELECT
            b.title,
            c.category_name AS category,
            b.price_gbp,
            b.price_inr,
            b.rating,
            b.in_stock
        FROM books b
        JOIN categories c
            ON b.category_id = c.category_id
        ORDER BY b.rating DESC, b.price_inr DESC
        LIMIT 10;
        """

        result_5 = pd.read_sql_query(
            query_5,
            connection
        )

        assert len(result_5) == 10

        print(
            "PASS — Required SQL clauses and JOIN "
            "are verified."
        )

        return query_5, result_5

    finally:
        connection.close()


# ============================================================
# 6. VERIFY pandas read_sql + merge
# ============================================================

def verify_pandas_merge():
    connection = sqlite3.connect(DATABASE_FILE)

    try:
        sql_join = """
        SELECT
            b.title,
            c.category_name AS category,
            b.price_gbp,
            b.price_inr,
            b.rating,
            b.in_stock
        FROM books b
        JOIN categories c
            ON b.category_id = c.category_id
        ORDER BY b.rating DESC, b.price_inr DESC
        LIMIT 10;
        """

        sql_result = pd.read_sql(
            sql_join,
            connection
        )

        books_df = pd.read_sql(
            """
            SELECT
                book_id,
                title,
                price_gbp,
                price_inr,
                rating,
                in_stock,
                category_id
            FROM books;
            """,
            connection
        )

        categories_df = pd.read_sql(
            """
            SELECT
                category_id,
                category_name AS category
            FROM categories;
            """,
            connection
        )

        merged = pd.merge(
            books_df,
            categories_df,
            on="category_id",
            how="inner"
        )

        merged_result = merged[
            [
                "title",
                "category",
                "price_gbp",
                "price_inr",
                "rating",
                "in_stock",
            ]
        ].sort_values(
            by=["rating", "price_inr"],
            ascending=[False, False]
        ).head(10).reset_index(drop=True)

        sql_result = sql_result.reset_index(drop=True)

        assert sql_result.equals(merged_result), (
            "SQL JOIN result and pandas.merge() "
            "result do not match."
        )

        print(
            "PASS — pd.read_sql() and pd.merge() "
            "produce equivalent JOIN results."
        )

    finally:
        connection.close()


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)
    print("MODULE 1 — END-TO-END PIPELINE VERIFICATION")
    print("=" * 60)

    print()
    print("[1/5] Checking required files...")

    check_file(RAW_FILE)
    check_file(CLEAN_FILE)
    check_file(DATABASE_FILE)

    print("PASS — All required files exist.")

    print()
    print("[2/5] Verifying raw dataset...")

    raw_df = verify_raw_data()

    print()
    print("[3/5] Verifying cleaned dataset...")

    clean_df = verify_clean_data()

    print()
    print("[4/5] Verifying GBP-to-INR conversion...")

    verify_price_conversion(clean_df)

    print()
    print("[5/5] Verifying SQLite database...")

    books, categories = verify_database()

    verify_sql_outputs()

    verify_pandas_merge()

    print()
    print("=" * 60)
    print("MODULE 1 STATUS: PASS")
    print("=" * 60)

    print()
    print(f"Raw rows:              {len(raw_df)}")
    print(f"Clean rows:            {len(clean_df)}")
    print(f"Database rows:         {len(books)}")
    print(f"Categories:            {len(categories)}")
    print("Price conversion:      VERIFIED")
    print("SQLite PK/FK schema:   VERIFIED")
    print("SQL queries:           VERIFIED")
    print("pd.read_sql():         VERIFIED")
    print("pd.merge():            VERIFIED")


if __name__ == "__main__":
    main()