# Evaluation Report: Skill Tagging Model Audit

**insiderOne AI/ML Internship Work Sample**

## Methodology

**Data:** 50 synthetic job descriptions (JD001–JD050) with model-generated skill tags, evaluated against a fixed approved skill vocabulary of 54 skills.

**Labeling rules:**
- **Correct:** A model tag maps to an approved skill (exact match or synonym) AND that skill appears in the JD description text.
- **Wrong:** A model tag is not in the approved skill list, OR maps to an approved skill that does NOT appear in the JD text.
- **Missing:** An approved skill appears in the JD text but the model did not tag it.

**Synonyms handled:** Node→Node.js, JS→JavaScript, Excel→Microsoft Excel, Postgres→PostgreSQL, API→REST APIs, ML→Machine Learning, Financial Modeling→Financial Modelling, Social Media→Social Media Marketing.

**Nice-to-have skills:** Counted as present if mentioned in the JD text (e.g., "Data Cleaning is a plus, not a must" still counts Data Cleaning as present).

## Results

| Metric | Calculation | Value |
|--------|-------------|-------|
| Total model tags assessed | 200 | |
| Correct tags | 172 | |
| Wrong tags | 28 | |
| Missing skills | 58 | |
| **Precision** | 172 / 200 | **86.0%** |
| **Recall** | 172 / 230 | **74.8%** |
| **F1 Score** | Harmonic mean | **80.0%** |

The model is reasonably precise (86% of assigned tags are valid) but misses about a quarter of real skills (recall 74.8%).

### Optional Skills in Metrics

Of the 58 missing skills, 39 appear in the JD text in an optional context (e.g., "plus, not a must", "nice to have", "bonus if"). These are counted as misses for recall purposes because the model failed to tag a skill that appears in the description, regardless of whether the JD framed it as required or optional.

**Rationale:** At prediction time, the model only sees the job description text — it cannot know which skills are framed as optional vs. required. The evaluation therefore treats all mentioned skills equally: if a skill appears in the text and the model didn't tag it, it's a miss. This is a conservative standard that favors higher recall expectations.

### Broad Synonym Mappings (Documented)

Two synonym mappings are broader than the canonical skill:

| Model Tag | Canonical Skill | Usage |
|---|---|---|
| API | REST APIs | JD023 — "REST APIs" appears in JD text |
| Social Media | Social Media Marketing | JD045 — "Social Media Marketing" appears in JD text |

These are documented as broad mappings because the source term is more general than the canonical skill. In both cases, the canonical skill text was verified to appear in the JD description before labeling as Correct. Both usages produced correct labels.


## Three Failure Patterns

### Pattern 1 — Soft-skill hallucination (16 tags)
The model tags skills not in the approved list at all, mostly generic soft skills.

| jd_id | Wrong tag |
|-------|-----------|
| JD001 | Teamwork |
| JD003 | Leadership |
| JD008 | Time Management |
| JD013 | Problem Solving |
| JD023 | Communication |

### Pattern 2 — Ghost skills (12 tags)
The model assigns an approved skill that is not mentioned anywhere in the JD text.

| jd_id | Wrong tag |
|-------|-----------|
| JD004 | SAP |
| JD005 | Machine Learning |
| JD007 | Kubernetes |
| JD012 | Kubernetes |
| JD018 | Blockchain |
| JD040 | SAP |
| JD047 | SAP |

### Pattern 3 — Missing required skills (58 tags)
Real skills appearing in the description go untagged. Most frequently missed: Research (4×), Microsoft Excel (4×), HTML (3×), GST (3×).

| jd_id | Missing skills |
|-------|----------------|
| JD001 | Data Cleaning |
| JD002 | HTML, React |
| JD003 | Git, Python |
| JD006 | Prototyping, Research |
| JD008 | Machine Learning, Pandas |

## Proposed Fix

**Change:** Restrict the model's output vocabulary to the 54-skill approved list, and add a post-processing filter that removes any tag whose skill term cannot be found verbatim (or as a known synonym) in the JD text.

**Why:** This directly eliminates Pattern 1 (non-list tags) and Pattern 2 (ghost skills), which account for all 28 wrong tags. Precision should rise toward 100% without harming recall.

**How to verify:** Re-run this same evaluation after the fix. Confirm wrong tags drop toward zero and precision improves, while recall remains stable.

## Deliverables

- `outputs/labels/tag_labels.csv` — Full label file (258 rows, includes `optional` column for Missing labels)
- `outputs/metrics/metrics.csv` — Precision, recall, F1 with counts
- `outputs/analysis/failure_patterns.md` — Three patterns with jd_ids
- `main.py` — Reproducible evaluation script
- `reports/annotation_methodology.md` — Detailed annotation rules

## AI Assistance Disclosure

This evaluation was developed with help from OpenCode (Nemotron model). OpenCode assisted by writing the evaluation Python scripts, computing metrics, designing the annotation rules, and drafting this report. I reviewed every label, verified all calculations with an independent re-run, spot-checked failure examples against the original JD descriptions, and made the final methodology decisions.
