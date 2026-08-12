from pathlib import Path
import re
import time

import pandas as pd
import requests
from bs4 import BeautifulSoup


BASE_URL = "https://books.toscrape.com/"
EXCHANGE_RATE_GBP_TO_INR = 105.50

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data_pipeline" / "data"
OUTPUT_DIR = PROJECT_ROOT / "data_pipeline" / "outputs"

RAW_OUTPUT = DATA_DIR / "books_raw.csv"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def get_soup(url):
    """Download a page and return its BeautifulSoup object."""
    response = requests.get(url, headers=HEADERS, timeout=30)
    response.raise_for_status()

    response.encoding = "utf-8"

    return BeautifulSoup(response.text, "html.parser")


def discover_categories():
    """Discover book categories from the website navigation."""
    soup = get_soup(BASE_URL)

    categories = []

    for link in soup.select("div.side_categories ul li ul li a"):
        name = link.get_text(strip=True)
        href = link.get("href")

        if name and href:
            categories.append(
                {
                    "category": name,
                    "url": BASE_URL + href.replace("../", ""),
                }
            )

    return categories


def scrape_category(category_name, category_url):
    """Scrape all pages belonging to one category."""
    rows = []
    page_url = category_url

    while page_url:
        soup = get_soup(page_url)

        for article in soup.select("article.product_pod"):
            title_element = article.select_one("h3 a")
            price_element = article.select_one("p.price_color")
            rating_element = article.select_one("p.star-rating")
            stock_element = article.select_one("p.instock.availability")

            title = (
                title_element.get("title", "").strip()
                if title_element
                else ""
            )

            price_text = (
                price_element.get_text(strip=True)
                if price_element
                else ""
            )

            rating = ""

            if rating_element:
                classes = rating_element.get("class", [])

                rating_words = {
                    "One": 1,
                    "Two": 2,
                    "Three": 3,
                    "Four": 4,
                    "Five": 5,
                }

                for word, value in rating_words.items():
                    if word in classes:
                        rating = value
                        break

            stock = (
                stock_element.get_text(" ", strip=True)
                if stock_element
                else ""
            )

            # Extract numeric price safely.
            price_match = re.search(
                r"\d+(?:\.\d+)?",
                price_text
            )

            price_gbp = (
                float(price_match.group())
                if price_match
                else None
            )

            price_inr = (
                round(
                    price_gbp * EXCHANGE_RATE_GBP_TO_INR,
                    2
                )
                if price_gbp is not None
                else None
            )

            rows.append(
                {
                    "title": title,
                    "price_gbp": price_gbp,
                    "price_inr": price_inr,
                    "rating": rating,
                    "stock": stock,
                    "category": category_name,
                }
            )

        next_link = soup.select_one("li.next a")

        if next_link and next_link.get("href"):
            next_href = next_link["href"]

            if page_url.endswith("/"):
                page_url = page_url + next_href
            else:
                page_url = (
                    page_url.rsplit("/", 1)[0]
                    + "/"
                    + next_href
                )
        else:
            page_url = None

        time.sleep(0.2)

    return rows


def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("Starting Books to Scrape pipeline...")
    print(
        f"Exchange rate: "
        f"1 GBP = INR {EXCHANGE_RATE_GBP_TO_INR}"
    )

    categories = discover_categories()

    if not categories:
        raise RuntimeError(
            "No categories were discovered."
        )

    print(
        f"Discovered {len(categories)} categories."
    )

    all_rows = []

    for category in categories:
        print(
            f"Scraping category: "
            f"{category['category']}"
        )

        category_rows = scrape_category(
            category["category"],
            category["url"],
        )

        all_rows.extend(category_rows)

        unique_categories = {
            row["category"]
            for row in all_rows
            if row["category"]
        }

        print(
            f"Collected {len(all_rows)} rows "
            f"across {len(unique_categories)} categories."
        )

        if (
            len(all_rows) >= 60
            and len(unique_categories) >= 3
        ):
            break

    df = pd.DataFrame(all_rows)

    required_columns = [
        "title",
        "price_gbp",
        "price_inr",
        "rating",
        "stock",
        "category",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise RuntimeError(
            f"Missing required columns: "
            f"{missing_columns}"
        )

    category_count = df["category"].nunique()

    if len(df) < 60:
        raise RuntimeError(
            f"Scraping failed validation: "
            f"only {len(df)} rows collected."
        )

    if category_count < 3:
        raise RuntimeError(
            "Scraping failed validation: "
            "fewer than 3 categories collected."
        )

    # Price extraction must succeed for every row.
    missing_prices = df["price_gbp"].isna().sum()

    if missing_prices > 0:
        raise RuntimeError(
            f"Scraping failed validation: "
            f"{missing_prices} rows have missing prices."
        )

    # Save using UTF-8 encoding.
    df.to_csv(
        RAW_OUTPUT,
        index=False,
        encoding="utf-8"
    )

    print()
    print("SCRAPING SUCCESSFUL")
    print(f"Rows collected: {len(df)}")
    print(f"Categories collected: {category_count}")
    print(f"Missing prices: {missing_prices}")
    print(f"Saved to: {RAW_OUTPUT}")


if __name__ == "__main__":
    main()