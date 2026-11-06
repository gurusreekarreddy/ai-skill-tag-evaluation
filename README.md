# ML Skill Tag Evaluation — insiderOne AI/ML Internship Work Sample

Evaluates the accuracy of an AI model's skill-tag predictions across 50 job descriptions, using an approved skill vocabulary of 54 skills.

## Project Structure

```
ml-skill-tag-evaluation/
├── data/
│   ├── raw/
│   │   ├── job-descriptions-tagged.csv   # 50 JDs with model tags
│   │   └── skill-list.csv                 # 55 approved canonical skills
│   └── processed/                         # (reserved)
├── outputs/
│   ├── labels/
│   │   └── tag_labels.csv                 # 258 labels: correct/wrong/missing
│   ├── metrics/
│   │   └── metrics.csv                    # Precision, recall, F1 with counts
│   └── analysis/
│       └── failure_patterns.md            # 3 failure patterns with jd_ids
├── reports/
│   └── annotation_methodology.md          # Full annotation rules
├── evaluation_report.md                   # One-page write-up (this deliverable)
├── main.py                                # Reproducible evaluation script
├── requirements.txt                       # Python dependencies
└── .gitignore                             # Python/macOS exclusions
```

## How to Run

### Prerequisites
- Python 3.9+
- pandas (optional, for viewing outputs)

### Execute
```bash
cd ml-skill-tag-evaluation/
python main.py
```

This reads `data/raw/job-descriptions-tagged.csv` and `data/raw/skill-list.csv`, applies the annotation rules, and writes all outputs.

## Outputs

| File | Description |
|------|-------------|
| `outputs/labels/tag_labels.csv` | One row per tag/skill per JD: jd_id, tag, status (Correct/Wrong/Missing), matched_skill, reason |
| `outputs/metrics/metrics.csv` | Precision, recall, F1 score with raw counts |
| `outputs/analysis/failure_patterns.md` | Three recurring error patterns with jd_id examples |

## Key Results

| Metric | Value | Calculation |
|--------|-------|-------------|
| Precision | 86.0% | 172 correct / 200 total tags |
| Recall | 74.8% | 172 correct / 230 total skills present |
| F1 Score | 80.0% | Harmonic mean |

## Methodology

See `reports/annotation_methodology.md` for the complete annotation rules:
- **Correct:** Tag maps to approved skill AND skill appears in JD text
- **Wrong:** Tag not in skill list, or skill not in JD text
- **Missing:** Approved skill in JD text but not tagged by model
- **Synonyms:** 16 variants mapped (Node→Node.js, JS→JavaScript, Excel→Microsoft Excel, etc.)
- **Nice-to-have:** Optional skills still count as present in JD

## AI Assistance Disclosure

This project was developed with help from OpenCode (Nemotron model). OpenCode assisted by:
- Writing the `main.py` evaluation script
- Designing the annotation rules and synonym map
- Drafting the methodology and evaluation report

I reviewed every label, verified all calculations with an independent re-run, spot-checked failure examples against the original JD descriptions, and made the final methodology decisions.

## License

None — internal work sample for insiderOne AI/ML internship application.
