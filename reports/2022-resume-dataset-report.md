# Resume Screening Automation: 2022 Dataset EDA Report

## Purpose and data governance

This report evaluates the project’s data pipeline using the public **Resume Dataset** published by Snehaan Bhawal (2022). The dataset contains resume examples originally scraped from LiveCareer and is distributed with text, HTML, an ID, and a job-category label. This repository uses it for aggregate exploratory analysis only; it does **not** commit raw resumes, IDs, HTML, email addresses, or PDFs.

Source: [Kaggle dataset](https://www.kaggle.com/datasets/snehaanbhawal/resume-dataset) · [Hugging Face CSV mirror](https://huggingface.co/datasets/Divyaamith/Kaggle-Resume)

## Reproducibility

```powershell
New-Item -ItemType Directory -Force data\raw | Out-Null
curl.exe -L --fail --output data\raw\Resume.csv "https://huggingface.co/datasets/Divyaamith/Kaggle-Resume/resolve/main/Resume.csv?download=true"
python -m pip install -r requirements-eda.txt
python scripts\run_eda.py
```

`data/raw/` and `reports/metrics.json` are intentionally ignored by Git. The script emits only aggregate figures and a local metrics file.

## Dataset profile

The analysis processed **2,484 resumes** across **24 labeled job categories**. The data is imbalanced: Information Technology and Business Development have 120 resumes each, while BPO has 22 and Automobile has 36. Any category classifier or score calibration should therefore use stratified splits and report per-category results rather than only an overall metric.

![Category distribution](figures/category-distribution.png)

The median resume contains **757 words**; the 95th percentile is **1,398.7 words**. This range supports the API’s file and text-length validation, but it also means a fixed prompt/input limit could disproportionately truncate long resumes.

![Resume length distribution](figures/resume-length-distribution.png)

## Text-signal EDA

Keyword signals vary substantially. Excel appears in **38.65%** of resumes and “project management” in **22.38%**, while Python appears in **1.61%** and AWS in **0.89%**. These are corpus-wide terms, not candidate-quality labels. A single universal technical-skills threshold would be inappropriate across the dataset’s 24 occupations; job-specific criteria must drive scoring.

![Keyword signal prevalence](figures/skill-signal-prevalence.png)

Quality checks found **0.04%** missing resume text, **0%** missing category labels, and **2 exact duplicate texts**. Only **0.76%** of resumes contain an extractable email pattern, reinforcing why the API treats email as an optional flag rather than a screening requirement. An explicit years-of-experience pattern appears in **37.72%** of records, so experience should not be inferred when the format does not expose it.

![Data quality and extractable signals](figures/data-quality-signals.png)

## Findings and limitations

1. The data is suitable for text-extraction checks, category exploration, and testing that the pipeline handles varied resume formats.
2. The `Category` field is a job-domain label—not an employment outcome or ground-truth job-fit score. This dataset cannot justify claims about screening precision, recall, fairness, or employment-outcome accuracy.
3. Before deploying a recommendation threshold, obtain consented, role-specific resume–job pairs with independent human suitability labels. Evaluate precision, recall, false-positive/negative rates, calibration, and disparate impact on a held-out set.
4. The source contains potentially personal resume content. Preserve data minimization: analyze locally, retain only aggregate outputs, and never send resumes to Zapier or an LLM without a lawful basis and explicit policy.

## System architecture

```mermaid
flowchart LR
    A[Recruiter uploads PDF] --> B[Flask /screen]
    B --> C{PDF has selectable text?}
    C -- No --> D[422: OCR or text PDF requested]
    C -- Yes --> E[Extract text]
    E --> F[Rules scorer or structured LLM]
    F --> G[Structured result: score, matched skills, flags]
    G --> H[Zapier Catch Hook]
    H --> I[Recruiter workflow: Sheets, ATS, Slack]
    J[2022 public dataset] -. local aggregate EDA only .-> K[EDA report and charts]
    K -. informs .-> F
```

## Claim boundary

This project demonstrates an auditable automation workflow and real-dataset EDA. It is configured as decision support, not as an automated employment-decision system. Final workflow disposition remains with an authorized reviewer.
