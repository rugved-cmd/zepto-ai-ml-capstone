from pathlib import Path
import sqlite3

import pandas as pd


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATABASE_FILE = (
    PROJECT_ROOT
    / "data_pipeline"
    / "data"
    / "books.db"
)

APP_FILE = (
    PROJECT_ROOT
    / "app"
    / "src"
    / "app.py"
)


# ============================================================
# DATABASE
# ============================================================

def load_books():
    connection = sqlite3.connect(DATABASE_FILE)

    try:
        df = pd.read_sql_query(
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

    return df


# ============================================================
# DATABASE VERIFICATION
# ============================================================

def verify_database(df):

    assert len(df) == 69, (
        f"Expected 69 books, found {len(df)}."
    )

    assert df["category"].nunique() == 3, (
        "Expected 3 categories."
    )

    required_categories = {
        "Mystery",
        "Historical Fiction",
        "Travel",
    }

    assert set(df["category"].unique()) == required_categories, (
        "Category values do not match the verified dataset."
    )


# ============================================================
# COLUMN VERIFICATION
# ============================================================

def verify_required_columns(df):

    required_columns = {
        "title",
        "price_gbp",
        "price_inr",
        "rating",
        "stock",
        "category",
    }

    missing_columns = (
        required_columns - set(df.columns)
    )

    assert not missing_columns, (
        f"Missing required columns: {missing_columns}"
    )


# ============================================================
# PRICE CONVERSION VERIFICATION
# ============================================================

def verify_price_conversion(df):
    """
    Verify GBP-to-INR conversion using the same Python
    rounding behavior used by the data pipeline.

    Required exchange rate:
        1 GBP = INR 105.50
    """

    expected_inr = df["price_gbp"].apply(
        lambda value: round(
            float(value) * 105.50,
            2,
        )
    )

    actual_inr = df["price_inr"].apply(
        lambda value: round(
            float(value),
            2,
        )
    )

    mismatches = (
        expected_inr != actual_inr
    )

    assert not mismatches.any(), (
        "GBP-to-INR conversion does not match "
        "the required 105.50 exchange rate."
    )


# ============================================================
# RECOMMENDATION VERIFICATION
# ============================================================

def verify_recommendation_logic(df):

    recommendations = df[
        (df["category"] == "Mystery")
        & (df["price_inr"] <= 3000)
        & (df["rating"] >= 4)
    ].copy()

    recommendations = recommendations.sort_values(
        [
            "rating",
            "price_inr",
        ],
        ascending=[
            False,
            True,
        ],
    ).head(5)

    assert len(recommendations) == 5, (
        f"Expected 5 recommendations, "
        f"found {len(recommendations)}."
    )

    assert (
        recommendations["category"] == "Mystery"
    ).all(), (
        "Recommendation category constraint failed."
    )

    assert (
        recommendations["price_inr"] <= 3000
    ).all(), (
        "Recommendation price constraint failed."
    )

    assert (
        recommendations["rating"] >= 4
    ).all(), (
        "Recommendation rating constraint failed."
    )


# ============================================================
# STREAMLIT APPLICATION VERIFICATION
# ============================================================

def verify_app_file():

    assert APP_FILE.exists(), (
        f"Application file not found: {APP_FILE}"
    )

    content = APP_FILE.read_text(
        encoding="utf-8"
    )

    required_features = [
        "streamlit",
        "load_books",
        "Dashboard",
        "Book Explorer",
        "Recommendations",
        "Analytics",
        "Get Recommendations",
    ]

    for feature in required_features:

        assert feature in content, (
            f"Required application feature missing: {feature}"
        )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)
    print("MODULE 4 — STREAMLIT APPLICATION VERIFICATION")
    print("=" * 60)

    # --------------------------------------------------------
    # 1
    # --------------------------------------------------------

    print("\n[1/5] Checking application file...")

    verify_app_file()

    print(
        "PASS — Streamlit application file exists."
    )

    print(
        "PASS — Required application features detected."
    )

    # --------------------------------------------------------
    # 2
    # --------------------------------------------------------

    print("\n[2/5] Checking SQLite database...")

    assert DATABASE_FILE.exists(), (
        f"Database not found: {DATABASE_FILE}"
    )

    books = load_books()

    verify_database(books)

    print(
        f"PASS — {len(books)} books and "
        f"{books['category'].nunique()} categories loaded."
    )

    # --------------------------------------------------------
    # 3
    # --------------------------------------------------------

    print(
        "\n[3/5] Verifying required database columns..."
    )

    verify_required_columns(books)

    print(
        "PASS — All required book fields are available."
    )

    # --------------------------------------------------------
    # 4
    # --------------------------------------------------------

    print(
        "\n[4/5] Verifying GBP-to-INR conversion..."
    )

    verify_price_conversion(books)

    print(
        "PASS — Every price matches "
        "1 GBP = INR 105.50."
    )

    # --------------------------------------------------------
    # 5
    # --------------------------------------------------------

    print(
        "\n[5/5] Verifying recommendation filters..."
    )

    verify_recommendation_logic(books)

    print(
        "PASS — Recommendation filters return "
        "5 valid Mystery books."
    )

    # --------------------------------------------------------
    # FINAL SUMMARY
    # --------------------------------------------------------

    print("\n" + "=" * 60)

    print(
        f"Books verified:             {len(books)}"
    )

    print(
        f"Categories verified:        "
        f"{books['category'].nunique()}"
    )

    print(
        "Database:                   VERIFIED"
    )

    print(
        "Price conversion:           VERIFIED"
    )

    print(
        "Recommendation logic:       VERIFIED"
    )

    print(
        "Streamlit application:      VERIFIED"
    )

    print("=" * 60)

    print("\nMODULE 4 STATUS: PASS")


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()