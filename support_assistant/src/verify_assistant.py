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

OUTPUT_DIR = (
    PROJECT_ROOT
    / "support_assistant"
    / "outputs"
)


# ============================================================
# DATABASE VALIDATION
# ============================================================

def load_books_from_database():
    """Load the verified book catalog from SQLite."""

    assert DATABASE_FILE.exists(), (
        f"Database not found: {DATABASE_FILE}"
    )

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

    assert len(df) == 69, (
        f"Expected 69 books, found {len(df)}."
    )

    assert df["category"].nunique() == 3, (
        "Expected 3 categories."
    )

    return df


# ============================================================
# SEARCH VALIDATION
# ============================================================

def verify_search_results(df):
    """Verify the saved Mystery search results."""

    output_file = (
        OUTPUT_DIR
        / "last_search_results.csv"
    )

    assert output_file.exists(), (
        "last_search_results.csv was not created."
    )

    results = pd.read_csv(
        output_file,
        encoding="utf-8",
    )

    assert len(results) == 32, (
        f"Expected 32 Mystery results, found {len(results)}."
    )

    assert (
        results["category"]
        .str.lower()
        .eq("mystery")
        .all()
    ), (
        "Search results contain non-Mystery books."
    )

    expected_count = (
        df["category"]
        .str.lower()
        .eq("mystery")
        .sum()
    )

    assert len(results) == expected_count, (
        "Search result count does not match the database."
    )

    return results


# ============================================================
# RECOMMENDATION VALIDATION
# ============================================================

def verify_recommendations():
    """Verify the saved recommendation results."""

    output_file = (
        OUTPUT_DIR
        / "recommendations.csv"
    )

    assert output_file.exists(), (
        "recommendations.csv was not created."
    )

    results = pd.read_csv(
        output_file,
        encoding="utf-8",
    )

    assert len(results) == 5, (
        f"Expected 5 recommendations, found {len(results)}."
    )

    assert (
        results["category"]
        .str.lower()
        .eq("mystery")
        .all()
    ), (
        "Recommendations contain non-Mystery books."
    )

    assert (
        results["price_inr"] <= 3000
    ).all(), (
        "Recommendation contains a book above ₹3000."
    )

    assert (
        results["rating"] >= 4
    ).all(), (
        "Recommendation contains a book rated below 4."
    )

    assert (
        results["rating"].is_monotonic_decreasing
    ), (
        "Recommendations are not sorted by rating."
    )

    return results


# ============================================================
# OUTPUT STRUCTURE VALIDATION
# ============================================================

def verify_result_columns(results):
    """Verify the assistant result structure."""

    required_columns = {
        "title",
        "category",
        "price_inr",
        "rating",
        "stock",
    }

    assert required_columns.issubset(
        results.columns
    ), (
        "Assistant output is missing required columns."
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)
    print("MODULE 3 — SUPPORT ASSISTANT VERIFICATION")
    print("=" * 60)

    # --------------------------------------------------------
    # 1. Database
    # --------------------------------------------------------

    print(
        "\n[1/5] Verifying SQLite database connection..."
    )

    df = load_books_from_database()

    print(
        "PASS — 69 books and 3 categories loaded."
    )

    # --------------------------------------------------------
    # 2. Search
    # --------------------------------------------------------

    print(
        "\n[2/5] Verifying book search..."
    )

    search_results = verify_search_results(df)

    verify_result_columns(search_results)

    print(
        "PASS — Mystery search returned 32 valid books."
    )

    # --------------------------------------------------------
    # 3. Recommendations
    # --------------------------------------------------------

    print(
        "\n[3/5] Verifying recommendation engine..."
    )

    recommendation_results = verify_recommendations()

    verify_result_columns(
        recommendation_results
    )

    print(
        "PASS — 5 recommendations satisfy "
        "all requested filters."
    )

    # --------------------------------------------------------
    # 4. Recommendation filters
    # --------------------------------------------------------

    print(
        "\n[4/5] Verifying recommendation constraints..."
    )

    assert (
        recommendation_results["category"]
        .str.lower()
        .eq("mystery")
        .all()
    )

    assert (
        recommendation_results["price_inr"] <= 3000
    ).all()

    assert (
        recommendation_results["rating"] >= 4
    ).all()

    print(
        "PASS — Category, price, and rating constraints verified."
    )

    # --------------------------------------------------------
    # 5. Output files
    # --------------------------------------------------------

    print(
        "\n[5/5] Verifying assistant output files..."
    )

    assert (
        OUTPUT_DIR
        / "last_search_results.csv"
    ).exists()

    assert (
        OUTPUT_DIR
        / "recommendations.csv"
    ).exists()

    print(
        "PASS — Search and recommendation outputs exist."
    )

    # --------------------------------------------------------
    # FINAL
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("MODULE 3 SUPPORT ASSISTANT VERIFICATION SUCCESSFUL")
    print("=" * 60)

    print(
        "Database books verified: 69"
    )

    print(
        "Categories verified: 3"
    )

    print(
        "Search results verified: 32"
    )

    print(
        "Recommendations verified: 5"
    )

    print(
        "Recommendation constraints: VERIFIED"
    )

    print(
        "Output files: VERIFIED"
    )

    print()
    print("MODULE 3 STATUS: PASS")


if __name__ == "__main__":
    main()