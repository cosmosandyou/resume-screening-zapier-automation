"""Transparent screening layer: deterministic baseline or structured LLM output."""
from __future__ import annotations

import json
import os
import re
from typing import Any


class ScreeningError(Exception):
    def __init__(self, code: str, message: str):
        self.code = code
        super().__init__(message)


EMAIL = re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b", re.I)


def _rules_screen(resume_text: str, requirements: dict[str, Any]) -> dict[str, Any]:
    required = [str(s).strip() for s in requirements.get("required_skills", []) if str(s).strip()]
    preferred = [str(s).strip() for s in requirements.get("preferred_skills", []) if str(s).strip()]
    lowered = resume_text.lower()
    matched_required = [s for s in required if s.lower() in lowered]
    matched_preferred = [s for s in preferred if s.lower() in lowered]
    required_score = 70 * len(matched_required) / len(required) if required else 70
    preferred_score = 20 * len(matched_preferred) / len(preferred) if preferred else 20
    experience_bonus = 10 if re.search(r"\b\d{1,2}\+?\s+years?\b", lowered) else 0
    score = round(min(100, required_score + preferred_score + experience_bonus))
    email = EMAIL.search(resume_text)
    threshold = int(os.getenv("INTERVIEW_THRESHOLD", "70"))
    return {
        "provider": "rules", "score": score,
        "recommendation": "interview" if score >= threshold else "review",
        "matched_required_skills": matched_required,
        "missing_required_skills": [s for s in required if s not in matched_required],
        "matched_preferred_skills": matched_preferred,
        "email": email.group(0) if email else None,
        "flags": [] if email else ["missing_email"],
        "rationale": "Score uses disclosed skills and an explicit experience signal; it does not infer protected traits.",
    }


def _openai_screen(resume_text: str, requirements: dict[str, Any]) -> dict[str, Any]:
    try:
        from openai import OpenAI
        prompt = f'''You are an auditable recruiting assistant. Evaluate ONLY job-relevant evidence.
Never use or infer protected characteristics. Return valid JSON with keys: score (0-100 integer),
recommendation (interview or review), matched_required_skills (array), missing_required_skills (array),
matched_preferred_skills (array), email (string or null), flags (array), rationale (one short sentence).
Job requirements: {json.dumps(requirements)}
Resume:
{resume_text[:18000]}'''
        response = OpenAI().chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}, temperature=0,
        )
        result = json.loads(response.choices[0].message.content or "{}")
        result["provider"] = "openai"
        return result
    except Exception as exc:
        raise ScreeningError("ai_screening_failed", "The AI screening service failed; retry or switch AI_PROVIDER=rules.") from exc


def screen_resume(resume_text: str, requirements: dict[str, Any]) -> dict[str, Any]:
    if os.getenv("AI_PROVIDER", "rules").lower() == "openai":
        return _openai_screen(resume_text, requirements)
    return _rules_screen(resume_text, requirements)
