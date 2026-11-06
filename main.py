"""
main.py — Skill Tag Evaluation Script
insiderOne AI/ML Internship Work Sample

Reads the 50 job descriptions with model-generated tags, applies the
annotation rules from reports/annotation_methodology.md, and writes:
  outputs/labels/tag_labels.csv
  outputs/metrics/metrics.csv
  outputs/analysis/failure_patterns.md

Run: python main.py
"""

import csv
import re
import os
from collections import defaultdict, Counter

# ---------------------------------------------------------------------------
# Paths (relative to this script's location)
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DATA_DIR = os.path.join(BASE_DIR, "data", "raw")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
LABELS_DIR = os.path.join(OUTPUT_DIR, "labels")
METRICS_DIR = os.path.join(OUTPUT_DIR, "metrics")
ANALYSIS_DIR = os.path.join(OUTPUT_DIR, "analysis")

JD_FILE = os.path.join(RAW_DATA_DIR, "job-descriptions-tagged.csv")
SKILL_FILE = os.path.join(RAW_DATA_DIR, "skill-list.csv")

LABELS_OUT = os.path.join(LABELS_DIR, "tag_labels.csv")
METRICS_OUT = os.path.join(METRICS_DIR, "metrics.csv")
PATTERNS_OUT = os.path.join(ANALYSIS_DIR, "failure_patterns.md")


# ---------------------------------------------------------------------------
# Load approved skill list
# ---------------------------------------------------------------------------
def load_skills(path):
    skills = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            skill = row["skill"].strip()
            if skill:
                skills.append(skill)
    return skills


SKILL_LIST = load_skills(SKILL_FILE)
SKILL_SET_LOWER = set(s.lower() for s in SKILL_LIST)
SKILL_TO_ORIGINAL = {s.lower(): s for s in SKILL_LIST}


# ---------------------------------------------------------------------------
# Synonym map: model tag variant -> canonical skill
# ---------------------------------------------------------------------------
SYNONYM_MAP = {
    "node": "Node.js", "node.js": "Node.js",
    "js": "JavaScript", "javascript": "JavaScript",
    "excel": "Microsoft Excel", "microsoft excel": "Microsoft Excel",
    "postgres": "PostgreSQL", "postgresql": "PostgreSQL",
    "api": "REST APIs", "apis": "REST APIs", "rest api": "REST APIs", "rest apis": "REST APIs",
    "ml": "Machine Learning", "machine learning": "Machine Learning",
    "financial modeling": "Financial Modelling", "financial modelling": "Financial Modelling",
    "social media": "Social Media Marketing", "social media marketing": "Social Media Marketing",
}

# Broad synonyms: mapped term is a superset of the canonical skill.
# Used only where the canonical skill text actually appears in the JD.
BROAD_SYNONYMS = {
    "api": "REST APIs",
    "social media": "Social Media Marketing",
}

# Patterns that indicate a skill is optional (nice-to-have) in the JD text.
OPTIONAL_PATTERNS = [
    "plus, not a must",
    "nice to have",
    "bonus if",
    "optional",
    "not required",
]


def norm(s):
    return s.strip().lower()


def map_tag(tag):
    """
    Rule D: Map a model tag to a canonical skill via exact match or synonym.
    Returns (canonical_skill, via) or (None, None).
    """
    t = norm(tag)
    if t in SKILL_SET_LOWER:
        return SKILL_TO_ORIGINAL[t], "exact"
    if t in SYNONYM_MAP:
        return SYNONYM_MAP[t], "synonym"
    return None, None


def skill_mentioned(skill, text):
    """
    Rule F: Check if a skill is explicitly mentioned in the JD text.
    Case-insensitive. Multi-word = phrase match. Single-word = word boundary.
    """
    tl = text.lower()
    sl = skill.lower()

    if " " in sl:
        return sl in tl

    pattern = r"\b" + re.escape(sl) + r"\b"
    return bool(re.search(pattern, tl))


def is_optional_mention(skill, text):
    """
    Check if a skill mention in the JD text is framed as optional
    (nice-to-have, bonus, plus, not required).
    Returns True if the skill appears in an optional context.
    """
    tl = text.lower()
    sl = skill.lower()

    # Find all occurrences of the skill in the text
    for m in re.finditer(re.escape(sl), tl):
        start = max(0, m.start() - 80)
        end = min(len(tl), m.end() + 40)
        context = tl[start:end]
        if any(p in context for p in OPTIONAL_PATTERNS):
            return True
    return False


# ---------------------------------------------------------------------------
# Load job descriptions
# ---------------------------------------------------------------------------
def load_jds(path):
    jds = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            jds.append(row)
    return jds


# ---------------------------------------------------------------------------
# Evaluate a single JD
# ---------------------------------------------------------------------------
def evaluate_jd(jd):
    """
    Apply Rules A–E to one job description.
    Returns a list of label dicts.
    """
    jid = jd["jd_id"]
    text = jd["description"]
    raw_tags = [t.strip() for t in jd.get("model_tags", "").split(";") if t.strip()]

    labels = []
    model_covered_skills = set()

    # ---- Evaluate each model tag (Rules A & B) ----
    for tag in raw_tags:
        skill, via = map_tag(tag)

        # Rule B1: Tag not in approved skill list
        if skill is None:
            labels.append({
                "jd_id": jid,
                "tag": tag,
                "status": "Wrong",
                "matched_skill": "—",
                "reason": "Tag not in approved skill list",
                "optional": "—",
            })
            continue

        model_covered_skills.add(skill)

        # Rule A: Tag maps to approved skill AND skill mentioned in JD
        if skill_mentioned(skill, text):
            labels.append({
                "jd_id": jid,
                "tag": tag,
                "status": "Correct",
                "matched_skill": skill,
                "reason": f"Matched via {via}",
                "optional": "—",
            })
        else:
            # Rule B2: Approved skill but not in JD text
            labels.append({
                "jd_id": jid,
                "tag": tag,
                "status": "Wrong",
                "matched_skill": skill,
                "reason": f"Matched via {via} but skill not mentioned in JD text",
                "optional": "—",
            })

    # ---- Find missing skills (Rule C) ----
    for skill in SKILL_LIST:
        if skill_mentioned(skill, text) and skill not in model_covered_skills:
            optional = "yes" if is_optional_mention(skill, text) else "no"
            labels.append({
                "jd_id": jid,
                "tag": skill,
                "status": "Missing",
                "matched_skill": skill,
                "reason": "Skill in JD but not tagged by model",
                "optional": optional,
            })

    return labels


# ---------------------------------------------------------------------------
# Group failures into patterns
# ---------------------------------------------------------------------------
def group_patterns(labels):
    pattern1 = [l for l in labels
                if l["status"] == "Wrong" and l["matched_skill"] == "—"]
    pattern2 = [l for l in labels
                if l["status"] == "Wrong" and l["matched_skill"] != "—"]
    pattern3 = [l for l in labels if l["status"] == "Missing"]
    return pattern1, pattern2, pattern3


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    # Create output directories
    for d in [LABELS_DIR, METRICS_DIR, ANALYSIS_DIR]:
        os.makedirs(d, exist_ok=True)

    # Load data
    jds = load_jds(JD_FILE)

    # Evaluate all JDs
    all_labels = []
    for jd in jds:
        all_labels.extend(evaluate_jd(jd))

    # ---- Write labels ----
    with open(LABELS_OUT, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "jd_id", "tag", "status", "matched_skill", "reason", "optional"
        ])
        writer.writeheader()
        writer.writerows(all_labels)

    # ---- Compute metrics ----
    total_model_tags = sum(1 for l in all_labels
                           if l["status"] in ("Correct", "Wrong"))
    correct_tags = sum(1 for l in all_labels if l["status"] == "Correct")
    wrong_tags = sum(1 for l in all_labels if l["status"] == "Wrong")
    missing_tags = sum(1 for l in all_labels if l["status"] == "Missing")
    missing_optional = sum(1 for l in all_labels
                           if l["status"] == "Missing" and l["optional"] == "yes")
    missing_mandatory = sum(1 for l in all_labels
                            if l["status"] == "Missing" and l["optional"] == "no")

    precision = correct_tags / total_model_tags if total_model_tags else 0.0
    recall = correct_tags / (correct_tags + missing_tags) \
        if (correct_tags + missing_tags) else 0.0
    f1 = (2 * precision * recall / (precision + recall)
          if (precision + recall) else 0.0)

    with open(METRICS_OUT, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["metric", "value", "count", "total"])
        writer.writerow(["precision", f"{precision*100:.1f}%",
                         correct_tags, total_model_tags])
        writer.writerow(["recall", f"{recall*100:.1f}%",
                         correct_tags, correct_tags + missing_tags])
        writer.writerow(["f1_score", f"{f1*100:.1f}%", "", ""])
        writer.writerow(["correct_tags", str(correct_tags), "", ""])
        writer.writerow(["wrong_tags", str(wrong_tags), "", ""])
        writer.writerow(["missing_tags", str(missing_tags), "", ""])
        writer.writerow(["missing_optional", str(missing_optional), "", ""])
        writer.writerow(["missing_mandatory", str(missing_mandatory), "", ""])

    # ---- Group failure patterns ----
    pattern1, pattern2, pattern3 = group_patterns(all_labels)

    with open(PATTERNS_OUT, "w", encoding="utf-8") as f:
        f.write("# Failure Pattern Analysis\n\n")

        f.write("## Pattern 1: Tags not in approved skill list\n\n")
        f.write(f"Count: {len(pattern1)}\n\n")
        f.write("The model assigns tags that are not in the 54-skill approved "
                "vocabulary — mostly generic soft skills.\n\n")
        for l in pattern1[:6]:
            f.write(f"- **{l['jd_id']}**: tag='{l['tag']}'\n")
        f.write("\nUnique offending tags: ")
        f.write(", ".join(sorted(set(l["tag"] for l in pattern1))))
        f.write("\n\n")

        f.write("## Pattern 2: Approved skill tagged but not in JD text\n\n")
        f.write(f"Count: {len(pattern2)}\n\n")
        f.write("The model assigns an approved skill that is not mentioned "
                "anywhere in the job description.\n\n")
        for l in pattern2[:6]:
            f.write(f"- **{l['jd_id']}**: tag='{l['tag']}' "
                    f"-> skill='{l['matched_skill']}'\n")
        f.write("\nUnique skills wrongly tagged: ")
        f.write(", ".join(sorted(set(l["matched_skill"] for l in pattern2))))
        f.write("\n\n")

        f.write("## Pattern 3: Skills in JD but not tagged (missing)\n\n")
        f.write(f"Count: {len(pattern3)}\n\n")
        f.write("Real skills appearing in the description go untagged by "
                "the model.\n\n")
        for l in pattern3[:10]:
            opt = f" (optional)" if l["optional"] == "yes" else ""
            f.write(f"- **{l['jd_id']}**: '{l['tag']}'{opt}\n")

        # Most frequently missed
        missing_counts = Counter(l["tag"] for l in pattern3)
        f.write("\nMost frequently missed skills:\n")
        for skill, count in missing_counts.most_common(8):
            f.write(f"- {skill}: {count} time(s)\n")

    # ---- Print summary ----
    print("=" * 60)
    print("EVALUATION COMPLETE")
    print("=" * 60)
    print(f"JDs evaluated: {len(jds)}")
    print(f"Model tags assessed: {total_model_tags}")
    print(f"  Correct: {correct_tags}  ({correct_tags/total_model_tags*100:.1f}%)")
    print(f"  Wrong:   {wrong_tags}  ({wrong_tags/total_model_tags*100:.1f}%)")
    print(f"Missing skills: {missing_tags}")
    print(f"  Mandatory: {missing_mandatory}")
    print(f"  Optional:  {missing_optional}")
    print(f"\nPrecision: {precision*100:.1f}%")
    print(f"Recall:    {recall*100:.1f}%")
    print(f"F1 Score:  {f1*100:.1f}%")
    print(f"\nOutputs written:")
    print(f"  {LABELS_OUT}")
    print(f"  {METRICS_OUT}")
    print(f"  {PATTERNS_OUT}")


if __name__ == "__main__":
    main()
