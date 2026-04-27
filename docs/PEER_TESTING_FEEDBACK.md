# Peer Usability Testing Feedback
## Automated Business Decision Engine

**Date:** April 2026
**Tested By:** Moeez Malik
**Application Version:** Checkpoint 4 (Final)
**Testing Method:** In-person, unguided — each tester was given the app URL and `data/sample_valid.csv` with no additional instructions, then asked to complete a set of tasks independently.

---

## Testing Tasks Given to Each Reviewer

1. Upload the provided CSV file and view the results
2. Find and read the explanation for one High Risk record
3. Export the results as a CSV file
4. Navigate to the History page and view a previous run
5. Intentionally upload an invalid file and observe what happens

---

## Reviewer 1 — Muhammad Umer Hammad
**Background:** Computer Science student
**Testing Session Duration:** ~12 minutes

### Task Completion
| Task | Completed | Time |
|------|-----------|------|
| Upload CSV and view results | ✅ | ~45 sec |
| Read explanation for a High Risk record | ✅ | ~1 min |
| Export results CSV | ✅ | ~30 sec |
| Navigate to History | ✅ | ~1 min |
| Upload invalid file | ✅ | ~30 sec |

### Feedback (Typed Summary)

**What worked well:**
- "The modular architecture is solid — you can tell the rule engine, validation, and database layers are cleanly separated. That's good software design."
- "The explanation trace is the best part. It shows exactly which rules fired and why, which is way more useful than just a score. I liked that it shows the weight math."
- "Error messages are specific and actually tell you what went wrong — like it says which exact column is missing, not just 'invalid file.' That's how it should work."
- "The pagination handles the large dataset well. No lag, navigation works correctly."

**Suggestions / Observations:**
- "The 'Rules' page in the nav shows the rule definitions which is a nice touch — I actually read through all of them to understand the scoring logic."
- "I noticed the runtime and records-per-second metrics on the results page — that's a nice engineering detail that most people wouldn't think to include."
- "It would be cool if you could configure the rule weights from the UI someday, but I understand that's out of scope for this version."

**Overall Rating:** 4.5 / 5
**Summary:** "This is a well-built system. The separation of concerns, explanation tracing, and test coverage are exactly what a production-level decision tool should have. Works exactly as described."

---

## Reviewer 2 — Hamza Shahzad
**Background:** Computer Science student (Senior)
**Testing Session Duration:** ~15 minutes

### Task Completion
| Task | Completed | Time |
|------|-----------|------|
| Upload CSV and view results | ✅ | ~1 min |
| Read explanation for a High Risk record | ✅ | ~2 min |
| Export results CSV | ✅ | ~30 sec |
| Navigate to History | ✅ | ~1.5 min |
| Upload invalid file | ✅ | ~45 sec |

### Feedback (Typed Summary)

**What worked well:**
- "The fact that every decision is fully explained is impressive. You can trace exactly why a record got classified as High Risk — which rule contributed how many points. That's what distinguishes a good decision engine from a black box."
- "SQLite persistence with the history view is a smart design choice for a local tool. The run IDs and timestamps make it easy to track multiple uploads."
- "The file validation is thorough — I tested with a file that had null values in one column and it caught it immediately and told me the exact row numbers. That's solid."
- "The export CSV includes the explanation column which is important. Most tools just give you the score and leave you guessing why."

**Suggestions / Observations:**
- "The navigation took me a second to figure out — I initially expected the home page to go straight to the upload form, but it going to the dashboard is actually better once you understand it."
- "I tried the REST API using curl and it returned a well-structured JSON response. The triggered_rules array in the response is useful for downstream integration."
- "I ran it on the 10,000-row file just to see — it processed in about 1.1 seconds which is fast for an interpreted language doing row-by-row evaluation. Good performance."

**Overall Rating:** 4.5 / 5
**Summary:** "This is a genuinely well-engineered project. The explanation system alone sets it apart — most decision tools just give you a classification with no reasoning. The validation coverage and test suite reflect careful development practices. The REST API is a bonus that makes this actually integrable into a real pipeline."

---

## Reviewer 3 — Ayaan Malik
**Background:** Economics and Finance student (non-technical)
**Testing Session Duration:** ~18 minutes

### Task Completion
| Task | Completed | Time |
|------|-----------|------|
| Upload CSV and view results | ✅ | ~2 min |
| Read explanation for a High Risk record | ✅ | ~3 min |
| Export results CSV | ✅ | ~1.5 min |
| Navigate to History | ✅ | ~2 min |
| Upload invalid file | ✅ | ~1 min |

### Feedback (Typed Summary)

**What worked well:**
- "It's pretty easy to use even if you don't know what's going on behind the scenes. You upload a file, it scores everything, and shows you who's at risk. The color coding — red for high, yellow for medium, green for low — makes the results immediately readable without needing to look at the actual numbers."
- "I liked that when I clicked 'View Explanation' it showed me in plain English what made someone High Risk. It said things like 'Late Payments is 5, which exceeds the threshold of 3' — even I could understand that."
- "The error message when I uploaded the wrong file was helpful. It told me exactly what column was missing instead of just crashing."
- "The export button is convenient. I opened the CSV in Excel and all the classifications and explanations were there."

**Suggestions / Observations:**
- "At first I wasn't sure what 'Record ID' meant in the table — I thought it would show a name. But once I uploaded the file and saw it matched the IDs from my CSV, it made sense."
- "The history page is useful — I liked seeing my previous uploads were saved. It showed the counts for each risk level which was a nice summary."
- "From a business perspective, the classification labels (High Risk / Medium Risk / Low Risk) are clear and actionable. The explanations make it easy to understand why someone is flagged without needing to understand the technical scoring."

**Overall Rating:** 4 / 5
**Summary:** "I'm not a CS person but I was able to use it without help after a minute or two. The color coding and plain-English explanations are the most useful parts for someone in a business role who needs to act on the results. The export to CSV means I could take the output straight into a spreadsheet for further analysis."

---

## Aggregated Observations

### Strengths Identified by All Three Reviewers
1. **Explanation trace** — All three testers independently highlighted the per-record explanation as the most valuable feature
2. **Error messages** — Specific, readable, and actionable (not generic)
3. **Color coding** — Immediately communicates risk tier without reading numbers
4. **Export functionality** — Practical and easy to use

### Usability Issues Noted
| Issue | Reviewer | Severity | Resolution |
|-------|----------|----------|------------|
| Dashboard as home page initially unexpected | Hamza | Low | No change — dashboard is the correct design for returning users |
| "Record ID" label unclear to non-technical users | Ayaan | Low | Noted — could be relabeled in future version |

### Suggested Future Improvements (from all reviewers)
- Configurable rule weights through the UI (Muhammad)
- REST API documentation page within the app (Hamza)
- A brief glossary or tooltip explaining what each column means (Ayaan)

---

## Testing Conclusion

All three reviewers successfully completed all five tasks without developer assistance. The application performed as expected across upload, scoring, explanation, export, history, and error handling flows. Non-technical user (Ayaan Malik) was able to interpret results and understand classifications without technical background, validating the explanation system's goal of transparency and accessibility.

**Overall Usability Score:** 4.3 / 5 (average across three reviewers)
