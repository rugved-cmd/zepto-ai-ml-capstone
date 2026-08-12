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
    / "analytics"
    / "outputs"
)


# ============================================================
# DATABASE
# ============================================================

def load_books():
    """Load verified book data from SQLite."""

    if not DATABASE_FILE.exists():
        raise FileNotFoundError(
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
                in_stock AS stock,
                c.category_name AS category
            FROM books b
            JOIN categories c ON b.category_id = c.category_id
            """,
            connection,
        )
    finally:
        connection.close()

    if df.empty:
        raise RuntimeError(
            "The books database contains no data."
        )

    return df


# ============================================================
# ANALYTICS
# ============================================================

def category_performance(df):
    """Calculate category-level performance."""

    result = (
        df.groupby("category")
        .agg(
            book_count=("title", "count"),
            average_price_inr=("price_inr", "mean"),
            average_rating=("rating", "mean"),
            minimum_price_inr=("price_inr", "min"),
            maximum_price_inr=("price_inr", "max"),
        )
        .reset_index()
    )

    result["average_price_inr"] = (
        result["average_price_inr"].round(2)
    )

    result["average_rating"] = (
        result["average_rating"].round(2)
    )

    result["minimum_price_inr"] = (
        result["minimum_price_inr"].round(2)
    )

    result["maximum_price_inr"] = (
        result["maximum_price_inr"].round(2)
    )

    return result.sort_values(
        "book_count",
        ascending=False
    )


def rating_analysis(df):
    """Calculate rating distribution."""

    result = (
        df.groupby("rating")
        .agg(
            book_count=("title", "count"),
            average_price_inr=("price_inr", "mean"),
        )
        .reset_index()
    )

    result["average_price_inr"] = (
        result["average_price_inr"].round(2)
    )

    return result.sort_values("rating")


def price_analysis(df):
    """Calculate overall pricing metrics."""

    result = pd.DataFrame(
        {
            "metric": [
                "Minimum price",
                "Maximum price",
                "Average price",
                "Median price",
            ],
            "price_inr": [
                df["price_inr"].min(),
                df["price_inr"].max(),
                df["price_inr"].mean(),
                df["price_inr"].median(),
            ],
        }
    )

    result["price_inr"] = (
        result["price_inr"].round(2)
    )

    return result


def most_expensive_books(df, limit=10):
    """Return the most expensive books."""

    return (
        df[
            [
                "title",
                "category",
                "price_inr",
                "rating",
            ]
        ]
        .sort_values(
            "price_inr",
            ascending=False
        )
        .head(limit)
        .reset_index(drop=True)
    )


def highest_rated_books(df, limit=10):
    """Return the highest-rated books."""

    return (
        df[
            [
                "title",
                "category",
                "rating",
                "price_inr",
            ]
        ]
        .sort_values(
            [
                "rating",
                "price_inr",
            ],
            ascending=[
                False,
                True,
            ],
        )
        .head(limit)
        .reset_index(drop=True)
    )


def affordable_books(df, limit=10):
    """Return the least expensive books."""

    return (
        df[
            [
                "title",
                "category",
                "price_inr",
                "rating",
            ]
        ]
        .sort_values(
            "price_inr",
            ascending=True
        )
        .head(limit)
        .reset_index(drop=True)
    )


# ============================================================
# BUSINESS INSIGHTS
# ============================================================

def generate_insights(
    df,
    category_df,
    rating_df,
):
    """Generate simple data-driven business insights."""

    insights = []

    # Largest category
    largest_category = category_df.iloc[0]

    insights.append(
        "Largest category: "
        f"{largest_category['category']} "
        f"with {int(largest_category['book_count'])} books."
    )

    # Highest average price category
    highest_price_category = (
        category_df
        .sort_values(
            "average_price_inr",
            ascending=False
        )
        .iloc[0]
    )

    insights.append(
        "Highest average-priced category: "
        f"{highest_price_category['category']} "
        f"at INR "
        f"{highest_price_category['average_price_inr']:.2f}."
    )

    # Highest average rating category
    highest_rating_category = (
        category_df
        .sort_values(
            "average_rating",
            ascending=False
        )
        .iloc[0]
    )

    insights.append(
        "Highest average-rated category: "
        f"{highest_rating_category['category']} "
        f"with an average rating of "
        f"{highest_rating_category['average_rating']:.2f}."
    )

    # Overall price
    insights.append(
        "Overall average book price: "
        f"INR {df['price_inr'].mean():.2f}."
    )

    # Most common rating
    rating_counts = (
        df["rating"]
        .value_counts()
        .sort_index()
    )

    most_common_rating = (
        rating_counts.idxmax()
    )

    most_common_rating_count = (
        rating_counts.max()
    )

    insights.append(
        "Most common rating: "
        f"{int(most_common_rating)}/5 "
        f"with {int(most_common_rating_count)} books."
    )

    # High-rated books
    high_rated_count = (
        df["rating"] >= 4
    ).sum()

    insights.append(
        f"Books rated 4/5 or higher: "
        f"{int(high_rated_count)} "
        f"out of {len(df)}."
    )

    return insights


# ============================================================
# SAVE OUTPUTS
# ============================================================

def save_outputs(
    category_df,
    rating_df,
    price_df,
    expensive_df,
    highest_rated_df,
    affordable_df,
    insights,
):
    """Save analytics results."""

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    category_df.to_csv(
        OUTPUT_DIR / "category_performance.csv",
        index=False,
        encoding="utf-8",
    )

    rating_df.to_csv(
        OUTPUT_DIR / "rating_analysis.csv",
        index=False,
        encoding="utf-8",
    )

    price_df.to_csv(
        OUTPUT_DIR / "price_analysis.csv",
        index=False,
        encoding="utf-8",
    )

    expensive_df.to_csv(
        OUTPUT_DIR / "most_expensive_books.csv",
        index=False,
        encoding="utf-8",
    )

    highest_rated_df.to_csv(
        OUTPUT_DIR / "highest_rated_books.csv",
        index=False,
        encoding="utf-8",
    )

    affordable_df.to_csv(
        OUTPUT_DIR / "affordable_books.csv",
        index=False,
        encoding="utf-8",
    )

    insights_file = (
        OUTPUT_DIR / "business_insights.txt"
    )

    with open(
        insights_file,
        "w",
        encoding="utf-8",
    ) as file:

        file.write(
            "MODULE 2 — BUSINESS INSIGHTS\n"
        )

        file.write(
            "=" * 50 + "\n\n"
        )

        for number, insight in enumerate(
            insights,
            start=1
        ):
            file.write(
                f"{number}. {insight}\n"
            )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)
    print("MODULE 2 — ANALYTICS ENGINE")
    print("=" * 60)

    # Load data
    print("\n[1/4] Loading books from SQLite...")

    df = load_books()

    print(
        f"PASS — Loaded {len(df)} books "
        f"from {df['category'].nunique()} categories."
    )

    # Run analytics
    print("\n[2/4] Running analytics...")

    category_df = category_performance(df)
    rating_df = rating_analysis(df)
    price_df = price_analysis(df)
    expensive_df = most_expensive_books(df)
    highest_rated_df = highest_rated_books(df)
    affordable_df = affordable_books(df)

    print("PASS — Analytics calculated.")

    # Generate insights
    print("\n[3/4] Generating business insights...")

    insights = generate_insights(
        df,
        category_df,
        rating_df,
    )

    print(
        f"PASS — Generated {len(insights)} insights."
    )

    # Save
    print("\n[4/4] Saving analytics outputs...")

    save_outputs(
        category_df,
        rating_df,
        price_df,
        expensive_df,
        highest_rated_df,
        affordable_df,
        insights,
    )

    print("PASS — Analytics outputs saved.")

    # Display results
    print()
    print("=" * 60)
    print("CATEGORY PERFORMANCE")
    print("=" * 60)

    print(
        category_df.to_string(index=False)
    )

    print()
    print("=" * 60)
    print("PRICE ANALYSIS")
    print("=" * 60)

    print(
        price_df.to_string(index=False)
    )

    print()
    print("=" * 60)
    print("BUSINESS INSIGHTS")
    print("=" * 60)

    for number, insight in enumerate(
        insights,
        start=1
    ):
        print(
            f"{number}. {insight}"
        )

    print()
    print("=" * 60)
    print("MODULE 2 ANALYTICS SUCCESSFUL")
    print("=" * 60)

    print(
        f"Books analyzed: {len(df)}"
    )

    print(
        f"Categories analyzed: "
        f"{df['category'].nunique()}"
    )

    print(
        f"Outputs saved to: {OUTPUT_DIR}"
    )


if __name__ == "__main__":
    main()


