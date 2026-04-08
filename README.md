# Automated Business Decision Engine

A locally hosted web-based software system that formalizes structured business decision logic into a transparent, reproducible, and testable application.

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)
![Tests](https://img.shields.io/badge/Tests-60%20passing-brightgreen.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## Overview

This system accepts structured tabular datasets in CSV format, applies deterministic weighted decision rules to each record, computes a cumulative score, assigns a classification based on thresholds, and generates a human-readable explanation describing how the final decision was reached. All results are persisted in a SQLite database for historical review.

---

## Features

| Feature | Description |
|---------|-------------|
| CSV Upload | Upload datasets with validation for required columns and data types |
| Rule Engine | 7 weighted decision rules evaluate each record |
| Classification | Records classified as High Risk (≥40), Medium Risk (20-39), or Low Risk (<20) |
| Explanations | Human-readable traces showing triggered rules and score calculations |
| Database Storage | SQLite persistence for all evaluation runs |
| History View | Browse and review previous evaluations |
| Export CSV | Download results with scores, classifications, and explanations |
| Performance Metrics | Runtime tracking with records/second display |
| Pagination | Handle large datasets with 20 records per page |

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT BROWSER                           │
│                    (localhost:5000)                             │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                     FLASK APPLICATION                           │
│                      (routes.py)                                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │   Upload    │  │   Results   │  │        History          │ │
│  │   Route     │  │   Route     │  │        Route            │ │
│  └──────┬──────┘  └──────┬──────┘  └───────────┬─────────────┘ │
└─────────┼────────────────┼─────────────────────┼───────────────┘
          │                │                     │
          ▼                │                     │
┌─────────────────────┐    │                     │
│  VALIDATION MODULE  │    │                     │
│  (validation.py)    │    │                     │
│  • Column checking  │    │                     │
│  • Type validation  │    │                     │
│  • Null detection   │    │                     │
└─────────┬───────────┘    │                     │
          │                │                     │
          ▼                │                     │
┌─────────────────────┐    │                     │
│    RULE ENGINE      │    │                     │
│    (rules.py)       │    │                     │
│  • 7 weighted rules │    │                     │
│  • Condition funcs  │    │                     │
└─────────┬───────────┘    │                     │
          │                │                     │
          ▼                │                     │
┌─────────────────────┐    │                     │
│  DECISION ENGINE    │◄───┘                     │
│  (engine.py)        │                          │
│  • Scoring loop     │                          │
│  • Classification   │                          │
│  • Explanations     │                          │
│  • Metrics tracking │                          │
└─────────┬───────────┘                          │
          │                                      │
          ▼                                      │
┌─────────────────────────────────────────────────────────────────┐
│                    DATABASE MODULE                              │
│                    (database.py)                                │
│                                                                 │
│    ┌─────────────────────┐    ┌─────────────────────┐          │
│    │  evaluation_runs    │    │      results        │          │
│    │  • id (PK)          │───▶│  • id (PK)          │          │
│    │  • filename         │    │  • run_id (FK)      │          │
│    │  • total_records    │    │  • record_id        │          │
│    │  • runtime_ms       │    │  • score            │          │
│    │  • records_per_sec  │    │  • classification   │          │
│    │  • timestamp        │    │  • explanation      │          │
│    └─────────────────────┘    └─────────────────────┘          │
│                                                                 │
│                    SQLite: decision_engine.db                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Database Schema

### Table: `evaluation_runs`
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key, auto-increment |
| filename | TEXT | Original uploaded filename |
| total_records | INTEGER | Number of records processed |
| runtime_ms | REAL | Processing time in milliseconds |
| records_per_second | REAL | Processing speed |
| timestamp | DATETIME | When evaluation was run |

### Table: `results`
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key, auto-increment |
| run_id | INTEGER | Foreign key to evaluation_runs |
| record_id | TEXT | Original Record_ID from CSV |
| score | INTEGER | Calculated cumulative score |
| classification | TEXT | High Risk / Medium Risk / Low Risk |
| explanation | TEXT | Human-readable explanation trace |
| timestamp | DATETIME | When record was processed |

---

## Decision Rules

| Rule Name | Column | Condition | Weight | Description |
|-----------|--------|-----------|--------|-------------|
| Short Tenure | Tenure | < 12 | +15 | Customer tenure less than 12 months |
| Very Short Tenure | Tenure | < 6 | +10 | Customer tenure less than 6 months |
| High Late Payments | Late_Payments | > 3 | +20 | More than 3 late payments |
| Moderate Late Payments | Late_Payments | > 1 | +10 | More than 1 late payment |
| Low Revenue | Revenue | < 1000 | +15 | Revenue less than $1,000 |
| Very Low Revenue | Revenue | < 500 | +10 | Revenue less than $500 |
| High Revenue Contributor | Revenue | > 5000 | -10 | Revenue over $5,000 (reduces risk) |

## Classification Thresholds

| Classification | Score Range | Color |
|---------------|-------------|-------|
| High Risk | ≥ 40 | Red |
| Medium Risk | 20 - 39 | Yellow |
| Low Risk | < 20 | Green |

---

## Installation

### Prerequisites
- Python 3.11 or higher
- pip (Python package manager)

### Steps

1. **Clone the repository:**
   ```bash
   git clone https://github.com/moeezislammalik/automated-business-decision-engine.git
   cd automated-business-decision-engine
   ```

2. **Create virtual environment (optional but recommended):**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```bash
   python run.py
   ```

5. **Open in browser:**
   ```
   http://127.0.0.1:5000
   ```

---

## Running Tests

```bash
# Run all tests with verbose output
pytest tests/ -v

# Run with coverage report
pytest tests/ -v --cov=app

# Run specific test file
pytest tests/test_engine.py -v
```

**Current test count: 60 passing tests**

---

## Reproducing Demo Results

### Step 1: Start the Application
```bash
python run.py
```

### Step 2: Test with Sample Data

**Valid Dataset (10 records):**
1. Navigate to http://127.0.0.1:5000
2. Upload `data/sample_valid.csv`
3. View results with classifications and explanations

**Validation Error - Missing Column:**
1. Upload `data/sample_invalid_missing_column.csv`
2. Observe error message about missing "Revenue" column

**Validation Error - Invalid Data Type:**
1. Upload `data/sample_invalid_non_numeric.csv`
2. Observe error about non-numeric values

### Step 3: Performance Test (10,000 records)
1. Upload `data/synthetic_10000.csv`
2. Observe runtime metrics (~1 second processing time)
3. Navigate through paginated results

### Step 4: Export Results
1. After any evaluation, click "Export CSV"
2. Download contains Record_ID, Score, Classification, Explanation

### Step 5: View History
1. Click "History" in navigation
2. See all previous evaluation runs with timestamps
3. Click any run to view its results

---

## Project Structure

```
├── app/
│   ├── __init__.py              # Flask app factory
│   ├── routes.py                # URL routes (upload, results, history, export)
│   ├── modules/
│   │   ├── validation.py        # CSV schema validation
│   │   ├── rules.py             # Rule class and 7 default rules
│   │   ├── engine.py            # Decision engine with metrics
│   │   └── database.py          # SQLite persistence layer
│   ├── templates/
│   │   ├── base.html            # Base template with navigation
│   │   ├── upload.html          # File upload page
│   │   ├── results.html         # Results dashboard
│   │   ├── rules.html           # Rules overview
│   │   └── history.html         # Historical runs
│   └── static/css/
│       └── style.css            # Custom styling
├── tests/
│   ├── test_rules.py            # Rule evaluation tests (14)
│   ├── test_validation.py       # Validation tests (6)
│   ├── test_engine.py           # Engine tests (18)
│   ├── test_classification.py   # Classification tests (14)
│   └── test_database.py         # Database tests (8)
├── data/
│   ├── sample_valid.csv         # 10-row valid test data
│   ├── sample_invalid_*.csv     # Invalid test files
│   ├── synthetic_100.csv        # 100-row performance test
│   ├── synthetic_1000.csv       # 1,000-row performance test
│   └── synthetic_10000.csv      # 10,000-row performance test
├── docs/
│   └── VALIDATION_REPORT.md     # Test validation report
├── scripts/
│   └── generate_synthetic_data.py  # Dataset generator
├── requirements.txt             # Python dependencies
├── pytest.ini                   # Test configuration
└── run.py                       # Application entry point
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Upload page |
| POST | `/upload` | Process uploaded CSV |
| GET | `/rules` | View decision rules |
| GET | `/history` | View past evaluations |
| GET | `/history/<run_id>` | View specific run results |
| GET | `/export/<run_id>` | Download results as CSV |

---

## Technologies Used

- **Backend:** Python 3.11+, Flask 3.0
- **Database:** SQLite3
- **Data Processing:** Pandas, NumPy
- **Frontend:** HTML5, Bootstrap 5, Jinja2
- **Testing:** pytest
- **Version Control:** Git

---

## Author

**Moeez Malik**  
Senior Project - Spring 2026  
Computer Science & Business Analytics

---

## License

This project is licensed under the MIT License.
