# Skill Tag Evaluation: Annotation Methodology

## 1. Objective

Evaluate the quality of model-generated skill tags across all 50 job descriptions using the approved skill vocabulary. Determine how often model tags are correct, wrong, or missing.

---

## 2. Annotation Rules (The Check)

### Approved Vocabulary (Canonical Skill List)

Only the **54 skills** in `skill-list.csv` are considered valid canonical skills. Any model tag that does not map to one of these 54 skills is automatically wrong.

The 54 skills are:
AWS, Accounting, Blockchain, C++, CSS, Canva, Content Writing, Copy Editing, Copywriting, Customer Support, Data Cleaning, Design Systems, Docker, Email Marketing, Figma, Financial Modelling, GST, Git, Google Analytics, HR Operations, HTML, Interviewing, Java, JavaScript, Jira, Kubernetes, Looker, Machine Learning, Microsoft Excel, Node.js, Pandas, PostgreSQL, Power BI, Prototyping, PyTorch, Python, R, REST APIs, React, Recruiting, Research, SAP, SEO, SQL, Social Media Marketing, Statistics, Tableau, Tally, TypeScript, User Research, Wireframing, WordPress, Written English, Zendesk.

---

### Rule A: Correct Tag (True Positive)

A model tag is **Correct** if BOTH conditions are met:

1. The tag maps to an approved canonical skill (via exact match or an approved synonym).
2. That canonical skill is explicitly mentioned in the job description text.

**Examples:**
- JD001: Model tag "Python" → canonical "Python" → JD says "knows Python" → **Correct**
- JD003: Model tag "Node" → synonym → canonical "Node.js" → JD says "Node.js" → **Correct**
- JD002: Model tag "CSS" → canonical "CSS" → JD says "CSS" → **Correct**

---

### Rule B: Wrong Tag (False Positive)

A model tag is **Wrong** if EITHER condition is met:

1. The tag does NOT map to any approved canonical skill (not in skill-list.csv and not an approved synonym).
2. The tag maps to an approved canonical skill, but that skill is NOT mentioned in the JD text.

**Examples:**
- JD001: Model tag "Teamwork" → not in skill list → **Wrong**
- JD004: Model tag "SAP" → canonical "SAP" → JD does not mention SAP → **Wrong**
- JD007: Model tag "Kubernetes" → canonical "Kubernetes" → JD does not mention Kubernetes → **Wrong**

---

### Rule C: Missed Skill (False Negative)

A **Missed Skill** is an approved canonical skill that:

1. Is explicitly mentioned in the JD description text, AND
2. Is NOT included in the model's predicted tags for that JD.

**Examples:**
- JD001: JD says "Data Cleaning" → model did not tag "Data Cleaning" → **Missed**
- JD002: JD says "HTML" → model did not tag "HTML" → **Missed**
- JD003: JD says "Git" → model did not tag "Git" → **Missed**

---

### Rule D: Synonym Handling

Model tags that are variant spellings, abbreviations, or alternative names for an approved skill are mapped to that canonical skill **before** applying Rules A–C.

**Approved Synonym Map:**

| Model Tag Variant | Canonical Skill |
|---|---|
| Node | Node.js |
| Node.js | Node.js |
| JS | JavaScript |
| JavaScript | JavaScript |
| Excel | Microsoft Excel |
| Microsoft Excel | Microsoft Excel |
| Postgres | PostgreSQL |
| PostgreSQL | PostgreSQL |
| API | REST APIs |
| APIs | REST APIs |
| Rest API | REST APIs |
| Rest APIs | REST APIs |
| ML | Machine Learning |
| Machine Learning | Machine Learning |
| Financial Modeling | Financial Modelling |
| Financial Modelling | Financial Modelling |
| Social Media | Social Media Marketing |
| Social Media Marketing | Social Media Marketing |

**Rule:** If a model tag matches a synonym, treat it as the canonical skill for all subsequent checks. Related but distinct skills (e.g., "Java" vs. "JavaScript") are NOT synonyms.

**Broad Synonyms (documented for transparency):**

Two synonym mappings are broader than the canonical skill:

| Model Tag | Canonical Skill | Assessment |
|---|---|---|
| API | REST APIs | "API" is a general term that could include GraphAPI, SOAP, etc. Mapped to REST APIs only when "REST API" or "REST APIs" appears in the JD text. Used in JD023. |
| Social Media | Social Media Marketing | "Social Media" could mean social media management or advertising, not just marketing. Mapped to Social Media Marketing only when that phrase appears in the JD text. Used in JD045. |

These are documented as broad mappings because the source term is more general than the canonical skill. In both cases, the canonical skill text was verified to appear in the JD description before labeling as Correct.

---

### Rule E: Nice-to-Have vs. Required Skills

Both mandatory ("required", "must have") and optional ("nice to have", "bonus", "plus") skills mentioned in the JD text are treated as **present in the JD**.

**Rationale:** The model's job is to identify all skills relevant to the role, whether required or optional. An optional skill that appears in the JD is still a skill the role uses.

**Optional classification in output:** Each Missing label includes an `optional` column:
- `yes`: The skill appears in the JD text in an optional context (e.g., "plus, not a must", "nice to have", "bonus if")
- `no`: The skill appears in the JD text as a required skill
- `—`: Not applicable (for Correct and Wrong labels)

**Metric impact:** Optional misses are counted the same as mandatory misses for precision, recall, and F1 calculations. The model is evaluated on whether it tagged **any** skill mentioned in the JD, regardless of whether the JD framed it as optional or required. This is because the model cannot know at prediction time which skills are optional vs. required — it only sees the job description text.

**Examples:**
- JD001: "Data Cleaning is a plus, not a must" → Data Cleaning is present → if model tagged it: Correct; if not: Missing (optional=yes).
- JD002: "Nice to have: HTML" → HTML is present → if model tagged it: Correct; if not: Missing (optional=yes).

---

### Rule F: Multi-Word and Case-Insensitive Matching

- Skill matching is **case-insensitive** ("python", "Python", "PYTHON" all match canonical "Python").
- Multi-word skills (e.g., "Microsoft Excel", "Social Media Marketing") must appear as a phrase in the JD text.
- Single-word skills use word-boundary matching to avoid false matches (e.g., "Java" does not match "JavaScript").

---

### Rule G: Label Output Format

For each model tag and each missed skill, produce one row:

| Column | Description |
|---|---|
| `jd_id` | Job description identifier |
| `tag` | The model tag or missed skill name |
| `status` | `Correct`, `Wrong`, or `Missing` |
| `matched_skill` | The canonical skill name (or "—" if not applicable) |
| `reason` | Short explanation of the decision |
| `optional` | `yes`/`no` for Missing labels; `—` for Correct/Wrong |

---

## 3. Evaluation Scope

- **Dataset:** All 50 supplied job descriptions (`job-descriptions-tagged.csv`)
- **Predictions:** `model_tags` column (semicolon-separated)
- **Ground truth:** The job description `description` column text
- **Annotation unit:** Individual job description × canonical skill
- **Approved vocabulary:** 54 skills from `skill-list.csv`

---

## 4. Evaluation Metrics

- **Precision** = Correct tags / Total model tags assessed
- **Recall** = Correct tags / (Correct tags + Missing skills)
- **F1 Score** = 2 × (Precision × Recall) / (Precision + Recall)

All counts are reported as raw numbers alongside percentages.

---

## 5. Error Analysis

After labeling all 50 JDs, group all Wrong and Missing labels into **three recurring patterns**. Each pattern must include 2–3 concrete examples identified by `jd_id`.

---

## 6. Proposed Improvement

After identifying the dominant error pattern, propose **one** code or process change, explain why it addresses the pattern, and describe how to verify it improved the metrics (re-run the same evaluation and compare before/after).

---

## 7. Deliverables

1. `outputs/labels/tag_labels.csv` — One row per tag/skill per JD (Correct/Wrong/Missing)
2. `outputs/metrics/metrics.csv` — Precision, recall, F1 with raw counts
3. `outputs/analysis/failure_patterns.md` — Three patterns with jd_id examples
4. `evaluation_report.md` — One-page write-up (methodology, metrics, failures, fix)
5. `main.py` — Reproducible Python script that generates all of the above

---

## 8. AI Assistance Disclosure

This methodology and the evaluation scripts were developed with help from OpenCode (Nemotron model). I reviewed every rule, verified calculations with an independent re-run, and made the final decisions on synonym mapping, nice-to-have handling, and failure pattern grouping.
