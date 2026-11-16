"""Produce privacy-preserving EDA assets from the 2022 public resume dataset.

The input CSV is intentionally ignored by Git. This script stores only aggregate
charts and summary metrics in the repository; no resume text, IDs, or contact
details are written to outputs.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data" / "raw" / "Resume.csv"
FIGURES = ROOT / "reports" / "figures"
METRICS = ROOT / "reports" / "metrics.json"

SKILLS = ("python", "sql", "java", "javascript", "aws", "excel", "project management", "salesforce")


def save_plot(name: str) -> None:
    plt.tight_layout()
    plt.savefig(FIGURES / name, dpi=180, bbox_inches="tight")
    plt.close()


def main() -> None:
    if not INPUT.exists():
        raise SystemExit("Dataset missing. Run the documented download command before EDA.")
    FIGURES.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(INPUT)
    required = {"ID", "Resume_str", "Resume_html", "Category"}
    if not required.issubset(df.columns):
        raise SystemExit(f"Unexpected columns: {list(df.columns)}")

    text = df["Resume_str"].fillna("").astype(str)
    clean = text.str.replace(r"\s+", " ", regex=True).str.strip()
    df["word_count"] = clean.str.split().str.len()
    df["char_count"] = clean.str.len()
    category_counts = df["Category"].value_counts().sort_values(ascending=True)
    duplicate_texts = int(clean.duplicated().sum())
    email_rate = float(clean.str.contains(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b", regex=True).mean())
    experience_rate = float(clean.str.contains(r"\b\d{1,2}\+?\s*(?:years?|yrs?)\b", case=False, regex=True).mean())

    plt.figure(figsize=(9, 8))
    category_counts.plot(kind="barh", color="#2f6f9f")
    plt.title("Resume count by labeled job category")
    plt.xlabel("Number of resumes")
    plt.ylabel("")
    save_plot("category-distribution.png")

    plt.figure(figsize=(9, 5))
    plt.hist(df["word_count"], bins=40, color="#4f8a8b", edgecolor="white")
    plt.axvline(df["word_count"].median(), color="#c44536", linewidth=2, label=f"Median: {df['word_count'].median():.0f} words")
    plt.title("Distribution of resume text length")
    plt.xlabel("Words per resume")
    plt.ylabel("Number of resumes")
    plt.legend()
    save_plot("resume-length-distribution.png")

    skill_rates = {skill: float(clean.str.contains(rf"\b{re.escape(skill)}\b", case=False, regex=True).mean()) * 100 for skill in SKILLS}
    ordered_skills = dict(sorted(skill_rates.items(), key=lambda item: item[1]))
    plt.figure(figsize=(9, 5))
    plt.barh(list(ordered_skills), list(ordered_skills.values()), color="#7a5c9e")
    plt.title("Keyword signal prevalence across resumes")
    plt.xlabel("Resumes containing keyword (%)")
    plt.xlim(0, 100)
    for index, value in enumerate(ordered_skills.values()):
        plt.text(value + 1, index, f"{value:.1f}%", va="center")
    save_plot("skill-signal-prevalence.png")

    quality = pd.Series({
        "Missing resume text": float((clean == "").mean()) * 100,
        "Missing category": float(df["Category"].isna().mean()) * 100,
        "Exact duplicate text": duplicate_texts / len(df) * 100,
        "Email present": email_rate * 100,
        "Experience pattern present": experience_rate * 100,
    }).sort_values()
    plt.figure(figsize=(9, 5))
    colors = ["#c44536" if value > 0 and "Missing" in name else "#3b7a57" for name, value in quality.items()]
    plt.barh(quality.index, quality.values, color=colors)
    plt.title("Data quality and extractable-signal checks")
    plt.xlabel("Share of records (%)")
    plt.xlim(0, 100)
    for index, value in enumerate(quality.values):
        plt.text(value + 1, index, f"{value:.1f}%", va="center")
    save_plot("data-quality-signals.png")

    metrics = {
        "dataset": "Bhawal (2022) Resume Dataset via Hugging Face mirror",
        "source_url": "https://www.kaggle.com/datasets/snehaanbhawal/resume-dataset",
        "source_mirror": "https://huggingface.co/datasets/Divyaamith/Kaggle-Resume",
        "records": int(len(df)),
        "categories": int(df["Category"].nunique()),
        "category_counts": {str(k): int(v) for k, v in df["Category"].value_counts().sort_index().items()},
        "missing_resume_text_pct": round(float((clean == "").mean()) * 100, 2),
        "missing_category_pct": round(float(df["Category"].isna().mean()) * 100, 2),
        "exact_duplicate_texts": duplicate_texts,
        "median_word_count": round(float(df["word_count"].median()), 1),
        "p95_word_count": round(float(df["word_count"].quantile(0.95)), 1),
        "email_present_pct": round(email_rate * 100, 2),
        "experience_pattern_present_pct": round(experience_rate * 100, 2),
        "keyword_prevalence_pct": {key: round(value, 2) for key, value in skill_rates.items()},
    }
    METRICS.parent.mkdir(exist_ok=True)
    METRICS.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
