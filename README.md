# \# Zepto AI/ML Capstone Project

# 

# \## Overview

# 

# This project is my Capstone submission for the Certificate Program in Artificial Intelligence and Machine Learning.

# 

# The objective of the project is to build one connected platform covering three different areas of an AI/ML engineering workflow:

# 

# \- collecting and preparing data

# \- analysing the prepared data and generating business insights

# \- building a support assistant using the structured data

# 

# The complete project is maintained in a single GitHub repository, as required by the Capstone instructions.

# 

# \---

# 

# \## Project Modules

# 

# | Module | Description | Main Focus |

# |---|---|---|

# | Module 1 | Data Pipeline | Web scraping, data cleaning, currency conversion, SQLite, SQL and pandas |

# | Module 2 | Analytics Pipeline | Data analysis, rankings, price/rating analysis and business insights |

# | Module 3 | Support Assistant | Book search and recommendation functionality |

# 

# \---

# 

# \# Project Structure

# 

# ```text

# zepto-ai-ml-capstone/

# │

# ├── data\_pipeline/

# │   ├── data/

# │   │   ├── books\_raw.csv

# │   │   ├── books\_clean.csv

# │   │   └── books.db

# │   │

# │   ├── outputs/

# │   │   └── sql\_results/

# │   │

# │   └── src/

# │       ├── scrape\_books.py

# │       ├── clean\_and\_store.py

# │       ├── run\_sql\_checks.py

# │       └── verify\_pipeline.py

# │

# ├── analytics/

# │   ├── outputs/

# │   └── src/

# │       ├── analytics.py

# │       └── verify\_analytics.py

# │

# ├── support\_assistant/

# │   ├── outputs/

# │   │   ├── last\_search\_results.csv

# │   │   └── recommendations.csv

# │   │

# │   └── src/

# │       ├── assistant.py

# │       └── verify\_assistant.py

# │

# ├── requirements.txt

# └── README.md

# Technology Stack

# Python

# Pandas

# Requests

# BeautifulSoup

# SQLite

# SQL

# Git

# GitHub

# Setup

# Requirements

# 

# Python 3.x is required.

# 

# The project uses one consolidated requirements.txt file at the root of the repository.

# 

# 1\. Clone the Repository

# git clone <YOUR\_GITHUB\_REPOSITORY\_URL>

# cd zepto-ai-ml-capstone

# 2\. Create a Virtual Environment

# Windows

# python -m venv .venv

# 

# Activate it:

# 

# .venv\\Scripts\\Activate.ps1

# 3\. Install Dependencies

# pip install -r requirements.txt

# Module 1 — Data Pipeline

# Objective

# 

# The first module builds an end-to-end data pipeline starting from a public web scraping source.

# 

# The workflow is:

# 

# Scrape → Clean → Convert → Store → Query → Validate

# 

# The source used is:

# 

# Books to Scrape

# 

# The scraper collects book information from at least three categories and produces a dataset containing more than the required 60 books.

# 

# Data Collected

# 

# For each book, the pipeline collects:

# 

# Title

# Price in GBP

# Star rating

# Availability

# Category

# Data Cleaning

# 

# The scraped data is converted into appropriate data types.

# 

# The following transformations are performed:

# 

# GBP price is converted into a numeric price\_gbp value.

# Text ratings such as One, Two, Three, Four, and Five are converted into integer values from 1 to 5.

# Availability is converted into a boolean-style stock field.

# Invalid or incomplete records are handled during the cleaning stage.

# Duplicate books are removed where required.

# Currency Conversion

# 

# The project uses the fixed conversion rate specified in the Capstone instructions:

# 

# 1 GBP = 105.50 INR

# 

# This is a project-defined fixed rate and does not use a live currency API.

# 

# The INR price is calculated using:

# 

# price\_inr = price\_gbp × 105.50

# Database

# 

# The cleaned data is stored in SQLite.

# 

# The database follows a normalized structure with:

# 

# categories

# books

# 

# The tables are connected using a primary key and foreign key relationship.

# 

# Run Module 1

# Step 1 — Scrape the data

# python data\_pipeline/src/scrape\_books.py

# Step 2 — Clean the data and create the database

# python data\_pipeline/src/clean\_and\_store.py

# Step 3 — Run SQL validation

# python data\_pipeline/src/run\_sql\_checks.py

# 

# The SQL validation demonstrates:

# 

# SELECT

# WHERE

# ORDER BY

# LIMIT

# DISTINCT

# IN

# BETWEEN

# JOIN

# 

# The project also compares the JOIN result produced using SQL with the equivalent result generated using pandas merge().

# 

# Step 4 — Verify the complete pipeline

# python data\_pipeline/src/verify\_pipeline.py

# Module 2 — Analytics Pipeline

# Objective

# 

# The second module uses the structured data produced by Module 1 and performs analysis to extract useful information from the dataset.

# 

# The analysis includes:

# 

# Category performance

# Rating distribution

# Price analysis

# Most expensive books

# Highest-rated books

# Affordable books

# Business insights

# 

# The outputs are saved inside the analytics/outputs/ directory.

# 

# Run Module 2

# python analytics/src/analytics.py

# Verify Module 2

# python analytics/src/verify\_analytics.py

# 

# The verification checks the generated analytical outputs and confirms that the expected results are present.

# 

# Module 3 — Support Assistant

# Objective

# 

# The third module provides a simple support assistant based on the structured book catalogue.

# 

# It allows users to search for books and generate recommendations using different constraints.

# 

# The recommendation functionality supports filtering based on:

# 

# Category

# Price

# Rating

# 

# The generated search and recommendation results are saved as CSV files.

# 

# Run Module 3

# python support\_assistant/src/assistant.py

# Verify Module 3

# python support\_assistant/src/verify\_assistant.py

# 

# The verification checks:

# 

# database connectivity

# book search

# recommendation results

# recommendation constraints

# generated output files

# End-to-End Execution

# 

# To reproduce the project from the beginning, run the modules in the following order.

# 

# Module 1

# python data\_pipeline/src/scrape\_books.py

# python data\_pipeline/src/clean\_and\_store.py

# python data\_pipeline/src/run\_sql\_checks.py

# python data\_pipeline/src/verify\_pipeline.py

# Module 2

# python analytics/src/analytics.py

# python analytics/src/verify\_analytics.py

# Module 3

# python support\_assistant/src/assistant.py

# python support\_assistant/src/verify\_assistant.py

# Verification Results

# 

# The completed project was tested using dedicated verification scripts.

# 

# Module 1

# 

# The pipeline verifies:

# 

# required files

# scraped dataset

# book count

# category count

# cleaned fields

# fixed GBP-to-INR conversion

# SQLite database

# SQL queries

# JOIN operation

# pandas read\_sql

# pandas merge

# Module 2

# 

# The analytics verification confirms:

# 

# required output files

# category performance

# rating analysis

# price analysis

# ranked book outputs

# business insights

# Module 3

# 

# The support assistant verification confirms:

# 

# SQLite database connection

# book search

# recommendation engine

# recommendation constraints

# generated output files

# Key Results

# 

# The current project dataset contains:

# 

# 69 books

# 3 categories

# 5 rating groups

# Fixed conversion rate of 1 GBP = 105.50 INR

# 

# The project also successfully demonstrates:

# 

# Web scraping

# Data cleaning

# Data transformation

# Relational database design

# SQL querying

# Pandas analysis

# Business insight generation

# Search and recommendation logic

# End-to-end verification

# Design Decisions

# Module 1

# 

# I used requests and BeautifulSoup because the project requires scraping from a public website.

# 

# SQLite was selected because it provides a lightweight relational database without requiring a separate database server.

# 

# The book and category information is separated into related tables to avoid unnecessary duplication and to satisfy the normalized database requirement.

# 

# The fixed project conversion rate was used instead of a live currency API because the Capstone explicitly defines the baseline as 1 GBP = 105.50 INR.

# 

# Module 2

# 

# I used pandas for the analytical workflow because the dataset is structured and can be efficiently grouped, filtered and ranked using DataFrames.

# 

# The analysis focuses on information that can be interpreted from a business perspective, such as pricing, ratings and category performance.

# 

# Module 3

# 

# The support assistant uses the structured catalogue created in Module 1 rather than maintaining a separate copy of the data.

# 

# This keeps the three modules connected and allows the search and recommendation functionality to work with the same cleaned data source.

# 

# Git Workflow

# 

# The project was developed using Git and a feature branch.

# 

# The main development branch used for the project is:

# 

# feature/capstone-development

# 

# The repository also contains the main branch.

# 

# The Git history contains multiple commits representing the development of the project.

# 

# Academic Integrity

# 

# This project was developed as my Capstone submission.

# 

# I used official documentation and learning resources when required, while implementing and testing the project myself.

# 

# I have also included verification scripts so that the main functionality can be checked after setup.

# 

# Author

# 

# Rugved

# 

# B.Tech — Computer Science and Engineering

