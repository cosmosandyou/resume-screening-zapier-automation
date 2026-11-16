from screening import screen_resume


def test_scores_and_flags_missing_email(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "rules")
    result = screen_resume("Python developer with 5 years of Flask and SQL.", {"required_skills": ["Python", "Flask"], "preferred_skills": ["SQL", "AWS"]})
    assert result["score"] == 90
    assert result["recommendation"] == "interview"
    assert result["missing_required_skills"] == []
    assert result["flags"] == ["missing_email"]


def test_missing_required_skill_reduces_score(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "rules")
    result = screen_resume("Recruiter email: alex@example.com", {"required_skills": ["Python", "Flask"]})
    assert result["score"] == 20
    assert result["missing_required_skills"] == ["Python", "Flask"]
