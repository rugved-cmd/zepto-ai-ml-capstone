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
# DATABASE
# ============================================================

def load_books():
    """Load book data from the verified SQLite database."""

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
                stock,
                category
            FROM books
            """,
            connection,
        )
    finally:
        connection.close()

    if df.empty:
        raise RuntimeError(
            "The database contains no books."
        )

    return df


# ============================================================
# SEARCH
# ============================================================

def search_books(df, query):
    """Search books by title, category, or keywords."""

    query = query.strip().lower()

    if not query:
        return pd.DataFrame()

    title_match = df["title"].str.lower().str.contains(
        query,
        na=False,
        regex=False,
    )

    category_match = df["category"].str.lower().str.contains(
        query,
        na=False,
        regex=False,
    )

    return df[
        title_match | category_match
    ].copy()


# ============================================================
# CATEGORY SEARCH
# ============================================================

def category_books(df, category):
    """Return books belonging to a category."""

    category = category.strip().lower()

    return df[
        df["category"]
        .str.lower()
        .eq(category)
    ].copy()


# ============================================================
# RECOMMENDATIONS
# ============================================================

def recommend_books(
    df,
    category=None,
    max_price=None,
    min_rating=None,
    limit=5,
):
    """
    Recommend books using optional category,
    price, and rating filters.
    """

    result = df.copy()

    if category:
        result = result[
            result["category"]
            .str.lower()
            .eq(category.strip().lower())
        ]

    if max_price is not None:
        result = result[
            result["price_inr"] <= max_price
        ]

    if min_rating is not None:
        result = result[
            result["rating"] >= min_rating
        ]

    result = result.sort_values(
        [
            "rating",
            "price_inr",
        ],
        ascending=[
            False,
            True,
        ],
    )

    return result.head(limit).copy()


# ============================================================
# DISPLAY HELPERS
# ============================================================

def display_books(df):
    """Display book results in a readable format."""

    if df.empty:
        print("\nNo books found.")
        return

    display_columns = [
        "title",
        "category",
        "price_inr",
        "rating",
        "stock",
    ]

    print()
    print(
        df[display_columns]
        .to_string(index=False)
    )


# ============================================================
# SAVE SEARCH
# ============================================================

def save_search_results(df, filename):
    """Save search or recommendation results."""

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_file = OUTPUT_DIR / filename

    df.to_csv(
        output_file,
        index=False,
        encoding="utf-8",
    )

    return output_file


# ============================================================
# COMMAND HANDLERS
# ============================================================

def handle_search(df):
    """Handle book search."""

    query = input(
        "\nEnter book title or category: "
    )

    results = search_books(
        df,
        query,
    )

    print(
        f"\nFound {len(results)} matching book(s)."
    )

    display_books(results)

    if not results.empty:
        output_file = save_search_results(
            results,
            "last_search_results.csv",
        )

        print(
            f"\nResults saved to: {output_file}"
        )


def handle_category(df):
    """Handle category browsing."""

    print("\nAvailable categories:")

    categories = sorted(
        df["category"]
        .dropna()
        .unique()
    )

    for category in categories:
        count = (
            df["category"]
            .eq(category)
            .sum()
        )

        print(
            f"- {category} ({count} books)"
        )

    category = input(
        "\nEnter category: "
    )

    results = category_books(
        df,
        category,
    )

    print(
        f"\nFound {len(results)} book(s)."
    )

    display_books(results)

    if not results.empty:
        output_file = save_search_results(
            results,
            "category_results.csv",
        )

        print(
            f"\nResults saved to: {output_file}"
        )


def handle_recommendations(df):
    """Handle recommendation requests."""

    print("\nRecommendation filters")
    print("Press Enter to skip any filter.")

    category = input(
        "Category: "
    ).strip()

    max_price_input = input(
        "Maximum price in INR: "
    ).strip()

    min_rating_input = input(
        "Minimum rating (1-5): "
    ).strip()

    try:
        max_price = (
            float(max_price_input)
            if max_price_input
            else None
        )
    except ValueError:
        print(
            "\nInvalid maximum price."
        )
        return

    try:
        min_rating = (
            float(min_rating_input)
            if min_rating_input
            else None
        )
    except ValueError:
        print(
            "\nInvalid minimum rating."
        )
        return

    results = recommend_books(
        df,
        category=category or None,
        max_price=max_price,
        min_rating=min_rating,
        limit=5,
    )

    print(
        f"\nRecommended books: {len(results)}"
    )

    display_books(results)

    if not results.empty:
        output_file = save_search_results(
            results,
            "recommendations.csv",
        )

        print(
            f"\nRecommendations saved to: {output_file}"
        )


# ============================================================
# ASSISTANT MENU
# ============================================================

def show_menu():
    """Display the assistant menu."""

    print()
    print("=" * 60)
    print("BOOK SUPPORT ASSISTANT")
    print("=" * 60)

    print("1. Search books")
    print("2. Browse category")
    print("3. Get recommendations")
    print("4. Show dataset summary")
    print("5. Exit")


def show_summary(df):
    """Display a summary of available books."""

    print()
    print("=" * 60)
    print("BOOK CATALOG SUMMARY")
    print("=" * 60)

    print(
        f"Total books: {len(df)}"
    )

    print(
        f"Categories: {df['category'].nunique()}"
    )

    print(
        f"Average price: "
        f"INR {df['price_inr'].mean():.2f}"
    )

    print(
        f"Average rating: "
        f"{df['rating'].mean():.2f}/5"
    )

    print("\nCategories:")

    category_counts = (
        df["category"]
        .value_counts()
    )

    for category, count in category_counts.items():
        print(
            f"- {category}: {count} books"
        )


# ============================================================
# MAIN ASSISTANT
# ============================================================

def run_assistant(df):
    """Run the interactive support assistant."""

    while True:

        show_menu()

        choice = input(
            "\nChoose an option (1-5): "
        ).strip()

        if choice == "1":
            handle_search(df)

        elif choice == "2":
            handle_category(df)

        elif choice == "3":
            handle_recommendations(df)

        elif choice == "4":
            show_summary(df)

        elif choice == "5":
            print(
                "\nThank you for using "
                "the Book Support Assistant."
            )
            break

        else:
            print(
                "\nInvalid option. "
                "Please choose 1-5."
            )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)
    print("MODULE 3 — SUPPORT ASSISTANT")
    print("=" * 60)

    print(
        "\nLoading verified book database..."
    )

    df = load_books()

    print(
        f"PASS — Loaded {len(df)} books "
        f"from {df['category'].nunique()} categories."
    )

    print(
        "\nSupport assistant is ready."
    )

    run_assistant(df)


if __name__ == "__main__":
    main()