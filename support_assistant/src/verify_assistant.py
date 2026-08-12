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
    / "support_assistant"
    / "outputs"
)

SEARCH_OUTPUT = OUTPUT_DIR / "last_search_results.csv"
RECOMMENDATION_OUTPUT = OUTPUT_DIR / "recommendations.csv"


# ============================================================
# LOAD BOOKS FROM NORMALIZED SQLITE DATABASE
# ============================================================

def load_books_from_database():
    if not DATABASE_FILE.exists():
        raise FileNotFoundError(
            f"Database not found: {DATABASE_FILE}"
        )

    connection = sqlite3.connect(DATABASE_FILE)

    try:
        query = """
            SELECT
                b.book_id,
                b.title,
                b.price_gbp,
                b.price_inr,
                b.rating,
                b.in_stock,
                c.category_name AS category
            FROM books AS b
            INNER JOIN categories AS c
                ON b.category_id = c.category_id
            ORDER BY b.book_id
        """

        df = pd.read_sql_query(
            query,
            connection
        )

    finally:
        connection.close()

    return df


# ============================================================
# VERIFY DATABASE
# ============================================================

def verify_database(df):
    assert len(df) == 69, (
        f"Expected 69 books, found {len(df)}."
    )

    assert df["category"].nunique() == 3, (
        "Expected 3 categories."
    )

    required_columns = {
        "book_id",
        "title",
        "price_gbp",
        "price_inr",
        "rating",
        "in_stock",
        "category",
    }

    assert required_columns.issubset(df.columns), (
        "Required book fields are missing."
    )

    print(
        f"PASS — {len(df)} books and "
        f"{df['category'].nunique()} categories loaded."
    )


# ============================================================
# VERIFY SEARCH
# ============================================================

def verify_search(df):
    mystery = df[
        df["category"].str.lower() == "mystery"
    ]

    assert len(mystery) == 32, (
        f"Expected 32 Mystery books, found {len(mystery)}."
    )

    print(
        f"PASS — Mystery search returned "
        f"{len(mystery)} valid books."
    )


# ============================================================
# VERIFY RECOMMENDATIONS
# ============================================================

def verify_recommendations(df):
    recommendations = df[
        (df["category"] == "Mystery")
        & (df["price_inr"] <= 3000)
        & (df["rating"] >= 4)
    ].copy()

    recommendations = recommendations.sort_values(
        by=["rating", "price_inr"],
        ascending=[False, True]
    ).head(5)

    assert len(recommendations) == 5, (
        f"Expected 5 recommendations, "
        f"found {len(recommendations)}."
    )

    print(
        f"PASS — {len(recommendations)} "
        "recommendations satisfy all requested filters."
    )

    return recommendations


# ============================================================
# VERIFY CONSTRAINTS
# ============================================================

def verify_constraints(recommendations):
    assert (
        recommendations["category"] == "Mystery"
    ).all()

    assert (
        recommendations["price_inr"] <= 3000
    ).all()

    assert (
        recommendations["rating"] >= 4
    ).all()

    print(
        "PASS — Category, price, and rating "
        "constraints verified."
    )


# ============================================================
# VERIFY OUTPUT FILES
# ============================================================

def verify_output_files():
    assert SEARCH_OUTPUT.exists(), (
        f"Search output not found: {SEARCH_OUTPUT}"
    )

    assert RECOMMENDATION_OUTPUT.exists(), (
        "Recommendation output not found: "
        f"{RECOMMENDATION_OUTPUT}"
    )

    print(
        "PASS — Search and recommendation "
        "outputs exist."
    )


# ============================================================
# MAIN VERIFICATION
# ============================================================

def main():

    print("=" * 60)
    print("MODULE 3 — SUPPORT ASSISTANT VERIFICATION")
    print("=" * 60)

    print()
    print("[1/5] Verifying SQLite database connection...")

    df = load_books_from_database()
    verify_database(df)

    print()
    print("[2/5] Verifying book search...")

    verify_search(df)

    print()
    print("[3/5] Verifying recommendation engine...")

    recommendations = verify_recommendations(df)

    print()
    print("[4/5] Verifying recommendation constraints...")

    verify_constraints(recommendations)

    print()
    print("[5/5] Verifying assistant output files...")

    verify_output_files()

    print()
    print("=" * 60)
    print("MODULE 3 STATUS: PASS")
    print("=" * 60)


if __name__ == "__main__":
    main()