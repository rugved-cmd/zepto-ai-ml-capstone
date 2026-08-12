from pathlib import Path
import sqlite3

import pandas as pd
import streamlit as st


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

ANALYTICS_DIR = (
    PROJECT_ROOT
    / "analytics"
    / "outputs"
)


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Book Intelligence Dashboard",
    page_icon="📚",
    layout="wide",
)


# ============================================================
# DATABASE
# ============================================================

@st.cache_data
def load_books():
    """Load verified books from SQLite."""

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

    return df


# ============================================================
# ANALYTICS
# ============================================================

@st.cache_data
def calculate_category_performance(df):
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

    return result


@st.cache_data
def calculate_rating_distribution(df):
    """Calculate rating distribution."""

    return (
        df.groupby("rating")
        .size()
        .reset_index(name="book_count")
        .sort_values("rating")
    )


# ============================================================
# PAGE HEADER
# ============================================================

st.title("📚 Book Intelligence Dashboard")

st.markdown(
    """
    **End-to-end AI/ML Capstone Dashboard**

    Explore the book catalog, analyze business performance,
    search books, and discover recommendations.
    """
)


# ============================================================
# LOAD DATA
# ============================================================

try:
    books = load_books()

except Exception as error:
    st.error(
        f"Unable to load the book database: {error}"
    )
    st.stop()


if books.empty:
    st.error("The database contains no books.")
    st.stop()


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Select a page:",
    [
        "Dashboard",
        "Book Explorer",
        "Recommendations",
        "Analytics",
    ],
)


# ============================================================
# SIDEBAR FILTERS
# ============================================================

st.sidebar.markdown("---")

st.sidebar.subheader("Catalog Filters")

categories = sorted(
    books["category"]
    .dropna()
    .unique()
    .tolist()
)

selected_categories = st.sidebar.multiselect(
    "Categories",
    categories,
    default=categories,
)

rating_filter = st.sidebar.slider(
    "Minimum Rating",
    min_value=1,
    max_value=5,
    value=1,
)

max_price = int(
    books["price_inr"].max()
)

price_filter = st.sidebar.slider(
    "Maximum Price (INR)",
    min_value=0,
    max_value=max_price,
    value=max_price,
    step=100,
)


# ============================================================
# APPLY FILTERS
# ============================================================

filtered_books = books[
    books["category"].isin(
        selected_categories
    )
    & (
        books["rating"] >= rating_filter
    )
    & (
        books["price_inr"] <= price_filter
    )
].copy()


# ============================================================
# DASHBOARD PAGE
# ============================================================

if page == "Dashboard":

    st.header("📊 Dashboard Overview")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total Books",
        len(filtered_books),
    )

    col2.metric(
        "Categories",
        filtered_books["category"].nunique(),
    )

    col3.metric(
        "Average Price",
        f"₹{filtered_books['price_inr'].mean():,.2f}"
        if not filtered_books.empty
        else "₹0.00",
    )

    col4.metric(
        "Average Rating",
        f"{filtered_books['rating'].mean():.2f}/5"
        if not filtered_books.empty
        else "0.00/5",
    )

    st.markdown("---")

    if filtered_books.empty:
        st.warning(
            "No books match the selected filters."
        )
        st.stop()

    st.subheader("Books by Category")

    category_counts = (
        filtered_books["category"]
        .value_counts()
        .rename_axis("category")
        .reset_index(name="book_count")
    )

    st.bar_chart(
        category_counts.set_index("category")
    )

    st.subheader("Rating Distribution")

    rating_counts = (
        filtered_books["rating"]
        .value_counts()
        .sort_index()
    )

    st.bar_chart(rating_counts)

    st.subheader("Catalog Preview")

    st.dataframe(
        filtered_books[
            [
                "title",
                "category",
                "price_inr",
                "rating",
                "stock",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# BOOK EXPLORER
# ============================================================

elif page == "Book Explorer":

    st.header("🔎 Book Explorer")

    search_query = st.text_input(
        "Search by book title or category",
        placeholder="Example: Mystery",
    )

    explorer_df = filtered_books.copy()

    if search_query.strip():

        query = search_query.strip().lower()

        title_match = (
            explorer_df["title"]
            .str.lower()
            .str.contains(
                query,
                na=False,
                regex=False,
            )
        )

        category_match = (
            explorer_df["category"]
            .str.lower()
            .str.contains(
                query,
                na=False,
                regex=False,
            )
        )

        explorer_df = explorer_df[
            title_match | category_match
        ]

    st.write(
        f"**{len(explorer_df)} book(s) found.**"
    )

    st.dataframe(
        explorer_df[
            [
                "title",
                "category",
                "price_inr",
                "rating",
                "stock",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# RECOMMENDATIONS
# ============================================================

elif page == "Recommendations":

    st.header("⭐ Book Recommendations")

    st.markdown(
        "Find books based on category, price, and rating."
    )

    rec_category = st.selectbox(
        "Category",
        ["Any"] + categories,
    )

    rec_max_price = st.number_input(
        "Maximum Price (INR)",
        min_value=0.0,
        max_value=float(
            books["price_inr"].max()
        ),
        value=float(
            books["price_inr"].max()
        ),
        step=100.0,
    )

    rec_min_rating = st.slider(
        "Minimum Rating",
        min_value=1,
        max_value=5,
        value=4,
    )

    recommendation_limit = st.slider(
        "Number of Recommendations",
        min_value=1,
        max_value=10,
        value=5,
    )

    if st.button(
        "Get Recommendations",
        type="primary",
    ):

        recommendations = books.copy()

        if rec_category != "Any":
            recommendations = recommendations[
                recommendations["category"]
                == rec_category
            ]

        recommendations = recommendations[
            recommendations["price_inr"]
            <= rec_max_price
        ]

        recommendations = recommendations[
            recommendations["rating"]
            >= rec_min_rating
        ]

        recommendations = recommendations.sort_values(
            [
                "rating",
                "price_inr",
            ],
            ascending=[
                False,
                True,
            ],
        ).head(
            recommendation_limit
        )

        if recommendations.empty:

            st.warning(
                "No books match those criteria. "
                "Try relaxing the filters."
            )

        else:

            st.success(
                f"Found {len(recommendations)} recommendation(s)."
            )

            st.dataframe(
                recommendations[
                    [
                        "title",
                        "category",
                        "price_inr",
                        "rating",
                        "stock",
                    ]
                ],
                use_container_width=True,
                hide_index=True,
            )


# ============================================================
# ANALYTICS PAGE
# ============================================================

elif page == "Analytics":

    st.header("📈 Business Analytics")

    category_performance = (
        calculate_category_performance(
            books
        )
    )

    rating_distribution = (
        calculate_rating_distribution(
            books
        )
    )

    st.subheader(
        "Category Performance"
    )

    display_category = category_performance.copy()

    display_category[
        "average_price_inr"
    ] = display_category[
        "average_price_inr"
    ].round(2)

    display_category[
        "average_rating"
    ] = display_category[
        "average_rating"
    ].round(2)

    display_category[
        "minimum_price_inr"
    ] = display_category[
        "minimum_price_inr"
    ].round(2)

    display_category[
        "maximum_price_inr"
    ] = display_category[
        "maximum_price_inr"
    ].round(2)

    st.dataframe(
        display_category,
        use_container_width=True,
        hide_index=True,
    )

    st.subheader(
        "Average Price by Category"
    )

    st.bar_chart(
        category_performance.set_index(
            "category"
        )[
            "average_price_inr"
        ]
    )

    st.subheader(
        "Average Rating by Category"
    )

    st.bar_chart(
        category_performance.set_index(
            "category"
        )[
            "average_rating"
        ]
    )

    st.subheader(
        "Rating Distribution"
    )

    st.bar_chart(
        rating_distribution.set_index(
            "rating"
        )[
            "book_count"
        ]
    )

    st.subheader(
        "Business Insights"
    )

    largest_category = (
        category_performance
        .sort_values(
            "book_count",
            ascending=False,
        )
        .iloc[0]
    )

    highest_price_category = (
        category_performance
        .sort_values(
            "average_price_inr",
            ascending=False,
        )
        .iloc[0]
    )

    highest_rating_category = (
        category_performance
        .sort_values(
            "average_rating",
            ascending=False,
        )
        .iloc[0]
    )

    st.info(
        f"""
        **Key Insights**

        • Largest category: **{largest_category['category']}**
        with {int(largest_category['book_count'])} books.

        • Highest average-priced category:
        **{highest_price_category['category']}**
        at ₹{highest_price_category['average_price_inr']:,.2f}.

        • Highest average-rated category:
        **{highest_rating_category['category']}**
        with an average rating of
        {highest_rating_category['average_rating']:.2f}/5.

        • Overall average price:
        **₹{books['price_inr'].mean():,.2f}**

        • Overall average rating:
        **{books['rating'].mean():.2f}/5**
        """
    )


# ============================================================
# FOOTER
# ============================================================

st.sidebar.markdown("---")

st.sidebar.caption(
    "Zepto AI/ML Capstone — Module 4"
)