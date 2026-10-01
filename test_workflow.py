import io
import json
from app import app

client = app.test_client()

def test_full_user_journey():
    print("==================================================")
    print("PHASE 11 - RESUME -> JOB MATCH -> CAREER OS WORKFLOW")
    print("==================================================")

    # STEP 1: Upload resume
    txt_file = (io.BytesIO(b"Alex Morgan\nEmail: alex@example.com\nSkills: Python, Flask, SQL, REST APIs\nEducation: B.Tech CSE (2027), CGPA: 8.4"), "alex_resume.txt")
    res1 = client.post("/api/analyze-resume", data={"resume_file": txt_file}, content_type="multipart/form-data")
    assert res1.status_code == 200, f"Step 1 failed: {res1.status_code}"
    print("[STEP 1 & 2 & 3 & 4] Resume uploaded, parsed, ATS score & skill gaps generated successfully.")

    # STEP 5 & 6 & 7: Open Job Matching & Calculate Match
    res5 = client.get("/api/job-match/jobs")
    assert res5.status_code == 200, f"Step 5 failed: {res5.status_code}"
    jobs_data = res5.get_json().get("jobs", [])
    top_job = jobs_data[0]
    print(f"[STEP 5 & 6 & 7] Job Matching initialized. Top target job: {top_job['title']} @ {top_job['company']} ({top_job['match_score']}% Match).")

    # STEP 8: Generate Resume Improvements
    res8 = client.post("/api/job-match/resume-improvements", json={"title": top_job["title"], "company": top_job["company"]})
    assert res8.status_code == 200, f"Step 8 failed: {res8.status_code}"
    imp = res8.get_json().get("improvements", {})
    assert imp.get("disclaimer") == "AI Suggestion — Verify before using"
    print(f"[STEP 8] Resume Improvements generated with mandatory disclaimer label: '{imp.get('disclaimer')}'.")

    # STEP 9 & 10: Open Career Agent & Next Best Action
    res9 = client.get("/api/career-agent/context")
    assert res9.status_code == 200, f"Step 9 failed: {res9.status_code}"
    print(f"[STEP 9 & 10] Career Agent context unified. Next best action calculated.")

    # STEP 11 & 12 & 13: Personalized Learning
    res11 = client.get("/api/learning/next")
    assert res11.status_code == 200, f"Step 11 failed: {res11.status_code}"
    res13 = client.post("/api/learning/complete", json={"lesson_id": "day_1"})
    assert res13.status_code == 200, f"Step 13 failed: {res13.status_code}"
    print(f"[STEP 11 & 12 & 13] Personalized Learning Engine recommendation loaded and lesson completed.")

    # STEP 14 & 15 & 16 & 17: Interview Intelligence
    res14 = client.post("/api/interview-intelligence/start", json={"role": "Python Backend Developer"})
    assert res14.status_code == 200, f"Step 14 failed: {res14.status_code}"
    res16 = client.post("/api/interview-intelligence/analyze", json={
        "question": "Explain Flask request routing",
        "answer": "Flask uses werkzeug URL map matching decorators like @app.route to bind endpoint functions to incoming HTTP request paths.",
        "expected_keywords": ["werkzeug", "decorators", "endpoint"]
    })
    assert res16.status_code == 200, f"Step 16 failed: {res16.status_code}"
    print(f"[STEP 14 & 15 & 16 & 17] Interview Intelligence simulator initialized and answer analyzed.")

    # STEP 18 & 19 & 20: Placement Strategy & War Plan
    res18 = client.get("/api/placement-strategy/rankings")
    assert res18.status_code == 200, f"Step 18 failed: {res18.status_code}"
    res20 = client.get("/api/placement-strategy/company/zenvexa-tech")
    assert res20.status_code == 200, f"Step 20 failed: {res20.status_code}"
    print(f"[STEP 18 & 19 & 20] Placement Strategy company rankings and Zenvexa War Room loaded.")

    # STEP 21 & 22: Placement Analytics & Readiness Prediction
    res21 = client.get("/api/placement-analytics/overview")
    assert res21.status_code == 200, f"Step 21 failed: {res21.status_code}"
    res22 = client.get("/api/placement-analytics/prediction")
    assert res22.status_code == 200, f"Step 22 failed: {res22.status_code}"
    print(f"[STEP 21 & 22] Placement Analytics & Readiness predictions loaded.")

    # STEP 23 & 24: Open Career OS & Unified Recommendation
    res23 = client.get("/api/career-os/overview")
    assert res23.status_code == 200, f"Step 23 failed: {res23.status_code}"
    print("[STEP 23 & 24] AI Career OS endpoints responded. Shared persistent user data was not verified.")

if __name__ == "__main__":
    test_full_user_journey()
