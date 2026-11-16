"""Create privacy-safe aggregate CSVs for the Power BI dashboard."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "Resume.csv"
METRICS = ROOT / "reports" / "category-classification-metrics.json"
OUTPUT = ROOT / "dashboard" / "data"


def main() -> None:
    if not RAW.exists() or not METRICS.exists():
        raise SystemExit("Run the EDA and category evaluation scripts before exporting dashboard data.")
    OUTPUT.mkdir(parents=True, exist_ok=True)
    data = pd.read_csv(RAW, usecols=["Resume_str", "Category"]).dropna()
    text = data["Resume_str"].astype(str).str.replace(r"\s+", " ", regex=True).str.strip()
    data = data[text.str.len() > 0]
    metrics = json.loads(METRICS.read_text(encoding="utf-8"))
    performance = pd.DataFrame.from_dict(metrics["per_category"], orient="index").rename_axis("category").reset_index()
    counts = data["Category"].value_counts().rename_axis("category").reset_index(name="resume_count")
    counts.merge(performance, on="category", how="left").sort_values("resume_count", ascending=False).to_csv(OUTPUT / "category-performance.csv", index=False)
    pd.DataFrame([
        {"metric": "Accuracy", "value": metrics["accuracy"]},
        {"metric": "Macro precision", "value": metrics["macro_precision"]},
        {"metric": "Macro recall", "value": metrics["macro_recall"]},
        {"metric": "Macro F1", "value": metrics["macro_f1"]},
        {"metric": "Weighted F1", "value": metrics["weighted_f1"]},
        {"metric": "Training records", "value": metrics["train_records"]},
        {"metric": "Held-out test records", "value": metrics["test_records"]},
        {"metric": "Role categories", "value": len(metrics["per_category"])},
    ]).to_csv(OUTPUT / "evaluation-summary.csv", index=False)
    print(f"Wrote dashboard data to {OUTPUT}")


if __name__ == "__main__":
    main()
