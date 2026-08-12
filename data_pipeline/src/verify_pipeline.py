from pathlib import Path
import sqlite3
from decimal import Decimal, ROUND_HALF_EVEN

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data_pipeline" / "data"

RAW_FILE = DATA_DIR / "books_raw.csv"
CLEAN_FILE = DATA_DIR / "books_clean.csv"
DATABASE_FILE = DATA_DIR / "books.db"


REQUIRED_COLUMNS = {
    "title",
    "price_gbp",
    "price_inr",
    "rating",
    "stock",
    "category",
}


def check_file_exists(path):
    """Check that a required file exists."""
    if not path.exists():
        raise AssertionError(
            f"Missing required file: {path}"
        )


def verify_raw_data():
    """Verify the raw scraped dataset."""

    df = pd.read_csv(
        RAW_FILE,
        encoding="utf-8"
    )

    assert len(df) >= 60, (
        f"Raw dataset has only {len(df)} rows."
    )

    assert df["category"].nunique() >= 3, (
        "Raw dataset contains fewer than 3 categories."
    )

    assert REQUIRED_COLUMNS.issubset(df.columns), (
        "Raw dataset is missing required columns."
    )

    assert df["price_gbp"].notna().all(), (
        "Raw dataset contains missing GBP prices."
    )

    assert df["price_inr"].notna().all(), (
        "Raw dataset contains missing INR prices."
    )

    return df


def verify_clean_data():
    """Verify the cleaned dataset."""

    df = pd.read_csv(
        CLEAN_FILE,
        encoding="utf-8"
    )

    assert len(df) >= 60, (
        f"Clean dataset has only {len(df)} rows."
    )

    assert df["category"].nunique() >= 3, (
        "Clean dataset contains fewer than 3 categories."
    )

    assert REQUIRED_COLUMNS.issubset(df.columns), (
        "Clean dataset is missing required columns."
    )

    assert df["title"].notna().all(), (
        "Clean dataset contains missing titles."
    )

    assert df["price_gbp"].notna().all(), (
        "Clean dataset contains missing GBP prices."
    )

    assert df["price_inr"].notna().all(), (
        "Clean dataset contains missing INR prices."
    )

    assert df["rating"].between(1, 5).all(), (
        "Clean dataset contains invalid ratings."
    )

    return df


def verify_database(clean_df):
    """Verify the SQLite database against the cleaned dataset."""

    connection = sqlite3.connect(DATABASE_FILE)

    try:
        database_df = pd.read_sql_query(
            """
            SELECT
                title,
                price_gbp,
                price_inr,
                rating,
                stock,
                category
            FROM books
            """,
            connection,
        )

    finally:
        connection.close()

    assert len(database_df) == len(clean_df), (
        "Database row count does not match clean dataset."
    )

    assert set(database_df.columns) == REQUIRED_COLUMNS, (
        "Database columns do not match expected columns."
    )

    assert database_df["price_gbp"].notna().all(), (
        "Database contains missing GBP prices."
    )

    assert database_df["price_inr"].notna().all(), (
        "Database contains missing INR prices."
    )

    assert database_df["rating"].between(1, 5).all(), (
        "Database contains invalid ratings."
    )

    return database_df


def python_round_price(price_gbp):
    """
    Reproduce the exact rounding behavior used
    by scrape_books.py.
    """

    return round(
        float(price_gbp) * 105.50,
        2
    )


def verify_price_conversion(df):
    """
    Verify GBP-to-INR conversion using the exact
    same calculation used by the scraper.
    """

    for index, row in df.iterrows():

        expected_inr = python_round_price(
            row["price_gbp"]
        )

        actual_inr = round(
            float(row["price_inr"]),
            2
        )

        if expected_inr != actual_inr:

            raise AssertionError(
                "GBP-to-INR conversion mismatch "
                f"at row {index}: "
                f"GBP={row['price_gbp']}, "
                f"expected INR={expected_inr}, "
                f"actual INR={actual_inr}"
            )


def main():

    print("=" * 60)
    print("MODULE 1 — END-TO-END PIPELINE VERIFICATION")
    print("=" * 60)

    # ---------------------------------------------------------
    # 1. Required files
    # ---------------------------------------------------------

    print("\n[1/5] Checking required files...")

    for path in [
        RAW_FILE,
        CLEAN_FILE,
        DATABASE_FILE,
    ]:
        check_file_exists(path)

    print("PASS — All required files exist.")

    # ---------------------------------------------------------
    # 2. Raw dataset
    # ---------------------------------------------------------

    print("\n[2/5] Verifying raw dataset...")

    raw_df = verify_raw_data()

    print(
        f"PASS — {len(raw_df)} raw rows, "
        f"{raw_df['category'].nunique()} categories."
    )

    # ---------------------------------------------------------
    # 3. Clean dataset
    # ---------------------------------------------------------

    print("\n[3/5] Verifying cleaned dataset...")

    clean_df = verify_clean_data()

    print(
        f"PASS — {len(clean_df)} clean rows, "
        f"{clean_df['category'].nunique()} categories."
    )

    # ---------------------------------------------------------
    # 4. Price conversion
    # ---------------------------------------------------------

    print("\n[4/5] Verifying GBP-to-INR conversion...")

    verify_price_conversion(clean_df)

    print(
        "PASS — Every price matches "
        "1 GBP = INR 105.50."
    )

    # ---------------------------------------------------------
    # 5. Database
    # ---------------------------------------------------------

    print("\n[5/5] Verifying SQLite database...")

    database_df = verify_database(clean_df)

    print(
        f"PASS — Database contains "
        f"{len(database_df)} verified rows."
    )

    # ---------------------------------------------------------
    # Category consistency
    # ---------------------------------------------------------

    raw_categories = set(
        raw_df["category"]
        .dropna()
        .unique()
    )

    clean_categories = set(
        clean_df["category"]
        .dropna()
        .unique()
    )

    database_categories = set(
        database_df["category"]
        .dropna()
        .unique()
    )

    assert raw_categories == clean_categories, (
        "Raw and clean category sets do not match."
    )

    assert clean_categories == database_categories, (
        "Clean and database category sets do not match."
    )

    # ---------------------------------------------------------
    # Final result
    # ---------------------------------------------------------

    print()
    print("=" * 60)
    print("MODULE 1 VERIFICATION SUCCESSFUL")
    print("=" * 60)

    print(f"Raw rows:       {len(raw_df)}")
    print(f"Clean rows:     {len(clean_df)}")
    print(f"Database rows:  {len(database_df)}")
    print(f"Categories:     {len(clean_categories)}")
    print("Price conversion: VERIFIED")
    print("Raw → Clean → SQLite: VERIFIED")
    print()
    print("MODULE 1 STATUS: PASS")


if __name__ == "__main__":
    main()