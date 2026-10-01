import os
import io
from app import app

client = app.test_client()

def test_security():
    print("==================================================")
    print("PHASE 18 — SECURITY TEST")
    print("==================================================")

    # 1. XSS Injection Test
    xss_payload = "<script>alert('xss')</script>"
    res_xss = client.post("/api/career-os/chat", json={"message": xss_payload})
    assert res_xss.status_code == 200
    data_xss = res_xss.get_json().get("data", {})
    assert "<script>" not in data_xss.get("reply", ""), "XSS script tag reflected unescaped!"
    print("[SECURITY 1 PASS] XSS payload safely sanitized in AI response.")

    # 2. Path Traversal Test
    res_traversal = client.get("/static/../../app.py")
    assert res_traversal.status_code in [400, 404], f"Path traversal succeeded! HTTP {res_traversal.status_code}"
    print("[SECURITY 2 PASS] Path traversal payload rejected with HTTP 404/400.")

    # 3. Unsafe File Upload Test
    sh_file = (io.BytesIO(b"#!/bin/bash\necho hack"), "exploit.sh")
    res_upload = client.post("/api/analyze-resume", data={"resume_file": sh_file}, content_type="multipart/form-data")
    assert res_upload.status_code == 400
    assert res_upload.get_json().get("success") is False
    print("[SECURITY 3 PASS] Unsafe file extension rejected with HTTP 400.")

    print("ALL SECURITY TESTS PASSED 100%!")

if __name__ == "__main__":
    test_security()
