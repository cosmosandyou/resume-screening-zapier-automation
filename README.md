# AI Resume Screening Automation

A Flask service that accepts a PDF resume, evaluates it against explicit job criteria, and sends the structured result to a **Zapier Catch Hook**. Zapier can then add a row in Airtable or Sheets, alert a reviewer in Slack, or create an ATS task.

The project includes reproducible, privacy-preserving EDA on the public 2022 Resume Dataset. Read the [full EDA report](reports/2022-resume-dataset-report.md) for real charts, findings, data limitations, and the system architecture.


## Architecture

```
Recruiter uploads PDF -> Flask /screen -> PDF text extraction -> screening layer -> Zapier webhook -> downstream Zap actions
                                          -> malformed / image-only / missing email are explicit outcomes
```

## What the “AI” does

The default `rules` provider is a transparent baseline: it matches stated required/preferred skills, checks for an experience signal, assigns a deterministic 0–100 score, and never makes a hiring decision.

Set `AI_PROVIDER=openai` to use an LLM with a constrained JSON-only prompt. The prompt limits the model to job-relevant evidence, forbids protected-trait inference, and returns matched/missing skills plus a short rationale. Recruiters retain final decision authority.

## Setup

1. Create a Zap with **Webhooks by Zapier → Catch Hook**, copy the hook URL, and use it as `ZAPIER_WEBHOOK_URL`.
2. `Copy-Item .env.example .env`, then add your hook URL (and `OPENAI_API_KEY` only for the LLM option).
3. `python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -r requirements.txt`
4. `flask --app app run --debug`

Try it in PowerShell:

```powershell
$requirements = '{"required_skills":["Python","Flask"],"preferred_skills":["SQL","AWS"]}'
curl.exe -X POST http://127.0.0.1:5000/screen -F "resume=@C:\path\resume.pdf" -F "candidate_name=Alex Morgan" -F "requirements=$requirements"
```

## Failure handling

| Situation | API behavior |
| --- | --- |
| No email in resume | Returns `email: null` and `flags: ["missing_email"]`; it does not silently invent contact data. |
| Image-only or empty PDF | Returns HTTP 422 with `image_only_or_empty_pdf`, asking for OCR or a text PDF. |
| Broken/non-PDF upload | Returns a clear 400/422 error. |
| Zapier unavailable | Returns HTTP 502 with the screening payload so the caller can retry without losing it. |

## Testing, evaluation, and accuracy boundaries

Run `pytest`. The test suite verifies the deterministic scoring baseline and missing-email path. The repository’s [2022 Dataset EDA Report](reports/2022-resume-dataset-report.md) analyzes 2,484 public resumes across 24 job categories, but those category labels are not hiring outcomes. Therefore, this project makes **no claim** of hiring accuracy, screening precision, recall, or fairness from that data.

To measure screening quality responsibly, collect consented, role-specific resume–job pairs with independent human suitability labels. Evaluate precision (of candidates recommended, how many reviewers judge qualified), recall (of qualified candidates, how many are recommended), false-positive/negative rates, calibration, and disparate impact on a held-out set.

## Example webhook payload

```json
{
  "event": "resume.screened",
  "candidate_name": "Alex Morgan",
  "score": 85,
  "recommendation": "interview",
  "matched_required_skills": ["Python", "Flask"],
  "missing_required_skills": [],
  "flags": ["missing_email"]
}
```

## Design principles

- **Clear integration boundary:** the Flask API owns validation, extraction, and scoring; Zapier owns downstream workflow orchestration.
- **Auditable output:** the default rules provider returns matched and missing skills, a deterministic score, and explicit flags.
- **Resilient input handling:** the service returns typed errors for missing files, unsupported formats, unreadable PDFs, image-only PDFs, and webhook delivery failures.
- **Responsible evaluation:** the public 2022 dataset supports reproducible exploratory analysis, but not claims of employment-outcome accuracy.
- **Human review:** the recommendation is decision-support output; final workflow disposition remains with an authorized reviewer.
