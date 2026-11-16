"""Evaluate a reproducible job-category classifier on the public 2022 resume dataset.

This is a role-category classification benchmark, not a hiring or job-fit model.
Only aggregate metrics and figures are retained in the repository.
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import ConfusionMatrixDisplay, accuracy_score, classification_report, precision_recall_fscore_support
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data" / "raw" / "Resume.csv"
FIGURES = ROOT / "reports" / "figures"
OUTPUT = ROOT / "reports" / "category-classification-metrics.json"
RANDOM_SEED = 42


def main() -> None:
    if not INPUT.exists():
        raise SystemExit("Dataset missing. Download Resume.csv before running this evaluation.")
    FIGURES.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(INPUT, usecols=["Resume_str", "Category"]).dropna()
    text = df["Resume_str"].astype(str).str.replace(r"\s+", " ", regex=True).str.strip()
    valid = text.str.len() > 0
    X, y = text[valid], df.loc[valid, "Category"].astype(str)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=RANDOM_SEED, stratify=y
    )
    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(lowercase=True, stop_words="english", ngram_range=(1, 2), min_df=2, max_features=15000, sublinear_tf=True)),
        ("classifier", LinearSVC(C=1.0, random_state=RANDOM_SEED)),
    ])
    pipeline.fit(X_train, y_train)
    predicted = pipeline.predict(X_test)
    labels = sorted(y.unique())
    accuracy = accuracy_score(y_test, predicted)
    macro_precision, macro_recall, macro_f1, _ = precision_recall_fscore_support(y_test, predicted, average="macro", zero_division=0)
    weighted_precision, weighted_recall, weighted_f1, _ = precision_recall_fscore_support(y_test, predicted, average="weighted", zero_division=0)
    report = classification_report(y_test, predicted, labels=labels, output_dict=True, zero_division=0)

    plt.figure(figsize=(12, 10))
    display = ConfusionMatrixDisplay.from_predictions(
        y_test, predicted, labels=labels, xticks_rotation=90, cmap="Blues", colorbar=True,
        include_values=False,
    )
    plt.setp(display.ax_.get_xticklabels(), fontsize=6)
    plt.setp(display.ax_.get_yticklabels(), fontsize=6)
    plt.title("Held-out role-category classification confusion matrix")
    plt.xlabel("Predicted category")
    plt.ylabel("True category")
    plt.tight_layout()
    plt.savefig(FIGURES / "category-confusion-matrix.png", dpi=180, bbox_inches="tight")
    plt.close()

    per_category = pd.DataFrame(report).T.loc[labels, ["precision", "recall", "f1-score", "support"]].sort_values("f1-score")
    plt.figure(figsize=(10, 8))
    plt.barh(per_category.index, per_category["f1-score"], color="#2f6f9f")
    plt.xlim(0, 1.05)
    plt.title("Held-out F1 score by role category")
    plt.xlabel("F1 score")
    for index, value in enumerate(per_category["f1-score"]):
        plt.text(value + 0.015, index, f"{value:.2f}", va="center", fontsize=8)
    plt.tight_layout()
    plt.savefig(FIGURES / "category-f1-by-class.png", dpi=180, bbox_inches="tight")
    plt.close()

    metrics = {
        "task": "24-class resume role-category classification (not hiring prediction)",
        "dataset_records_after_cleaning": int(len(X)),
        "train_records": int(len(X_train)),
        "test_records": int(len(X_test)),
        "test_fraction": 0.20,
        "random_seed": RANDOM_SEED,
        "model": "TF-IDF (unigrams and bigrams, 15,000 max features) + LinearSVC",
        "accuracy": round(float(accuracy), 4),
        "macro_precision": round(float(macro_precision), 4),
        "macro_recall": round(float(macro_recall), 4),
        "macro_f1": round(float(macro_f1), 4),
        "weighted_precision": round(float(weighted_precision), 4),
        "weighted_recall": round(float(weighted_recall), 4),
        "weighted_f1": round(float(weighted_f1), 4),
        "per_category": {
            category: {metric: round(float(value), 4) for metric, value in values.items()}
            for category, values in per_category.to_dict(orient="index").items()
        },
    }
    OUTPUT.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
