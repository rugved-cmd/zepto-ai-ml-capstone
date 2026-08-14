
# Zepto AI/ML Capstone Project

## Data Pipeline • Analytics Pipeline • Support Assistant

This repository contains my Capstone Project for the Certificate Program in Artificial Intelligence and Machine Learning.

The project demonstrates an end-to-end data workflow starting from web data collection and continuing through data cleaning, database storage, analytics, and a catalogue-based support assistant.

Instead of treating each task as an independent project, the three modules are connected through a common SQLite database created by the data pipeline.

---

## Project Overview

The project consists of three connected modules:

### Module 1 — Data Pipeline

Collects book data from a public website, cleans and transforms the data, converts prices from GBP to INR, stores the processed data in SQLite, and performs SQL validation.

**Workflow:**

`Scrape → Clean → Convert → Store → Query → Validate`

### Module 2 — Analytics Pipeline

Uses the structured data produced by Module 1 to analyse categories, ratings, prices, rankings, and business-oriented insights.

**Workflow:**

`Load Data → Analyse → Rank → Generate Insights → Save Results → Verify`

### Module 3 — Support Assistant

Uses the same SQLite catalogue created by Module 1 to provide book search and recommendation functionality based on category, price, and rating constraints.

**Workflow:**

`Load SQLite Data → Search → Filter → Recommend → Save Results → Verify`

---

# Project Architecture

```text
                    PUBLIC WEB SOURCE
                           │
                           ▼
              ┌─────────────────────────┐
              │     MODULE 1             │
              │     DATA PIPELINE        │
              │                         │
              │ Scraping                │
              │ Cleaning                │
              │ Transformation          │
              │ Currency Conversion     │
              │ SQLite Storage           │
              │ SQL Validation          │
              └────────────┬────────────┘
                           │
                           │ books.db
                           ▼
              ┌─────────────────────────┐
              │     MODULE 2             │
              │  ANALYTICS PIPELINE      │
              │                         │
              │ Category Analysis       │
              │ Rating Analysis         │
              │ Price Analysis          │
              │ Rankings                │
              │ Business Insights       │
              └─────────────────────────┘

                           │
                           │ Same SQLite Catalogue
                           ▼

              ┌─────────────────────────┐
              │     MODULE 3             │
              │   SUPPORT ASSISTANT      │
              │                         │
              │ Book Search             │
              │ Filtering               │
              │ Recommendations         │
              │ CSV Results             │
              └─────────────────────────┘


---

Repository Structure

zepto-ai-ml-capstone/
│
├── data_pipeline/
│   ├── data/
│   │   ├── books_raw.csv
│   │   ├── books_clean.csv
│   │   └── books.db
│   │
│   ├── outputs/
│   │   └── sql_results/
│   │
│   ├── src/
│   │   ├── scrape_books.py
│   │   ├── clean_and_store.py
│   │   ├── run_sql_checks.py
│   │   └── verify_pipeline.py
│   │
│   ├── README.md
│   └── requirements.txt
│
├── analytics/
│   ├── outputs/
│   │
│   ├── src/
│   │   ├── analytics.py
│   │   └── verify_analytics.py
│   │
│   ├── README.md
│   └── requirements.txt
│
├── support_assistant/
│   ├── outputs/
│   │   ├── last_search_results.csv
│   │   └── recommendations.csv
│   │
│   ├── src/
│   │   ├── assistant.py
│   │   └── verify_assistant.py
│   │
│   ├── README.md
│   └── requirements.txt
│
├── tests/
│
├── .gitignore
├── requirements.txt
└── README.md


---

Technology Stack

The project uses the following technologies:

Python

Pandas

NumPy

Requests

BeautifulSoup

SQLite

SQL

Scikit-learn

Matplotlib

Seaborn

Plotly

OpenPyXL

SQLAlchemy

Pytest

Git

GitHub



---

Requirements

Python 3.x is required.

The repository contains:

A root requirements.txt for the complete project

A separate requirements.txt inside each module for module-specific dependencies


The recommended approach is to install the root requirements once from the project root.


---

Setup

1. Clone the Repository

git clone https://github.com/rugved-cmd/zepto-ai-ml-capstone.git
cd zepto-ai-ml-capstone

2. Create a Virtual Environment

Windows

python -m venv .venv

Activate the environment:

.venv\Scripts\Activate.ps1

If PowerShell activation is not available, the environment can also be activated using:

.venv\Scripts\activate

3. Install Project Dependencies

pip install -r requirements.txt


---

How to Run the Complete Project

The modules should be executed in order because Module 2 and Module 3 use the structured data created by Module 1.

Step 1 — Run Module 1

1. Scrape the data

python data_pipeline/src/scrape_books.py

This collects the book data and creates the raw dataset.

2. Clean the data and create the database

python data_pipeline/src/clean_and_store.py

This cleans and transforms the data and creates the SQLite database.

3. Run SQL validation

python data_pipeline/src/run_sql_checks.py

This executes the required SQL checks and stores the generated results.

4. Verify Module 1

python data_pipeline/src/verify_pipeline.py

This verifies the complete data pipeline.


---

Step 2 — Run Module 2

After Module 1 has successfully completed, run the analytics pipeline.

1. Generate analytics

python analytics/src/analytics.py

This analyses the structured book dataset and generates analytical outputs.

2. Verify Module 2

python analytics/src/verify_analytics.py

This checks whether the expected analytics outputs were generated correctly.


---

Step 3 — Run Module 3

After Module 1 has successfully created the SQLite database, the support assistant can be executed.

1. Run the Support Assistant

python support_assistant/src/assistant.py

The assistant provides book search and recommendation functionality.

2. Verify Module 3

python support_assistant/src/verify_assistant.py

This verifies:

SQLite database connectivity

Book search

Recommendation functionality

Recommendation constraints

Generated output files



---

Complete Execution Order

For a fresh end-to-end execution, use the following order:

MODULE 1 — DATA PIPELINE
        │
        ├── scrape_books.py
        ├── clean_and_store.py
        ├── run_sql_checks.py
        └── verify_pipeline.py
        │
        ▼
MODULE 2 — ANALYTICS PIPELINE
        │
        ├── analytics.py
        └── verify_analytics.py
        │
        ▼
MODULE 3 — SUPPORT ASSISTANT
        │
        ├── assistant.py
        └── verify_assistant.py

Commands in Order

python data_pipeline/src/scrape_books.py

python data_pipeline/src/clean_and_store.py

python data_pipeline/src/run_sql_checks.py

python data_pipeline/src/verify_pipeline.py

python analytics/src/analytics.py

python analytics/src/verify_analytics.py

python support_assistant/src/assistant.py

python support_assistant/src/verify_assistant.py


---

Module 1 — Data Pipeline

Purpose

Module 1 builds the foundation of the complete project.

It collects book information from a public web source and prepares the data for the remaining modules.

Main Operations

Web scraping

Data cleaning

Data transformation

Rating conversion

Price conversion

Currency conversion

SQLite database creation

SQL querying

SQL JOIN validation

Pandas validation

End-to-end verification


Data Source

The project uses Books to Scrape as the public web source.

Data Collected

The pipeline collects:

Book title

Price in GBP

Star rating

Availability

Category


Currency Conversion

The Capstone-defined fixed conversion rate is:

1 GBP = 105.50 INR

The INR price is calculated as:

price_inr = price_gbp × 105.50

Database

The cleaned data is stored in SQLite.

The database is available at:

data_pipeline/data/books.db

The module uses a normalized database structure containing related category and book information.

Module Documentation

Detailed Module 1 documentation is available at:

data_pipeline/README.md


---

Module 2 — Analytics Pipeline

Purpose

Module 2 analyses the structured dataset created by Module 1.

Main Analysis Areas

Category performance

Rating distribution

Price analysis

Most expensive books

Highly-rated books

Affordable books

Rankings

Business-oriented insights


Data Source

Module 2 uses:

data_pipeline/data/books.db

Outputs

Analytical results are stored in:

analytics/outputs/

Module Documentation

Detailed Module 2 documentation is available at:

analytics/README.md


---

Module 3 — Support Assistant

Purpose

Module 3 provides a simple catalogue-based support assistant.

It uses the same structured SQLite database created by Module 1.

Features

Book search

Keyword-based search

Category filtering

Maximum price filtering

Minimum rating filtering

Book recommendations

Search result export

Recommendation result export


Data Source

The assistant uses:

data_pipeline/data/books.db

This means Module 3 does not maintain a separate copy of the book catalogue.

Outputs

The generated results are stored in:

support_assistant/outputs/

The main output files are:

last_search_results.csv
recommendations.csv

Module Documentation

Detailed Module 3 documentation is available at:

support_assistant/README.md


---

Verification

Each module contains its own verification script.

Module 1

python data_pipeline/src/verify_pipeline.py

Verifies the data pipeline, cleaned data, database, SQL operations, JOIN logic, and pandas operations.

Module 2

python analytics/src/verify_analytics.py

Verifies the generated analytical outputs.

Module 3

python support_assistant/src/verify_assistant.py

Verifies database connectivity, search, recommendations, constraints, and generated files.

The verification scripts are included to make the project easier to reproduce and evaluate.


---

Key Results

The current project dataset contains:

Metric	Result

Books	69
Categories	3
Rating Groups	5
GBP → INR Rate	1 GBP = 105.50 INR


The project demonstrates:

Web scraping

Data cleaning

Data transformation

Currency conversion

Relational database design

SQLite

SQL querying

SQL JOIN operations

Pandas data processing

Analytics

Business insight generation

Search functionality

Recommendation logic

Automated verification



---

Design Decisions

Why Requests and BeautifulSoup?

Requests and BeautifulSoup are used for collecting structured information from the public web source required for the data pipeline.

Why SQLite?

SQLite provides a lightweight relational database that does not require a separate database server.

It is suitable for this project because the dataset is relatively small and the database can be easily reproduced and inspected.

Why Pandas?

Pandas is used for data cleaning, transformation, analysis, filtering, ranking, and comparison operations.

Why a Fixed Currency Rate?

The project follows the Capstone-defined conversion rate:

1 GBP = 105.50 INR

A live currency API is not required for this implementation.

Why Share One Database?

Modules 2 and 3 use the database produced by Module 1.

This avoids duplicate datasets and ensures that the complete project follows one connected data flow.


---

Reproducibility

The project is organized so that another user can reproduce the workflow by:

1. Cloning the repository


2. Creating a Python virtual environment


3. Installing the required dependencies


4. Running Module 1


5. Verifying Module 1


6. Running Module 2


7. Verifying Module 2


8. Running Module 3


9. Verifying Module 3



The module-level README files provide additional details for each stage.


---

GitHub Repository

The complete source code and documentation are available here:

https://github.com/rugved-cmd/zepto-ai-ml-capstone


---

Academic Integrity

This project was developed as my Capstone submission for the Certificate Program in Artificial Intelligence and Machine Learning.

Official documentation and learning resources were used where necessary, while the project implementation, testing, documentation, and verification were completed as part of the capstone development process.


---

Author

Rugved

B.Tech — Computer Science and Engineering

AI/ML | Python | Data Analytics | SQL


---

Project Summary

The project demonstrates a complete data-to-application workflow:

Public Web Data
      ↓
Data Collection
      ↓
Data Cleaning & Transformation
      ↓
SQLite Database
      ↓
SQL Validation
      ↓
Analytics & Business Insights
      ↓
Search & Recommendation Assistant
      ↓
Verification

The three modules together demonstrate how raw data can be transformed into structured information, analysed for insights, and finally used to build a simple user-oriented support system.

### One important thing, bro

Your **root README** should be this one.

Your three module READMEs should remain:

```text
data_pipeline/README.md
analytics/README.md
support_assistant/README.md

So your final documentation structure is:

README.md                         ← MAIN PROJECT README
│
├── data_pipeline/
│   ├── README.md                ← MODULE 1 README
│   └── requirements.txt
│
├── analytics/
│   ├── README.md                ← MODULE 2 README
│   └── requirements.txt
│
└── support_assistant/
    ├── README.md                ← MODULE 3 README
    └── requirements.txt


