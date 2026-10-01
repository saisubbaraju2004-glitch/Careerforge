from services.ai_service import AIService
from services.career_engine import CareerEngine


def test_resume_analysis_uses_deterministic_fallback_without_gemini():
    service = AIService(career_engine=CareerEngine())
    service.gemini_key = ""

    result = service.generate_resume_analysis(
        "Backend Developer", ["Python", "Flask"], "A sufficiently long resume text.", ["Built an API"]
    )

    assert result["strengths"]
    assert result["bullet_rewrites"][0]["original"] == "Built an API"


def test_career_plan_uses_fallback_after_invalid_or_unavailable_ai(monkeypatch):
    service = AIService(career_engine=CareerEngine())
    service.gemini_key = "test-only-key"

    for response in (None, "not valid json"):
        monkeypatch.setattr(service, "_call_gemini", lambda prompt, value=response: value)
        result = service.generate_career_plan("Backend Developer", [], ["Python"], 1)
        assert result
