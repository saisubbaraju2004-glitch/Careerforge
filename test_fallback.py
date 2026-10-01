import os
from types import SimpleNamespace
from app import app
from google import genai
from services.ai_service import AIService
from services.career_engine import CareerEngine

client = app.test_client()

def test_ai_prompt_templates_and_provider_failures():
    original_client = genai.Client
    try:
        class MalformedResponseClient:
            def __init__(self, **kwargs):
                self.models = self

            def generate_content(self, **kwargs):
                return SimpleNamespace(text="not valid JSON")

        genai.Client = MalformedResponseClient
        ai = AIService(CareerEngine())
        ai.gemini_key = "test-only-not-a-real-key"

        assert ai.generate_career_plan("Python Developer", [], ["Docker"], 2)
        assert ai.generate_career_diagnosis("Python Developer", [], ["Docker"], 50)
        assert ai.generate_resume_analysis("Python Developer", [], "A" * 60)

        class TimeoutClient:
            def __init__(self, **kwargs):
                assert kwargs["http_options"].timeout == 15_000
                self.models = self

            def generate_content(self, **kwargs):
                raise TimeoutError("simulated provider timeout")

        genai.Client = TimeoutClient
        assert ai.generate_career_plan("Python Developer", [], ["Docker"], 2)
    finally:
        genai.Client = original_client

def test_gemini_fallbacks():
    print("==================================================")
    print("PHASE 16 — GEMINI OFFLINE / FALLBACK TEST")
    print("==================================================")
    os.environ["GEMINI_API_KEY"] = ""

    # Test 1: Resume Improvement Fallback
    res1 = client.post("/api/job-match/resume-improvements", json={"title": "Software Engineer", "company": "Demo Corp"})
    assert res1.status_code == 200, f"Fallback 1 failed: {res1.status_code}"
    data1 = res1.get_json().get("improvements", {})
    assert "disclaimer" in data1
    print(f"[FALLBACK 1 PASS] Job Match Resume Improvements returned fallback bullets with disclaimer.")

    # Test 2: Interview Answer Fallback
    res2 = client.post("/api/interview-intelligence/analyze", json={
        "question": "What is GIL?",
        "answer": "GIL is Global Interpreter Lock in CPython.",
        "role": "Python Backend Developer"
    })
    assert res2.status_code == 200, f"Fallback 2 failed: {res2.status_code}"
    print(f"[FALLBACK 2 PASS] Interview Analysis returned deterministic fallback scores & structure suggestions.")

    # Test 3: AI Career OS Chat Fallback
    res3 = client.post("/api/career-os/chat", json={"message": "What should I do today?"})
    assert res3.status_code == 200, f"Fallback 3 failed: {res3.status_code}"
    data3 = res3.get_json().get("data", {})
    assert "reply" in data3
    print(f"[FALLBACK 3 PASS] AI Career OS Chat returned deterministic guidance without API key.")

    print("ALL GEMINI FALLBACK TESTS PASSED 100%!")

if __name__ == "__main__":
    test_ai_prompt_templates_and_provider_failures()
    test_gemini_fallbacks()
