# Module 3 — Support Assistant

## Overview

Module 3 is the support assistant stage of the Zepto AI/ML Capstone Project.

This module uses the structured book catalogue created by Module 1 to provide book search and recommendation functionality.

The assistant allows users to search for books and generate recommendations based on constraints such as category, price, and rating.

The workflow is:

**Load SQLite Data → Search → Apply Filters → Generate Recommendations → Save Results → Verify**

---

## Objectives

The main objectives of this module are:

- Load the verified book catalogue from SQLite
- Provide book search functionality
- Search books using user-provided keywords
- Generate book recommendations
- Apply category constraints
- Apply price constraints
- Apply rating constraints
- Save search and recommendation results
- Verify the assistant functionality using an automated verification script

---

## Data Source

Module 3 uses the SQLite database created by Module 1:

```text
data_pipeline/data/books.db
```

The assistant uses the same structured catalogue instead of maintaining a separate copy of the data.

This keeps the three project modules connected.

---

## Support Assistant Features

### Book Search

Users can search the catalogue using book-related keywords.

The search functionality returns matching books from the verified database.

### Book Recommendations

The recommendation engine generates recommendations based on requested conditions.

The recommendation functionality supports:

- Category
- Maximum price
- Minimum rating

The returned recommendations are checked against the requested constraints.

---

## Project Structure

```text
support_assistant/
│
├── outputs/
│   ├── last_search_results.csv
│   └── recommendations.csv
│
├── src/
│   ├── assistant.py
│   └── verify_assistant.py
│
├── README.md
└── requirements.txt
```

---

## Script Responsibilities

### `assistant.py`

Loads the book database and provides the search and recommendation functionality.

### `verify_assistant.py`

Verifies database connectivity, book search, recommendations, recommendation constraints, and generated output files.

---

## Output Files

The assistant stores generated results inside:

```text
support_assistant/outputs/
```

### `last_search_results.csv`

Contains the results from the most recent book search.

### `recommendations.csv`

Contains the books returned by the recommendation engine.

These outputs make it possible to inspect the assistant's results after execution.

---

## Verification Results

The Module 3 verification script successfully checks the main functionality of the support assistant.

The verification covers:

- SQLite database connection
- Book search
- Recommendation engine
- Recommendation constraints
- Generated output files

### Verified Results

- **69 books loaded**
- **3 categories available**
- **Mystery search returned 32 valid books**
- **5 recommendations satisfied the requested filters**
- Category constraints verified
- Price constraints verified
- Rating constraints verified
- Search output verified
- Recommendation output verified

### Module 3 Status

**PASS**

---

## Design Decisions

### Reusing Module 1 Database

The support assistant directly uses the structured SQLite database produced by Module 1.

This avoids maintaining duplicate datasets and keeps the complete capstone project connected.

### Pandas

Pandas is used to load and process the structured book data and perform the filtering operations required for search and recommendations.

### SQLite

SQLite provides a lightweight and reliable source for the book catalogue without requiring a separate database server.

### Constraint-Based Recommendations

The recommendation engine uses explicit category, price, and rating constraints so that returned recommendations satisfy the requested conditions.

---

## Connection With Other Modules

The complete project follows a connected workflow:

### Module 1 — Data Pipeline

Collects, cleans, transforms, and stores the book data.

↓

### Module 2 — Analytics Pipeline

Analyses the structured data and generates business insights.

↓

### Module 3 — Support Assistant

Uses the structured catalogue to provide search and recommendation functionality.

This design ensures that all three modules work as parts of one connected project rather than as independent applications.

---

## Module 3 Outcome

Module 3 successfully demonstrates a catalogue-based support assistant with search and recommendation functionality.

The workflow is:

**SQLite Catalogue → Search → Filtering → Recommendations → CSV Outputs → Verification**

The module completes the user-facing workflow of the capstone project by turning the structured book catalogue into a simple search and recommendation system.