# Power BI Dashboard

This folder contains a Power BI dashboard and the privacy-safe aggregate data used to build it. No raw resumes, IDs, email addresses, or PDF files are included.

## Contents

- `Resume_Screening_Analytics.pbix`: the Power BI Desktop report with the category-performance visual and embedded aggregate tables.
- `data/category-performance.csv`: public category counts plus precision, recall, F1, and held-out support by category.
- `data/evaluation-summary.csv`: overall held-out evaluation metrics and split sizes.

The report evaluates **role-category classification**; it does not estimate hiring likelihood or job-fit.

## Data refresh

```powershell
python scripts\run_eda.py
python scripts\evaluate_category_baseline.py
python scripts\export_dashboard_data.py
```

Then refresh the two CSV queries in Power BI Desktop.
