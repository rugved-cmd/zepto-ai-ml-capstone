# Module 1 — Data Pipeline

## Overview

Module 1 implements the data pipeline for the Zepto AI/ML Capstone Project.

The pipeline collects book data from a public website, cleans and transforms the data, stores the processed data in SQLite, performs SQL validation, and verifies the complete workflow.

The overall workflow is:

**Scrape → Clean → Convert → Store → Query → Validate**

---

## Objective

The main objectives of this module are:

- Collect book data from a public web source
- Clean and transform the collected data
- Convert prices from GBP to INR using the specified fixed conversion rate
- Store the cleaned data in a SQLite database
- Create a normalized database structure
- Execute SQL queries for validation and analysis
- Compare SQL JOIN results with pandas `merge()`
- Verify the complete pipeline using an automated verification script

---

## Source

The data is collected from:

**Books to Scrape**

The pipeline collects book information from multiple categories and produces a dataset containing more than the required number of books.

---

## Data Collected

The pipeline collects the following information for each book:

- Book title
- Price in GBP
- Star rating
- Availability
- Category

The cleaned dataset also contains the calculated INR price.

---

## Data Cleaning and Transformation

The raw scraped data is processed before being stored in the database.

The following transformations are performed:

- GBP prices are converted to numeric values.
- Text-based ratings such as `One`, `Two`, `Three`, `Four`, and `Five` are converted to integer values from 1 to 5.
- Availability information is converted into a boolean-style stock field.
- Invalid or incomplete records are handled during cleaning.
- Duplicate records are removed where required.

---

## Currency Conversion

The project uses the fixed conversion rate specified in the Capstone requirements:

**1 GBP = 105.50 INR**

The INR price is calculated using:

```text
price_inr = price_gbp × 105.50
```

The project uses this fixed conversion rate instead of a live currency API.

---

## Database Design

The cleaned data is stored in SQLite.

The database contains two related tables:

- `categories`
- `books`

The `categories` table stores category information.

The `books` table stores book-level information and references the category using a foreign key.

This structure reduces unnecessary duplication and provides a normalized relational design.

The database file is:

```text
data_pipeline/data/books.db
```

---

## SQL Validation

The module includes SQL validation queries demonstrating:

- `SELECT`
- `WHERE`
- `ORDER BY`
- `LIMIT`
- `DISTINCT`
- `IN`
- `BETWEEN`
- `JOIN`

The project also compares the SQL JOIN result with an equivalent pandas `merge()` operation.

This demonstrates both SQL-based and pandas-based approaches for combining related data.

---

## Project Structure

```text
data_pipeline/
│
├── data/
│   ├── books_raw.csv
│   ├── books_clean.csv
│   └── books.db
│
├── outputs/
│   └── sql_results/
│
├── src/
│   ├── scrape_books.py
│   ├── clean_and_store.py
│   ├── run_sql_checks.py
│   └── verify_pipeline.py
│
├── README.md
└── requirements.txt
```

---

## Script Responsibilities

### `scrape_books.py`

Collects book information from the public source and saves the raw dataset.

### `clean_and_store.py`

Cleans the scraped data, performs transformations, calculates INR prices, and stores the processed data in SQLite.

### `run_sql_checks.py`

Runs the required SQL queries and saves the SQL validation results.

### `verify_pipeline.py`

Performs end-to-end verification of the data pipeline and confirms that the required outputs and transformations are correct.

---

## Module Outputs

The module generates:

- Raw scraped data
- Cleaned book data
- SQLite database
- SQL query results
- Verification results

The generated files are stored under:

```text
data_pipeline/data/
data_pipeline/outputs/
```

---

## Verification Results

The completed pipeline was tested using the dedicated verification script.

The verification covers:

- Required files
- Scraped dataset
- Book count
- Category count
- Cleaned fields
- GBP-to-INR conversion
- SQLite database
- SQL queries
- SQL JOIN
- pandas `read_sql()`
- pandas `merge()`
- End-to-end pipeline functionality

The completed dataset contains:

- **69 books**
- **3 categories**

### Module 1 Status

**PASS**

---

## Design Decisions

### Requests and BeautifulSoup

Requests and BeautifulSoup are used to collect structured book information from the public web source.

### SQLite

SQLite was selected because it provides a lightweight relational database without requiring a separate database server.

### Normalized Database

Book and category information are stored in separate related tables to reduce unnecessary duplication and demonstrate relational database design.

### Fixed Currency Rate

The project uses the Capstone-defined conversion rate of:

**1 GBP = 105.50 INR**

A live currency API is not required for this project.

### Pandas

Pandas is used for data cleaning, transformation, SQL result loading, and comparison with SQL JOIN results.

---

## Module 1 Outcome

Module 1 successfully demonstrates an end-to-end data engineering workflow:

**Web Scraping → Data Cleaning → Transformation → SQLite Storage → SQL Validation → pandas Validation → Verification**

The resulting structured database is then reused by Module 2 and Module 3.