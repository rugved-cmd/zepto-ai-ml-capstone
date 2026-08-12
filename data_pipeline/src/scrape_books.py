import csv
import time
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


# ============================================================
# CONFIGURATION
# ============================================================

BASE_URL = "https://books.toscrape.com/"
CATEGORY_INDEX_URL = BASE_URL

BASE_DIR = Path(__file__).resolve().parents[1]
OUTPUT_FILE = BASE_DIR / "data" / "books_raw.csv"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

# Module 1 requires:
# - at least 3 different categories
# - at least 60 books
TARGET_CATEGORIES = {
    "Travel",
    "Mystery",
    "Historical Fiction",
}


# ============================================================
# REQUEST HELPER
# ============================================================

def get_page(url):
    """
    Download a page and return its BeautifulSoup object.

    Raises an exception for HTTP errors instead of silently
    continuing with invalid HTML.
    """
    response = requests.get(
        url,
        headers=HEADERS,
        timeout=20
    )

    response.raise_for_status()

    return BeautifulSoup(
        response.text,
        "html.parser"
    )


# ============================================================
# URL HELPER
# ============================================================

def make_absolute_url(href):
    """
    Convert a relative Books to Scrape URL into an absolute URL.

    urljoin prevents accidental URLs such as:
    /catalogue/catalogue/...
    """
    return urljoin(BASE_URL, href)


# ============================================================
# DISCOVER REQUIRED CATEGORY URLS
# ============================================================

def get_category_urls():
    """
    Find the URLs of the three required categories from the
    website instead of hard-coding their URLs.
    """
    soup = get_page(CATEGORY_INDEX_URL)

    category_urls = {}

    for link in soup.select(
        "div.side_categories ul li ul li a"
    ):
        category_name = link.get_text(strip=True)

        if category_name not in TARGET_CATEGORIES:
            continue

        href = link.get("href")

        if href:
            category_urls[category_name] = make_absolute_url(href)

    missing = sorted(
        TARGET_CATEGORIES - set(category_urls.keys())
    )

    if missing:
        raise RuntimeError(
            f"Could not find required categories: {missing}"
        )

    return category_urls


# ============================================================
# SCRAPE ONE CATEGORY
# ============================================================

def scrape_category(category_name, category_url):
    """
    Scrape every book listed in one category, including all
    pagination pages.
    """
    rows = []

    current_url = category_url
    page_number = 1

    while current_url:
        print(
            f"Scraping {category_name} — page {page_number}"
        )

        soup = get_page(current_url)

        products = soup.select(
            "article.product_pod"
        )

        if not products:
            raise RuntimeError(
                f"No books found on page: {current_url}"
            )

        for product in products:

            # ------------------------------------------------
            # TITLE
            # ------------------------------------------------

            title_tag = product.select_one(
                "h3 a"
            )

            title = ""

            if title_tag:
                title = title_tag.get(
                    "title",
                    ""
                ).strip()

            # ------------------------------------------------
            # PRICE
            # ------------------------------------------------

            price_tag = product.select_one(
                "p.price_color"
            )

            price = ""

            if price_tag:
                price = price_tag.get_text(
                    strip=True
                )

            # ------------------------------------------------
            # STAR RATING
            # ------------------------------------------------

            rating_tag = product.select_one(
                "p.star-rating"
            )

            star_rating = ""

            if rating_tag:
                classes = rating_tag.get(
                    "class",
                    []
                )

                rating_words = {
                    "One",
                    "Two",
                    "Three",
                    "Four",
                    "Five",
                }

                for class_name in classes:
                    if class_name in rating_words:
                        star_rating = class_name
                        break

            # ------------------------------------------------
            # AVAILABILITY
            # ------------------------------------------------

            availability_tag = product.select_one(
                "p.instock.availability"
            )

            availability = ""

            if availability_tag:
                availability = availability_tag.get_text(
                    " ",
                    strip=True
                )

            # ------------------------------------------------
            # STORE RAW FIELDS
            # ------------------------------------------------

            rows.append(
                {
                    "title": title,
                    "price": price,
                    "star_rating": star_rating,
                    "availability": availability,
                    "category": category_name,
                }
            )

        # ----------------------------------------------------
        # FIND NEXT PAGE
        # ----------------------------------------------------

        next_link = soup.select_one(
            "li.next a"
        )

        if next_link:
            next_href = next_link.get("href")

            if not next_href:
                current_url = None
            else:
                current_url = urljoin(
                    current_url,
                    next_href
                )

                page_number += 1

                # Small delay between requests.
                time.sleep(0.2)

        else:
            current_url = None

    return rows


# ============================================================
# VALIDATE RAW DATA
# ============================================================

def validate_raw_data(rows):
    """
    Validate the raw dataset before saving it.
    """

    required_columns = [
        "title",
        "price",
        "star_rating",
        "availability",
        "category",
    ]

    if not rows:
        raise RuntimeError(
            "No books were scraped."
        )

    # Check that every required field exists.
    for row_number, row in enumerate(rows, start=1):

        for column in required_columns:

            if column not in row:
                raise RuntimeError(
                    f"Missing required field '{column}' "
                    f"in row {row_number}."
                )

    categories = {
        row["category"]
        for row in rows
    }

    if len(rows) < 60:
        raise RuntimeError(
            f"Only {len(rows)} books were scraped. "
            "Module 1 requires at least 60 books."
        )

    if len(categories) < 3:
        raise RuntimeError(
            f"Only {len(categories)} categories were scraped. "
            "Module 1 requires at least 3 categories."
        )

    # Check that the important raw fields were actually found.
    empty_titles = sum(
        not row["title"]
        for row in rows
    )

    empty_prices = sum(
        not row["price"]
        for row in rows
    )

    empty_ratings = sum(
        not row["star_rating"]
        for row in rows
    )

    empty_availability = sum(
        not row["availability"]
        for row in rows
    )

    if empty_titles:
        raise RuntimeError(
            f"{empty_titles} rows have missing titles."
        )

    if empty_prices:
        raise RuntimeError(
            f"{empty_prices} rows have missing prices."
        )

    if empty_ratings:
        raise RuntimeError(
            f"{empty_ratings} rows have missing star ratings."
        )

    if empty_availability:
        raise RuntimeError(
            f"{empty_availability} rows have missing availability."
        )

    print()
    print("RAW DATA VALIDATION")
    print("-" * 50)
    print(f"Rows: {len(rows)}")
    print(f"Categories: {len(categories)}")
    print(
        f"Categories found: {sorted(categories)}"
    )


# ============================================================
# SAVE RAW CSV
# ============================================================

def save_csv(rows):
    """
    Save the raw scraped fields exactly as required by Module 1.
    Cleaning/conversion happens in the next pipeline stage.
    """

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    fieldnames = [
        "title",
        "price",
        "star_rating",
        "availability",
        "category",
    ]

    with open(
        OUTPUT_FILE,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(rows)


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)
    print("MODULE 1 — BOOKS TO SCRAPE")
    print("=" * 60)

    print()
    print("Discovering required categories...")

    category_urls = get_category_urls()

    print(
        f"Found {len(category_urls)} required categories."
    )

    all_rows = []

    # Use a fixed order for reproducible output.
    for category_name in sorted(category_urls):

        category_url = category_urls[category_name]

        category_rows = scrape_category(
            category_name,
            category_url
        )

        all_rows.extend(category_rows)

        print(
            f"Collected {len(category_rows)} "
            f"books from {category_name}."
        )

    validate_raw_data(all_rows)

    save_csv(all_rows)

    print()
    print("=" * 60)
    print("SCRAPING SUCCESSFUL")
    print("=" * 60)

    print(
        f"Rows collected: {len(all_rows)}"
    )

    print(
        "Categories collected: "
        f"{len(set(row['category'] for row in all_rows))}"
    )

    print(
        f"Saved to: {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()