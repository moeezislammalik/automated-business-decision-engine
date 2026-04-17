# Testing Guide
## Automated Business Decision Engine

---

## Quick Start

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=app --cov-report=term-missing

# Run specific test file
pytest tests/test_engine.py -v

# Run specific test class
pytest tests/test_engine.py::TestDecisionEngine -v

# Run specific test
pytest tests/test_classification.py::TestClassificationThresholds::test_high_risk_at_threshold -v
```

---

## Test Suite Overview

| File | Tests | Description |
|------|-------|-------------|
| `test_rules.py` | 14 | Rule class and condition functions |
| `test_validation.py` | 6 | CSV validation and error handling |
| `test_engine.py` | 18 | Scoring engine and metrics |
| `test_classification.py` | 14 | Classification thresholds and explanations |
| `test_database.py` | 8 | SQLite persistence operations |
| **Total** | **60** | |

---

## Test Categories

### 1. Unit Tests - Rules (`test_rules.py`)

**Condition Functions:**
- `test_less_than_true` - Value below threshold
- `test_less_than_false` - Value above threshold
- `test_less_than_equal_boundary` - Value equals threshold
- `test_greater_than_true` - Value above threshold
- `test_greater_than_false` - Value below threshold
- `test_greater_than_equal_boundary` - Value equals threshold

**Rule Class:**
- `test_rule_creation` - Rule object initialization
- `test_rule_evaluate_triggers` - Rule condition met
- `test_rule_evaluate_does_not_trigger` - Rule condition not met
- `test_rule_evaluate_missing_column` - Handles missing data
- `test_rule_evaluate_boundary_value` - Boundary condition

**Default Rules:**
- `test_default_rules_count` - At least 5 rules defined
- `test_default_rules_have_required_attributes` - All attributes present
- `test_negative_weight_rule_exists` - High revenue rule exists

### 2. Unit Tests - Validation (`test_validation.py`)

- `test_valid_csv_passes_validation` - Valid file accepted
- `test_missing_required_column_fails` - Missing column detected
- `test_empty_file_fails` - Empty file rejected
- `test_non_numeric_value_fails` - Type errors detected
- `test_check_required_columns_all_present` - All columns present
- `test_check_required_columns_missing` - Missing columns listed

### 3. Unit Tests - Engine (`test_engine.py`)

**EvaluationResult:**
- `test_result_creation` - Result object creation
- `test_result_to_dict` - Serialization to dictionary

**EvaluationMetrics:**
- `test_metrics_creation` - Metrics object creation
- `test_metrics_to_dict` - Serialization
- `test_runtime_formatted_ms` - Millisecond formatting
- `test_runtime_formatted_seconds` - Second formatting

**DecisionEngine:**
- `test_engine_with_default_rules` - Default rules loaded
- `test_engine_with_custom_rules` - Custom rules work
- `test_evaluate_single_record_no_triggers` - Zero score
- `test_evaluate_single_record_with_trigger` - Score calculated
- `test_evaluate_multiple_rules_cumulative_score` - Scores accumulate
- `test_evaluate_high_risk_classification` - High risk assigned
- `test_evaluate_dataset_returns_tuple` - Returns (results, metrics)
- `test_evaluate_dataset_scores` - Correct scores
- `test_evaluate_dataset_classifications` - Correct classifications
- `test_evaluate_dataset_metrics_runtime` - Runtime tracked
- `test_get_rules_summary` - Summary generated
- `test_get_classification_thresholds` - Thresholds returned

### 4. Unit Tests - Classification (`test_classification.py`)

**Threshold Tests:**
- `test_high_risk_at_threshold` - Score = 40
- `test_high_risk_above_threshold` - Score > 40
- `test_medium_risk_at_threshold` - Score = 20
- `test_medium_risk_between_thresholds` - 20 ≤ Score < 40
- `test_low_risk_below_threshold` - Score < 20
- `test_boundary_medium_to_high` - 39 vs 40
- `test_boundary_low_to_medium` - 19 vs 20
- `test_negative_score` - Negative scores

**Explanation Tests:**
- `test_explanation_no_rules_triggered` - Empty explanation
- `test_explanation_with_triggered_rules` - Rules listed
- `test_explanation_contains_weight_sum` - Calculation shown
- `test_explanation_high_risk_threshold_text` - Threshold text
- `test_explanation_medium_risk_threshold_text` - Threshold text
- `test_explanation_low_risk_threshold_text` - Threshold text

### 5. Unit Tests - Database (`test_database.py`)

**Initialization:**
- `test_init_creates_tables` - Tables created

**Save Operations:**
- `test_save_single_result` - Single record saved
- `test_save_multiple_results` - Multiple records saved

**Retrieval:**
- `test_get_runs_empty` - Empty database
- `test_get_runs_after_save` - Runs retrieved
- `test_get_nonexistent_run` - Returns None
- `test_get_existing_run` - Results retrieved

**Summary:**
- `test_summary_counts` - Classification counts correct

---

## Manual Testing Scenarios

### Scenario 1: Valid Upload Flow
1. Start app: `python run.py`
2. Open http://127.0.0.1:5000
3. Upload `data/sample_valid.csv`
4. Verify: 10 records processed
5. Verify: Classification cards show counts
6. Click "View Explanation" on any row
7. Verify: Explanation shows triggered rules

### Scenario 2: Validation Errors
1. Upload `data/sample_invalid_missing_column.csv`
2. Verify: Error message shows "Revenue" missing
3. Upload `data/sample_invalid_non_numeric.csv`
4. Verify: Error about non-numeric values

### Scenario 3: Performance Test
1. Upload `data/synthetic_10000.csv`
2. Verify: Processes in ~1 second
3. Verify: Runtime metrics displayed
4. Verify: Pagination shows 500 pages

### Scenario 4: Export
1. After any upload, click "Export CSV"
2. Verify: File downloads
3. Open file, verify columns present

### Scenario 5: History
1. Click "History" in navigation
2. Verify: Previous runs listed
3. Click "View" on any run
4. Verify: Results displayed correctly

---

## Continuous Integration

To run tests in CI/CD:

```yaml
# GitHub Actions example
- name: Run tests
  run: |
    pip install -r requirements.txt
    pytest tests/ -v --tb=short
```

---

## Test Coverage Goals

| Module | Target | Current |
|--------|--------|---------|
| validation.py | 90% | ✅ |
| rules.py | 95% | ✅ |
| engine.py | 90% | ✅ |
| database.py | 85% | ✅ |

---

## Adding New Tests

1. Create test file in `tests/` directory
2. Name file `test_<module>.py`
3. Create test class `Test<Feature>`
4. Name methods `test_<description>`
5. Run `pytest tests/ -v` to verify
