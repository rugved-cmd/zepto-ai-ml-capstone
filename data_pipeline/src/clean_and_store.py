from pathlib import Path
import sqlite3

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data_pipeline" / "data"

RAW_FILE = DATA_DIR / "books_raw.csv"
CLEAN_FILE = DATA_DIR / "books_clean.csv"
DATABASE_FILE = DATA_DIR / "books.db"


REQUIRED_COLUMNS = [
    "title",
    "price_gbp",
    "price_inr",
    "rating",
    "stock",
    "category",
]


def load_raw_data():
    """Load the raw scraped dataset."""
    if not RAW_FILE.exists():
        raise FileNotFoundError(
            f"Raw dataset not found: {RAW_FILE}"
        )

    return pd.read_csv(
        RAW_FILE,
        encoding="utf-8"
    )


def clean_data(df):
    """Clean and standardize the scraped dataset."""

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    cleaned = df.copy()

    # Remove completely empty rows.
    cleaned = cleaned.dropna(how="all")

    # Clean text columns.
    cleaned["title"] = (
        cleaned["title"]
        .astype("string")
        .str.strip()
    )

    cleaned["stock"] = (
        cleaned["stock"]
        .astype("string")
        .str.strip()
    )

    cleaned["category"] = (
        cleaned["category"]
        .astype("string")
        .str.strip()
    )

    # Convert numeric columns explicitly.
    cleaned["price_gbp"] = pd.to_numeric(
        cleaned["price_gbp"],
        errors="coerce"
    )

    cleaned["price_inr"] = pd.to_numeric(
        cleaned["price_inr"],
        errors="coerce"
    )

    cleaned["rating"] = pd.to_numeric(
        cleaned["rating"],
        errors="coerce"
    )

    # Remove rows where critical fields are missing.
    cleaned = cleaned.dropna(
        subset=[
            "title",
            "price_gbp",
            "price_inr",
            "rating",
            "stock",
            "category",
        ]
    )

    # Remove duplicate books.
    cleaned = cleaned.drop_duplicates(
        subset=["title", "category"]
    )

    # Keep only valid rating values.
    cleaned = cleaned[
        cleaned["rating"].between(1, 5)
    ]

    # Round prices to two decimal places.
    cleaned["price_gbp"] = cleaned["price_gbp"].round(2)
    cleaned["price_inr"] = cleaned["price_inr"].round(2)

    # Reset the DataFrame index.
    cleaned = cleaned.reset_index(drop=True)

    return cleaned


def save_clean_csv(df):
    """Save the cleaned dataset as UTF-8 CSV."""
    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(
        CLEAN_FILE,
        index=False,
        encoding="utf-8"
    )


def create_database(df):
    """Create a SQLite database containing the cleaned data."""

    if DATABASE_FILE.exists():
        DATABASE_FILE.unlink()

    connection = sqlite3.connect(DATABASE_FILE)

    try:
        df.to_sql(
            "books",
            connection,
            if_exists="replace",
            index=False
        )

        connection.commit()

    finally:
        connection.close()


def verify_database():
    """Verify that the SQLite database contains the expected data."""

    connection = sqlite3.connect(DATABASE_FILE)

    try:
        result = pd.read_sql_query(
            "SELECT COUNT(*) AS row_count FROM books",
            connection
        )

        row_count = int(
            result.loc[0, "row_count"]
        )

    finally:
        connection.close()

    return row_count


def main():
    print("Starting cleaning and storage pipeline...")

    raw_df = load_raw_data()

    print(
        f"Raw rows loaded: {len(raw_df)}"
    )

    cleaned_df = clean_data(raw_df)

    if cleaned_df.empty:
        raise RuntimeError(
            "Cleaning produced zero rows."
        )

    save_clean_csv(cleaned_df)

    create_database(cleaned_df)

    database_rows = verify_database()

    if database_rows != len(cleaned_df):
        raise RuntimeError(
            "Database row count does not match "
            "cleaned CSV row count."
        )

    print()
    print("CLEANING AND STORAGE SUCCESSFUL")
    print(
        f"Cleaned rows: {len(cleaned_df)}"
    )
    print(
        f"Cleaned categories: "
        f"{cleaned_df['category'].nunique()}"
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


if __name__ == "__main__":
    main()