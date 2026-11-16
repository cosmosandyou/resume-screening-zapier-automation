"""Resume screening API that delivers structured recommendations to Zapier."""
from __future__ import annotations

import io
import json
import os
from datetime import UTC, datetime
from typing import Any

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from pypdf import PdfReader

from screening import ScreeningError, screen_resume
from zapier import ZapierDeliveryError, send_to_zapier

load_dotenv()
app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024


def extract_pdf_text(file_bytes: bytes) -> str:
    """Extract selectable text; image-only PDFs return an actionable error."""
    try:
        reader = PdfReader(io.BytesIO(file_bytes))
        text = "\n".join(page.extract_text() or "" for page in reader.pages).strip()
    except Exception as exc:
        raise ScreeningError("invalid_pdf", "The uploaded file is not a readable PDF.") from exc
    if len(text) < 40:
        raise ScreeningError("image_only_or_empty_pdf", "No selectable resume text was found. Ask for a text-based PDF or run OCR before retrying.")
    return text


@app.post("/screen")
def screen() -> tuple[Any, int]:
    resume = request.files.get("resume")
    requirements_raw = request.form.get("requirements")
    candidate_name = request.form.get("candidate_name", "Unknown candidate").strip()
    if not resume or not resume.filename:
        return jsonify(error="missing_resume", message="Attach a resume PDF as form field 'resume'."), 400
    if not requirements_raw:
        return jsonify(error="missing_requirements", message="Provide JSON requirements."), 400
    if not resume.filename.lower().endswith(".pdf"):
        return jsonify(error="unsupported_file", message="Only PDF resumes are accepted."), 400
    try:
        requirements = json.loads(requirements_raw)
        if not isinstance(requirements, dict):
            raise ValueError("must be an object")
        result = screen_resume(extract_pdf_text(resume.read()), requirements)
    except json.JSONDecodeError:
        return jsonify(error="invalid_requirements", message="requirements must be a JSON object."), 400
    except ScreeningError as exc:
        return jsonify(error=exc.code, message=str(exc)), 422
    payload = {"event": "resume.screened", "occurred_at": datetime.now(UTC).isoformat(), "candidate_name": candidate_name, "source_filename": resume.filename, **result}
    try:
        delivery = send_to_zapier(payload)
    except ZapierDeliveryError as exc:
        return jsonify(error="zapier_delivery_failed", message=str(exc), screening=payload), 502
    return jsonify(screening=payload, zapier=delivery), 200


@app.get("/health")
def health() -> tuple[Any, int]:
    return jsonify(status="ok", ai_provider=os.getenv("AI_PROVIDER", "rules")), 200


@app.errorhandler(413)
def too_large(_: Any) -> tuple[Any, int]:
    return jsonify(error="file_too_large", message="Maximum upload size is 8 MB."), 413


if __name__ == "__main__":
    app.run(debug=True, port=5000)
