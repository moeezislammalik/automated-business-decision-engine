# End-to-End Testing Report
## Automated Business Decision Engine

**Date:** April 2026  
**Tester:** Moeez Malik  
**Environment:** macOS, Python 3.13, Flask 3.1

---

## Test Environment Setup

```bash
# Clone repository
git clone https://github.com/moeezislammalik/automated-business-decision-engine.git
cd automated-business-decision-engine

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start application
python run.py
```

---

## E2E Test Scenarios

### Scenario 1: Complete Upload-to-Export Flow

**Steps:**
1. Navigate to http://127.0.0.1:5000
2. Upload `data/sample_valid.csv`
3. View results dashboard
4. Expand explanation for Record R003
5. Click "Export CSV"
6. Open downloaded file

**Expected Results:**
| Step | Expected | Result |
|------|----------|--------|
| Upload | File accepted, redirects to results | ✅ Pass |
| Dashboard | Shows 10 records, classification cards | ✅ Pass |
| Classifications | Mix of High/Medium/Low | ✅ Pass |
| Explanation | Shows triggered rules with weights | ✅ Pass |
| Export | CSV downloads with all data | ✅ Pass |

**Screenshots Required:** Results dashboard, Expanded explanation

---

### Scenario 2: Validation Error Handling

**Steps:**
1. Upload `data/sample_invalid_missing_column.csv`
2. Observe error message
3. Upload `data/sample_invalid_non_numeric.csv`
4. Observe error message

**Expected Results:**
| Step | Expected | Result |
|------|----------|--------|
| Missing column | Error: "Required columns are missing: Revenue" | ✅ Pass |
| Non-numeric | Error: "Column contains non-numeric values" | ✅ Pass |
| No crash | Application remains functional | ✅ Pass |

**Screenshots Required:** Error message display

---

### Scenario 3: Large Dataset Performance

**Steps:**
1. Upload `data/synthetic_10000.csv`
2. Note processing time
3. Navigate through pagination
4. Export results

**Expected Results:**
| Step | Expected | Result |
|------|----------|--------|
| Processing | Completes in < 2 seconds | ✅ Pass (1.1s) |
| Metrics | Shows runtime and records/sec | ✅ Pass |
| Pagination | 500 pages, navigation works | ✅ Pass |
| UI responsive | No freezing or lag | ✅ Pass |
| Export | Large CSV downloads | ✅ Pass |

**Screenshots Required:** Performance metrics display

---

### Scenario 4: History Persistence

**Steps:**
1. Upload `data/sample_valid.csv`
2. Note run ID
3. Upload `data/synthetic_100.csv`
4. Navigate to History page
5. Click on first run to view

**Expected Results:**
| Step | Expected | Result |
|------|----------|--------|
| First upload | Creates run entry | ✅ Pass |
| Second upload | Creates separate entry | ✅ Pass |
| History page | Shows both runs | ✅ Pass |
| View old run | Displays correct results | ✅ Pass |
| Timestamps | Accurate and ordered | ✅ Pass |

**Screenshots Required:** History page with multiple runs

---

### Scenario 5: Classification Boundary Testing

**Test Data:** Custom CSV with boundary values

| Record | Tenure | Late_Payments | Revenue | Expected Score | Expected Class |
|--------|--------|---------------|---------|----------------|----------------|
| B001 | 24 | 0 | 6000 | -10 | Low Risk |
| B002 | 11 | 2 | 800 | 40 | High Risk |
| B003 | 6 | 1 | 2000 | 25 | Medium Risk |
| B004 | 3 | 4 | 400 | 80 | High Risk |

**Results:**
| Record | Actual Score | Actual Class | Match |
|--------|--------------|--------------|-------|
| B001 | -10 | Low Risk | ✅ |
| B002 | 40 | High Risk | ✅ |
| B003 | 25 | Medium Risk | ✅ |
| B004 | 80 | High Risk | ✅ |

---

### Scenario 6: Multiple Consecutive Operations

**Steps:**
1. Upload valid file
2. Export results
3. View history
4. Upload invalid file (error)
5. Upload another valid file
6. View history again

**Expected Results:**
| Step | Expected | Result |
|------|----------|--------|
| All operations | No errors or crashes | ✅ Pass |
| History | Shows only successful uploads | ✅ Pass |
| State | Application maintains consistency | ✅ Pass |

---

## Browser Compatibility

| Browser | Version | Status |
|---------|---------|--------|
| Chrome | Latest | ✅ Pass |
| Safari | Latest | ✅ Pass |
| Firefox | Latest | ✅ Pass |

---

## Performance Benchmarks

| Dataset Size | Avg Processing Time | Records/Second |
|--------------|---------------------|----------------|
| 10 records | 3 ms | 3,333 |
| 100 records | 15 ms | 6,667 |
| 1,000 records | 120 ms | 8,333 |
| 10,000 records | 1,100 ms | 9,091 |

---

## Issues Found & Resolved

| Issue | Severity | Resolution |
|-------|----------|------------|
| Database schema migration | Medium | Delete and recreate DB |
| Port 5000 in use | Low | Kill existing process |

---

## E2E Test Summary

| Category | Tests | Passed | Failed |
|----------|-------|--------|--------|
| Upload Flow | 5 | 5 | 0 |
| Validation | 3 | 3 | 0 |
| Performance | 5 | 5 | 0 |
| History | 5 | 5 | 0 |
| Boundaries | 4 | 4 | 0 |
| Stability | 3 | 3 | 0 |
| **Total** | **25** | **25** | **0** |

**Overall Status: ✅ ALL TESTS PASSED**

---

## Sign-Off

End-to-end testing completed successfully. Application is ready for final demonstration.
