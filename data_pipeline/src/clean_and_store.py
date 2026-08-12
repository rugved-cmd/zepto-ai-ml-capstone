from pathlib import Path
import re
import sqlite3

import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data_pipeline" / "data"

RAW_FILE = DATA_DIR / "books_raw.csv"
CLEAN_FILE = DATA_DIR / "books_clean.csv"
DATABASE_FILE = DATA_DIR / "books.db"

# Required project-defined fixed exchange rate.
GBP_TO_INR = 105.50

RAW_REQUIRED_COLUMNS = [
    "title",
    "price",
    "star_rating",
    "availability",
    "category",
]

RATING_MAP = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5,
}


# ============================================================
# LOAD RAW DATA
# ============================================================

def load_raw_data():
    """Load the raw scraped dataset."""

    if not RAW_FILE.exists():
        raise FileNotFoundError(
            f"Raw dataset not found: {RAW_FILE}"
        )

    df = pd.read_csv(
        RAW_FILE,
        encoding="utf-8-sig"
    )

    missing_columns = [
        column
        for column in RAW_REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Raw dataset is missing required columns: "
            f"{missing_columns}"
        )

    return df


# ============================================================
# CLEAN PRICE
# ============================================================

def parse_price(value):
    """
    Convert a raw GBP price such as '£45.17' into float 45.17.

    Invalid values become NaN and are handled later using
    median imputation.
    """

    if pd.isna(value):
        return float("nan")

    text = str(value).strip()

    # Remove currency symbol and any unexpected non-numeric
    # characters except decimal point.
    text = re.sub(r"[^0-9.]", "", text)

    if not text:
        return float("nan")

    try:
        return float(text)
    except ValueError:
        return float("nan")


# ============================================================
# CLEAN RATING
# ============================================================

def parse_rating(value):
    """
    Convert text star ratings such as 'Three' into integers.
    """

    if pd.isna(value):
        return float("nan")

    text = str(value).strip()

    return RATING_MAP.get(
        text,
        float("nan")
    )


# ============================================================
# CLEAN AVAILABILITY
# ============================================================

def parse_availability(value):
    """
    Convert availability text into a boolean.

    'In stock' -> True
    'Out of stock' -> False

    Unexpected values become missing and are removed because
    there is no safe numeric/boolean median-imputation strategy
    for an unknown stock status.
    """

    if pd.isna(value):
        return None

    text = str(value).strip().lower()

    if "in stock" in text:
        return True

    if "out of stock" in text:
        return False

    return None


# ============================================================
# CLEAN DATA
# ============================================================

def clean_data(df):
    """
    Clean and transform raw scraped data according to the
    Module 1 requirements.
    """

    cleaned = df.copy()

    # --------------------------------------------------------
    # Remove completely empty rows.
    # --------------------------------------------------------

    cleaned = cleaned.dropna(
        how="all"
    )

    # --------------------------------------------------------
    # Clean text columns.
    # --------------------------------------------------------

    for column in [
        "title",
        "star_rating",
        "availability",
        "category",
    ]:
        cleaned[column] = (
            cleaned[column]
            .astype("string")
            .str.strip()
        )

    # --------------------------------------------------------
    # Parse price.
    # --------------------------------------------------------

    cleaned["price_gbp"] = (
        cleaned["price"]
        .apply(parse_price)
    )

    # --------------------------------------------------------
    # Parse star rating.
    # --------------------------------------------------------

    cleaned["rating"] = (
        cleaned["star_rating"]
        .apply(parse_rating)
    )

    # --------------------------------------------------------
    # Parse availability into boolean.
    # --------------------------------------------------------

    cleaned["in_stock"] = (
        cleaned["availability"]
        .apply(parse_availability)
    )

    # --------------------------------------------------------
    # Numeric imputation.
    #
    # Assignment allows median imputation for numeric fields
    # when parsing fails.
    # --------------------------------------------------------

    price_median = cleaned["price_gbp"].median()

    rating_median = cleaned["rating"].median()

    if pd.isna(price_median):
        raise RuntimeError(
            "Unable to calculate price median."
        )

    if pd.isna(rating_median):
        raise RuntimeError(
            "Unable to calculate rating median."
        )

    cleaned["price_gbp"] = (
        cleaned["price_gbp"]
        .fillna(price_median)
    )

    cleaned["rating"] = (
        cleaned["rating"]
        .fillna(rating_median)
    )

    # Rating must remain an integer from 1 to 5.
    cleaned["rating"] = (
        cleaned["rating"]
        .round()
        .astype(int)
    )

    # --------------------------------------------------------
    # Drop rows where non-numeric critical fields cannot be
    # safely recovered.
    # --------------------------------------------------------

    cleaned = cleaned.dropna(
        subset=[
            "title",
            "category",
            "in_stock",
        ]
    )

    # --------------------------------------------------------
    # Validate rating range.
    # --------------------------------------------------------

    cleaned = cleaned[
        cleaned["rating"].between(1, 5)
    ]

    # --------------------------------------------------------
    # Remove duplicate books within a category.
    # --------------------------------------------------------

    cleaned = cleaned.drop_duplicates(
        subset=[
            "title",
            "category",
        ]
    )

    # --------------------------------------------------------
    # Calculate required fixed-rate INR conversion.
    #
    # IMPORTANT:
    # This is NOT a live exchange rate.
    # It is the assignment's fixed baseline.
    # --------------------------------------------------------

    cleaned["price_gbp"] = (
        cleaned["price_gbp"]
        .round(2)
    )

    cleaned["price_inr"] = (
        cleaned["price_gbp"] * GBP_TO_INR
    ).round(2)

    # --------------------------------------------------------
    # Keep only the cleaned fields required downstream.
    # --------------------------------------------------------

    cleaned = cleaned[
        [
            "title",
            "price_gbp",
            "price_inr",
            "rating",
            "in_stock",
            "category",
        ]
    ]

    # --------------------------------------------------------
    # Explicitly enforce proper data types.
    # --------------------------------------------------------

    cleaned["title"] = (
        cleaned["title"]
        .astype(str)
        .str.strip()
    )

    cleaned["category"] = (
        cleaned["category"]
        .astype(str)
        .str.strip()
    )

    cleaned["price_gbp"] = (
        cleaned["price_gbp"]
        .astype(float)
    )

    cleaned["price_inr"] = (
        cleaned["price_inr"]
        .astype(float)
    )

    cleaned["rating"] = (
        cleaned["rating"]
        .astype(int)
    )

    cleaned["in_stock"] = (
        cleaned["in_stock"]
        .astype(bool)
    )

    cleaned = cleaned.reset_index(
        drop=True
    )

    return cleaned


# ============================================================
# SAVE CLEAN CSV
# ============================================================

def save_clean_csv(df):
    """Save cleaned data as CSV."""

    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(
        CLEAN_FILE,
        index=False,
        encoding="utf-8"
    )


# ============================================================
# CREATE NORMALIZED SQLITE DATABASE
# ============================================================

def create_database(df):
    """
    Create a normalized SQLite database containing:

    categories
        category_id PRIMARY KEY
        category_name UNIQUE

    books
        book_id PRIMARY KEY
        title
        price_gbp
        price_inr
        rating
        in_stock
        category_id FOREIGN KEY
    """

    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    if DATABASE_FILE.exists():
        DATABASE_FILE.unlink()

    connection = sqlite3.connect(
        DATABASE_FILE
    )

    try:

        # Enforce foreign-key relationships.
        connection.execute(
            "PRAGMA foreign_keys = ON"
        )

        cursor = connection.cursor()

        # ----------------------------------------------------
        # Categories table
        # ----------------------------------------------------

        cursor.execute(
            """
            CREATE TABLE categories (
                category_id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_name TEXT NOT NULL UNIQUE
            )
            """
        )

        # ----------------------------------------------------
        # Books table
        # ----------------------------------------------------

        cursor.execute(
            """
            CREATE TABLE books (
                book_id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                price_gbp REAL NOT NULL,
                price_inr REAL NOT NULL,
                rating INTEGER NOT NULL,
                in_stock INTEGER NOT NULL,
                category_id INTEGER NOT NULL,
                FOREIGN KEY (category_id)
                    REFERENCES categories(category_id)
            )
            """
        )

        # ----------------------------------------------------
        # Insert categories
        # ----------------------------------------------------

        categories = sorted(
            df["category"].unique()
        )

        cursor.executemany(
            """
            INSERT INTO categories (category_name)
            VALUES (?)
            """,
            [
                (category,)
                for category in categories
            ]
        )

        # ----------------------------------------------------
        # Create category lookup
        # ----------------------------------------------------

        category_rows = cursor.execute(
            """
            SELECT category_id, category_name
            FROM categories
            """
        ).fetchall()

        category_lookup = {
            category_name: category_id
            for category_id, category_name
            in category_rows
        }

        # ----------------------------------------------------
        # Insert books
        # ----------------------------------------------------

        books_to_insert = []

        for _, row in df.iterrows():

            books_to_insert.append(
                (
                    row["title"],
                    float(row["price_gbp"]),
                    float(row["price_inr"]),
                    int(row["rating"]),
                    int(bool(row["in_stock"])),
                    category_lookup[row["category"]],
                )
            )

        cursor.executemany(
            """
            INSERT INTO books (
                title,
                price_gbp,
                price_inr,
                rating,
                in_stock,
                category_id
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            books_to_insert
        )

        connection.commit()

    finally:
        connection.close()


# ============================================================
# VERIFY DATABASE
# ============================================================

def verify_database():
    """
    Verify:
    - two required tables exist
    - category count
    - book count
    - PK/FK relationship
    """

    connection = sqlite3.connect(
        DATABASE_FILE
    )

    try:

        connection.execute(
            "PRAGMA foreign_keys = ON"
        )

        # ----------------------------------------------------
        # Verify tables.
        # ----------------------------------------------------

        tables = pd.read_sql_query(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            AND name IN ('categories', 'books')
            ORDER BY name
            """,
            connection
        )

        expected_tables = {
            "books",
            "categories",
        }

        actual_tables = set(
            tables["name"].tolist()
        )

        if actual_tables != expected_tables:
            raise RuntimeError(
                "SQLite schema does not contain "
                "the required categories and books tables."
            )

        # ----------------------------------------------------
        # Verify row counts.
        # ----------------------------------------------------

        category_count = int(
            pd.read_sql_query(
                """
                SELECT COUNT(*) AS count
                FROM categories
                """,
                connection
            ).loc[0, "count"]
        )

        book_count = int(
            pd.read_sql_query(
                """
                SELECT COUNT(*) AS count
                FROM books
                """,
                connection
            ).loc[0, "count"]
        )

        # ----------------------------------------------------
        # Verify no orphaned category IDs.
        # ----------------------------------------------------

        orphan_count = int(
            pd.read_sql_query(
                """
                SELECT COUNT(*) AS count
                FROM books b
                LEFT JOIN categories c
                    ON b.category_id = c.category_id
                WHERE c.category_id IS NULL
                """,
                connection
            ).loc[0, "count"]
        )

        if orphan_count != 0:
            raise RuntimeError(
                f"Found {orphan_count} books with "
                "invalid category references."
            )

        return (
            category_count,
            book_count
        )

    finally:
        connection.close()


# ============================================================
# MAIN
# ============================================================

def main():

    print(
        "Starting cleaning and storage pipeline..."
    )

    # --------------------------------------------------------
    # Load
    # --------------------------------------------------------

    raw_df = load_raw_data()

    print(
        f"Raw rows loaded: {len(raw_df)}"
    )

    # --------------------------------------------------------
    # Clean and enrich
    # --------------------------------------------------------

    cleaned_df = clean_data(
        raw_df
    )

    if cleaned_df.empty:
        raise RuntimeError(
            "Cleaning produced zero rows."
        )

    # --------------------------------------------------------
    # Save cleaned CSV
    # --------------------------------------------------------

    save_clean_csv(
        cleaned_df
    )

    # --------------------------------------------------------
    # Create normalized SQLite database
    # --------------------------------------------------------

    create_database(
        cleaned_df
    )

    # --------------------------------------------------------
    # Verify database
    # --------------------------------------------------------

    category_count, database_rows = (
        verify_database()
    )

    if database_rows != len(cleaned_df):
        raise RuntimeError(
            "Database row count does not match "
            "cleaned CSV row count."
        )

    # --------------------------------------------------------
    # Final validation
    # --------------------------------------------------------

    expected_price = (
        cleaned_df["price_gbp"] * GBP_TO_INR
    ).round(2)

    if not (
        expected_price
        .eq(cleaned_df["price_inr"].round(2))
    ).all():

        raise RuntimeError(
            "GBP-to-INR conversion validation failed."
        )

    print()
    print(
        "CLEANING AND STORAGE SUCCESSFUL"
    )

    print(
        f"Raw rows: {len(raw_df)}"
    )

    print(
        f"Cleaned rows: {len(cleaned_df)}"
    )

    print(
        f"Cleaned categories: "
        f"{cleaned_df['category'].nunique()}"
    )

    print(
        f"Exchange rate: "
        f"1 GBP = INR {GBP_TO_INR:.2f}"
    )

    print(
        f"Cleaned CSV: {CLEAN_FILE}"
    )

    print(
        f"SQLite database: {DATABASE_FILE}"
    )

    print(
        f"Database rows verified: {database_rows}"
    )

    print(
        f"Database categories verified: "
        f"{category_count}"
    )

    print(
        "SQLite schema: categories → books "
        "(PRIMARY KEY / FOREIGN KEY)"
    )


if __name__ == "__main__":
    main()