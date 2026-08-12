from pathlib import Path
import pandas as pd


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

OUTPUT_DIR = (
    PROJECT_ROOT
    / "analytics"
    / "outputs"
)


# ============================================================
# REQUIRED OUTPUT FILES
# ============================================================

REQUIRED_FILES = [
    "category_performance.csv",
    "rating_analysis.csv",
    "price_analysis.csv",
    "most_expensive_books.csv",
    "highest_rated_books.csv",
    "affordable_books.csv",
    "business_insights.txt",
]


# ============================================================
# HELPERS
# ============================================================

def check_required_files():
    """Verify all Module 2 output files exist."""

    missing_files = []

    for filename in REQUIRED_FILES:

        file_path = OUTPUT_DIR / filename

        if not file_path.exists():
            missing_files.append(filename)

    assert not missing_files, (
        "Missing analytics output files: "
        + ", ".join(missing_files)
    )


def load_csv(filename):
    """Load an analytics CSV file."""

    file_path = OUTPUT_DIR / filename

    assert file_path.exists(), (
        f"Missing file: {file_path}"
    )

    df = pd.read_csv(
        file_path,
        encoding="utf-8"
    )

    assert not df.empty, (
        f"{filename} is empty."
    )

    return df


# ============================================================
# CATEGORY VALIDATION
# ============================================================

def verify_category_performance():
    """Verify category performance output."""

    df = load_csv(
        "category_performance.csv"
    )

    required_columns = {
        "category",
        "book_count",
        "average_price_inr",
        "average_rating",
        "minimum_price_inr",
        "maximum_price_inr",
    }

    assert required_columns.issubset(
        df.columns
    ), (
        "category_performance.csv "
        "is missing required columns."
    )

    assert len(df) == 3, (
        "Expected exactly 3 categories."
    )

    assert df["book_count"].sum() == 69, (
        "Category book counts do not total 69."
    )

    assert (
        df["average_price_inr"] > 0
    ).all(), (
        "Category average prices must be positive."
    )

    assert (
        df["average_rating"].between(1, 5)
    ).all(), (
        "Category ratings must be between 1 and 5."
    )

    return df


# ============================================================
# RATING VALIDATION
# ============================================================

def verify_rating_analysis():
    """Verify rating analysis output."""

    df = load_csv(
        "rating_analysis.csv"
    )

    required_columns = {
        "rating",
        "book_count",
        "average_price_inr",
    }

    assert required_columns.issubset(
        df.columns
    ), (
        "rating_analysis.csv "
        "is missing required columns."
    )

    assert df["rating"].between(1, 5).all(), (
        "Ratings must be between 1 and 5."
    )

    assert df["book_count"].sum() == 69, (
        "Rating counts do not total 69."
    )

    assert (
        df["average_price_inr"] > 0
    ).all(), (
        "Average prices must be positive."
    )

    return df


# ============================================================
# PRICE VALIDATION
# ============================================================

def verify_price_analysis():
    """Verify overall price analysis."""

    df = load_csv(
        "price_analysis.csv"
    )

    required_columns = {
        "metric",
        "price_inr",
    }

    assert required_columns.issubset(
        df.columns
    ), (
        "price_analysis.csv "
        "is missing required columns."
    )

    expected_metrics = {
        "Minimum price",
        "Maximum price",
        "Average price",
        "Median price",
    }

    actual_metrics = set(
        df["metric"].tolist()
    )

    assert actual_metrics == expected_metrics, (
        "Price analysis metrics do not match "
        "the expected metrics."
    )

    assert (
        df["price_inr"] > 0
    ).all(), (
        "Price values must be positive."
    )

    return df


# ============================================================
# TOP BOOKS VALIDATION
# ============================================================

def verify_top_book_files():

    expensive = load_csv(
        "most_expensive_books.csv"
    )

    highest_rated = load_csv(
        "highest_rated_books.csv"
    )

    affordable = load_csv(
        "affordable_books.csv"
    )

    expected_columns = {
        "title",
        "category",
        "price_inr",
        "rating",
    }

    assert expected_columns.issubset(
        expensive.columns
    ), (
        "most_expensive_books.csv "
        "is missing required columns."
    )

    assert expected_columns.issubset(
        highest_rated.columns
    ), (
        "highest_rated_books.csv "
        "is missing required columns."
    )

    assert expected_columns.issubset(
        affordable.columns
    ), (
        "affordable_books.csv "
        "is missing required columns."
    )

    assert len(expensive) == 10, (
        "Expected 10 most expensive books."
    )

    assert len(highest_rated) == 10, (
        "Expected 10 highest-rated books."
    )

    assert len(affordable) == 10, (
        "Expected 10 affordable books."
    )

    assert (
        expensive["price_inr"].is_monotonic_decreasing
    ), (
        "Most expensive books are not sorted "
        "from highest to lowest price."
    )

    assert (
        affordable["price_inr"].is_monotonic_increasing
    ), (
        "Affordable books are not sorted "
        "from lowest to highest price."
    )

    assert (
        highest_rated["rating"].is_monotonic_decreasing
    ), (
        "Highest-rated books are not sorted "
        "from highest to lowest rating."
    )


# ============================================================
# BUSINESS INSIGHTS VALIDATION
# ============================================================

def verify_business_insights():

    file_path = (
        OUTPUT_DIR
        / "business_insights.txt"
    )

    assert file_path.exists(), (
        "business_insights.txt does not exist."
    )

    text = file_path.read_text(
        encoding="utf-8"
    )

    assert text.strip(), (
        "business_insights.txt is empty."
    )

    insight_lines = [
        line
        for line in text.splitlines()
        if line.strip().startswith(
            tuple(str(i) for i in range(1, 10))
        )
    ]

    assert len(insight_lines) == 6, (
        "Expected exactly 6 business insights."
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)
    print("MODULE 2 — ANALYTICS OUTPUT VERIFICATION")
    print("=" * 60)

    # --------------------------------------------------------
    # 1. Required files
    # --------------------------------------------------------

    print("\n[1/5] Checking analytics output files...")

    check_required_files()

    print(
        "PASS — All required analytics outputs exist."
    )

    # --------------------------------------------------------
    # 2. Category performance
    # --------------------------------------------------------

    print(
        "\n[2/5] Verifying category performance..."
    )

    category_df = verify_category_performance()

    print(
        "PASS — 3 categories and 69 books verified."
    )

    # --------------------------------------------------------
    # 3. Rating + price analysis
    # --------------------------------------------------------

    print(
        "\n[3/5] Verifying rating and price analysis..."
    )

    rating_df = verify_rating_analysis()
    price_df = verify_price_analysis()

    print(
        "PASS — Rating distribution and price metrics verified."
    )

    # --------------------------------------------------------
    # 4. Top book outputs
    # --------------------------------------------------------

    print(
        "\n[4/5] Verifying ranked book outputs..."
    )

    verify_top_book_files()

    print(
        "PASS — Top 10 expensive, rated, and affordable "
        "books verified."
    )

    # --------------------------------------------------------
    # 5. Business insights
    # --------------------------------------------------------

    print(
        "\n[5/5] Verifying business insights..."
    )

    verify_business_insights()

    print(
        "PASS — 6 business insights verified."
    )

    # --------------------------------------------------------
    # FINAL
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("MODULE 2 ANALYTICS VERIFICATION SUCCESSFUL")
    print("=" * 60)

    print(
        f"Categories verified: {len(category_df)}"
    )

    print(
        f"Books verified through categories: "
        f"{int(category_df['book_count'].sum())}"
    )

    print(
        f"Rating groups verified: {len(rating_df)}"
    )

    print(
        f"Price metrics verified: {len(price_df)}"
    )

    print(
        "Ranked outputs verified: 30 records"
    )

    print(
        "Business insights verified: 6"
    )

    print()
    print("MODULE 2 STATUS: PASS")


if __name__ == "__main__":
    main()