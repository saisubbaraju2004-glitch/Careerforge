import io
import json
from app import app

client = app.test_client()

def run_tests():
    print("==================================================")
    print("PHASE 6 — PAGE REGRESSION TEST")
    print("==================================================")
    page_routes = [
        '/',
        '/career-agent',
        '/placements',
        '/placements/company/zenvexa-tech',
        '/placement-strategy',
        '/placement-strategy/company/zenvexa-tech',
        '/job-match',
        '/job-match/job/job_py_01',
        '/interview',
        '/interview-intelligence',
        '/learning',
        '/placement-analytics',
        '/career-os',
        '/placement-practice/aptitude',
        '/placement-practice/coding',
        '/applications',
        '/applications/app_01',
        '/progress',
        '/jobs',
        '/resume-builder',
        '/intelligence',
        '/career'
    ]

    pages_passed = 0
    for r in page_routes:
        res = client.get(r)
        if res.status_code == 200:
            pages_passed += 1
            print(f"[PASS] {r} -> HTTP 200")
        else:
            print(f"[FAIL] {r} -> HTTP {res.status_code}")

    print(f"\nPages Passed: {pages_passed}/{len(page_routes)}")

    print("\n==================================================")
    print("PHASE 7 & 8 — API REGRESSION TEST")
    print("==================================================")
    api_get_endpoints = [
        '/api/health',
        '/api/roles',
        '/api/roadmap/python_backend_developer',
        '/api/jobs/python_backend_developer',
        '/api/career-intelligence',
        '/api/career-agent/context',
        '/api/career-agent/daily-mission',
        '/api/career-agent/weekly-review',
        '/api/career-agent/career-report',
        '/api/placements/profile',
        '/api/placements/companies',
        '/api/placements/eligible',
        '/api/placements/readiness',
        '/api/placements/company/zenvexa-tech',
        '/api/placements/daily-mission',
        '/api/placements/analytics',
        '/api/placements/report',
        '/api/placement-strategy/rankings',
        '/api/placement-strategy/company/zenvexa-tech',
        '/api/placement-strategy/apply-decision',
        '/api/placement-strategy/next-action',
        '/api/placement-strategy/war-plan',
        '/api/placement-strategy/daily-command',
        '/api/placement-strategy/readiness',
        '/api/job-match/jobs',
        '/api/job-match/top',
        '/api/job-match/job/job_py_01',
        '/api/job-match/skills',
        '/api/job-match/company/zenvexa-tech',
        '/api/interview-intelligence/history',
        '/api/interview-intelligence/readiness',
        '/api/interview/history',
        '/api/interview/improvement-plan',
        '/api/learning/profile',
        '/api/learning/progress',
        '/api/learning/resources',
        '/api/learning/next',
        '/api/placement-analytics/overview',
        '/api/placement-analytics/prediction',
        '/api/placement-analytics/companies',
        '/api/placement-analytics/funnel',
        '/api/placement-analytics/trends',
        '/api/placement-analytics/risks',
        '/api/placement-analytics/goals',
        '/api/career-os/overview',
        '/api/career-os/report',
        '/api/applications',
        '/api/applications/analytics',
        '/api/applications/priority'
    ]

    apis_passed = 0
    for api in api_get_endpoints:
        res = client.get(api)
        if res.status_code == 200 and res.is_json:
            data = res.get_json()
            if data.get("success") is True:
                apis_passed += 1
                print(f"[PASS] {api} -> HTTP 200 success=True")
            else:
                err = data.get("error", "No error string")
                print(f"[FAIL] {api} -> success=False: {err}")
        else:
            print(f"[FAIL] {api} -> HTTP {res.status_code}")

    print(f"\nAPIs Passed: {apis_passed}/{len(api_get_endpoints)}")

    print("\n==================================================")
    print("PHASE 9 — INVALID INPUT TESTING")
    print("==================================================")
    invalid_post_endpoints = [
        ("/api/career-plan", {}),
        ("/api/job-match/analyze", {"title": "", "description": ""}),
        ("/api/interview-intelligence/analyze", {"question": "", "answer": ""}),
        ("/api/interview-intelligence/next-question", {"previous_score": -100}),
        ("/api/placement-practice/coding/submit", {"user_code": "", "language": "invalid_lang"}),
        ("/api/resume-builder/analyze", {"resume_text": ""}),
        ("/api/career-os/chat", {"message": ""})
    ]

    invalid_passed = 0
    for endpoint, payload in invalid_post_endpoints:
        res = client.post(endpoint, json=payload)
        if res.is_json:
            data = res.get_json()
            # Must return clean JSON with success true/false and never crash (HTTP 500)
            if res.status_code in [200, 400, 422] and ("success" in data):
                invalid_passed += 1
                print(f"[PASS] {endpoint} with invalid input -> HTTP {res.status_code} ({data.get('success')})")
            else:
                print(f"[FAIL] {endpoint} -> HTTP {res.status_code}")
        else:
            print(f"[FAIL] {endpoint} -> Non-JSON response (HTTP {res.status_code})")

    print(f"Invalid Inputs Handled cleanly: {invalid_passed}/{len(invalid_post_endpoints)}")

    print("\n==================================================")
    print("PHASE 10 — FILE UPLOAD TESTING")
    print("==================================================")
    # Test valid txt file
    txt_file = (io.BytesIO(b"Alex Morgan\nPython, Flask, SQL, Docker\nB.Tech CSE"), "test_resume.txt")
    res_txt = client.post("/api/analyze-resume", data={"resume": txt_file}, content_type="multipart/form-data")
    print(f"[TEST] TXT Resume Upload -> HTTP {res_txt.status_code} ({res_txt.is_json})")

    # Test invalid extension file
    exe_file = (io.BytesIO(b"binary data"), "malicious.exe")
    res_exe = client.post("/api/analyze-resume", data={"resume": exe_file}, content_type="multipart/form-data")
    print(f"[TEST] EXE Resume Upload -> HTTP {res_exe.status_code} JSON={res_exe.is_json}")

    # Test empty upload
    res_empty = client.post("/api/analyze-resume", data={}, content_type="multipart/form-data")
    print(f"[TEST] Empty Resume Upload -> HTTP {res_empty.status_code} JSON={res_empty.is_json}")

if __name__ == "__main__":
    run_tests()
