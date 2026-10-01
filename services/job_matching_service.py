import os
import json
from config.config import Config

DEMO_JOBS_DATASET = [
    {
        "id": "job_py_01",
        "title": "Python Backend Developer",
        "company": "TechForge Solutions",
        "location": "Bengaluru",
        "work_mode": "Hybrid",
        "salary": "₹5–8 LPA",
        "experience": "0–1 Years",
        "skills": ["Python", "Flask", "SQL", "PostgreSQL", "REST APIs", "Docker"],
        "description": "Build high-performance REST APIs, database queries, and modular backend microservices for enterprise clients.",
        "apply_url": "https://careers.techforgesolutions.com/jobs/py-backend",
        "is_demo": True,
        "data_label": "Demo Job Data",
        "role_category": "python_backend_developer"
    },
    {
        "id": "job_py_02",
        "title": "Junior Backend Engineer",
        "company": "Nexus Systems",
        "location": "Remote",
        "work_mode": "Remote",
        "salary": "₹4–6 LPA",
        "experience": "Fresher",
        "skills": ["Python", "Django", "SQL", "REST APIs", "Git"],
        "description": "Develop core business logic, maintain API documentation, and execute SQL schema updates in an agile backend team.",
        "apply_url": "https://nexus-systems.io/careers/junior-backend",
        "is_demo": True,
        "data_label": "Demo Job Data",
        "role_category": "python_backend_developer"
    },
    {
        "id": "job_py_03",
        "title": "FastAPI & Cloud Engineer",
        "company": "CloudScale AI",
        "location": "Hyderabad",
        "work_mode": "Onsite",
        "salary": "₹7–11 LPA",
        "experience": "1–3 Years",
        "skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "AWS", "Redis"],
        "description": "Architect async microservices, implement Redis caching pipelines, and maintain Docker deployment scripts on AWS.",
        "apply_url": "https://cloudscale.ai/jobs/fastapi-backend",
        "is_demo": True,
        "data_label": "Demo Job Data",
        "role_category": "python_backend_developer"
    },
    {
        "id": "job_py_04",
        "title": "Full Stack Python Developer",
        "company": "Innovate Labs",
        "location": "Pune",
        "work_mode": "Hybrid",
        "salary": "₹6–9 LPA",
        "experience": "0–1 Years",
        "skills": ["Python", "Flask", "JavaScript", "HTML", "CSS", "SQL"],
        "description": "End-to-end web product development combining robust Python Flask backends with intuitive web user interfaces.",
        "apply_url": "https://innovate-labs.co/careers/fullstack-py",
        "is_demo": True,
        "data_label": "Demo Job Data",
        "role_category": "python_backend_developer"
    },
    {
        "id": "job_py_05",
        "title": "Python API Developer",
        "company": "DataPulse Technologies",
        "location": "Gurugram",
        "work_mode": "Onsite",
        "salary": "₹5–8 LPA",
        "experience": "Fresher",
        "skills": ["Python", "REST APIs", "SQL", "PostgreSQL", "Docker"],
        "description": "Construct clean, OpenAPI-compliant endpoints, execute automated integration tests, and optimize query latency.",
        "apply_url": "https://datapulse.tech/jobs/api-developer",
        "is_demo": True,
        "data_label": "Demo Job Data",
        "role_category": "python_backend_developer"
    },
    {
        "id": "job_fe_01",
        "title": "Frontend Web Developer",
        "company": "PixelCraft UI Studio",
        "location": "Bengaluru",
        "work_mode": "Remote",
        "salary": "₹5–7 LPA",
        "experience": "0–1 Years",
        "skills": ["JavaScript", "HTML", "CSS", "React", "Tailwind CSS"],
        "description": "Craft responsive web application interfaces, glassmorphic UI components, and stateful dashboard workflows.",
        "apply_url": "https://pixelcraft.design/jobs/frontend",
        "is_demo": True,
        "data_label": "Demo Job Data",
        "role_category": "frontend_developer"
    },
    {
        "id": "job_devops_01",
        "title": "DevOps & Backend Specialist",
        "company": "InfraScale Ops",
        "location": "Noida",
        "work_mode": "Hybrid",
        "salary": "₹8–12 LPA",
        "experience": "1–3 Years",
        "skills": ["Python", "Docker", "AWS", "Linux", "CI/CD", "PostgreSQL"],
        "description": "Automate cloud infrastructure provisioning, containerize Python web microservices, and manage CI/CD deployment pipelines.",
        "apply_url": "https://infrascale.io/jobs/devops-backend",
        "is_demo": True,
        "data_label": "Demo Job Data",
        "role_category": "devops_engineer"
    },
    {
        "id": "job_ds_01",
        "title": "Junior Data Engineer",
        "company": "Insight Analytics",
        "location": "Mumbai",
        "work_mode": "Onsite",
        "salary": "₹6–9 LPA",
        "experience": "Fresher",
        "skills": ["Python", "SQL", "PostgreSQL", "Pandas", "ETL Pipelines"],
        "description": "Build scalable data pipelines, extract business metrics, and write optimized SQL queries for business intelligence reports.",
        "apply_url": "https://insightanalytics.com/careers/data-engineer",
        "is_demo": True,
        "data_label": "Demo Job Data",
        "role_category": "data_scientist"
    }
]

class JobMatchingService:
    def __init__(self, ai_service=None):
        self.ai_service = ai_service
        self.jobs_dataset = DEMO_JOBS_DATASET

    def get_all_jobs(self, filters=None):
        """Returns jobs dataset with optional filtering & sorting."""
        jobs = list(self.jobs_dataset)
        if not filters:
            return jobs

        role_filter = filters.get("role")
        location_filter = filters.get("location")
        work_mode = filters.get("work_mode")
        experience = filters.get("experience")

        filtered = []
        for j in jobs:
            if role_filter and role_filter.lower() not in j["title"].lower() and role_filter.lower() not in j["role_category"].lower():
                continue
            if location_filter and location_filter.lower() not in j["location"].lower():
                continue
            if work_mode and work_mode != "All" and j["work_mode"].lower() != work_mode.lower():
                continue
            if experience and experience != "All" and j["experience"].lower() != experience.lower():
                continue
            filtered.append(j)

        return filtered

    def get_job_by_id(self, job_id):
        job_id_lower = str(job_id).lower()
        for j in self.jobs_dataset:
            if j["id"].lower() == job_id_lower or j.get("role_category", "").lower() == job_id_lower or job_id_lower in j.get("title", "").lower():
                return j
        return self.jobs_dataset[0] if self.jobs_dataset else None

    def calculate_job_match(self, job, candidate_profile):
        """
        Calculates deterministic match score (0-100) using weighted factors:
        - Skill Match: 40%
        - Experience Match: 20%
        - Role Match: 15%
        - Project Match: 10%
        - Resume ATS Score: 10%
        - Career Readiness: 5%
        """
        user_skills = [s.strip().lower() for s in candidate_profile.get("skills", [])]
        req_skills = [s.strip().lower() for s in job.get("skills", [])]

        # 1. Skill Match (40%)
        matching_skills = [s for s in job.get("skills", []) if s.strip().lower() in user_skills]
        missing_skills = [s for s in job.get("skills", []) if s.strip().lower() not in user_skills]

        skill_ratio = len(matching_skills) / max(1, len(req_skills))
        skill_score = skill_ratio * 40

        # 2. Experience Match (20%)
        exp_req = job.get("experience", "").lower()
        exp_score = 20 if "fresher" in exp_req or "0–1" in exp_req or "0-1" in exp_req else 14

        # 3. Role Title Match (15%)
        target_role = candidate_profile.get("target_role", "").lower()
        job_title = job.get("title", "").lower()

        if "python" in target_role and "python" in job_title:
            role_score = 15
        elif "backend" in target_role and "backend" in job_title:
            role_score = 14
        else:
            role_score = 10

        # 4. Project Match (10%)
        projects = candidate_profile.get("projects", [])
        proj_score = 10 if projects else 6

        # 5. Resume ATS Match (10%)
        ats_score = self._clamp(candidate_profile.get("ats_score", 75), 0, 100)
        resume_score = (ats_score / 100) * 10

        # 6. Readiness Score Match (5%)
        readiness_score = self._clamp(candidate_profile.get("readiness_score", 70), 0, 100)
        readiness_component = (readiness_score / 100) * 5

        # Weighted Total
        raw_match = skill_score + exp_score + role_score + proj_score + resume_score + readiness_component
        final_match = self._clamp(raw_match, 10, 98)

        # Readiness classification for application
        if final_match >= 80:
            match_category = "Excellent Match"
            badge_color = "green"
            apply_readiness = "APPLY NOW"
            apply_reason = "You meet most critical technical requirements. High placement match probability."
        elif final_match >= 60:
            match_category = "Good Match"
            badge_color = "yellow"
            apply_readiness = "IMPROVE THEN APPLY" if missing_skills else "APPLY NOW"
            apply_reason = "Strong core fit. Closing 1 key missing skill will boost callback probability."
        elif final_match >= 40:
            match_category = "Partial Match"
            badge_color = "orange"
            apply_readiness = "IMPROVE THEN APPLY"
            apply_reason = "You match foundational skills but require additional project/tool depth."
        else:
            match_category = "Low Match"
            badge_color = "red"
            apply_readiness = "NOT RECOMMENDED YET"
            apply_reason = "Significant skill gaps exist for this specific position."

        # Job Skill Gap Breakdown
        skill_breakdown = []
        for sk in job.get("skills", []):
            if sk.strip().lower() in user_skills:
                skill_breakdown.append({"skill": sk, "status": "✓", "type": "matched"})
            elif len(skill_breakdown) < len(user_skills) + 1:
                skill_breakdown.append({"skill": sk, "status": "⚠", "type": "gap"})
            else:
                skill_breakdown.append({"skill": sk, "status": "✕", "type": "missing"})

        estimated_gap_days = len(missing_skills) * 7

        return {
            "job_id": job["id"],
            "title": job["title"],
            "company": job["company"],
            "location": job["location"],
            "work_mode": job["work_mode"],
            "salary": job["salary"],
            "experience": job["experience"],
            "skills": job["skills"],
            "description": job["description"],
            "apply_url": job["apply_url"],
            "is_demo": job.get("is_demo", True),
            "data_label": job.get("data_label", "Demo Job Data"),
            "match_score": final_match,
            "match_category": match_category,
            "badge_color": badge_color,
            "apply_readiness": apply_readiness,
            "apply_reason": apply_reason,
            "matching_skills": matching_skills,
            "missing_skills": missing_skills,
            "your_advantage": f"Your project experience in {candidate_profile.get('projects', ['Python APIs'])[0] if candidate_profile.get('projects') else 'backend development'} aligns directly with {job['company']}'s tech stack.",
            "skill_breakdown": skill_breakdown,
            "estimated_gap_days": estimated_gap_days
        }

    def process_job_matches(self, candidate_profile, filters=None):
        """Processes and ranks all dataset jobs against candidate profile."""
        jobs = self.get_all_jobs(filters)
        matched_jobs = []

        for j in jobs:
            m = self.calculate_job_match(j, candidate_profile)
            matched_jobs.append(m)

        # Sort by match score descending
        matched_jobs.sort(key=lambda x: x["match_score"], reverse=True)

        # Top 3 Recommended Jobs
        top_recommendations = matched_jobs[:3]

        # Market Skill Demand (Calculated from demo dataset)
        all_req_skills = []
        for j in self.jobs_dataset:
            all_req_skills.extend(j.get("skills", []))

        total_jobs_count = max(1, len(self.jobs_dataset))
        skill_counts = {}
        for sk in all_req_skills:
            skill_counts[sk] = skill_counts.get(sk, 0) + 1

        skill_demand = []
        for sk, count in sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:8]:
            demand_pct = int(round((count / total_jobs_count) * 100))
            skill_demand.append({
                "skill": sk,
                "percentage": demand_pct,
                "job_count": count
            })

        # Determine most common missing skill across top matching jobs
        top_missing_counts = {}
        for m in matched_jobs[:10]:
            for sk in m["missing_skills"]:
                top_missing_counts[sk] = top_missing_counts.get(sk, 0) + 1

        top_missing_skill = "Docker"
        if top_missing_counts:
            top_missing_skill = max(top_missing_counts.items(), key=lambda x: x[1])[0]

        top_missing_frequency = top_missing_counts.get(top_missing_skill, 6)

        recommended_action = {
            "title": f"Master {top_missing_skill} Fundamentals",
            "action": f"Learn {top_missing_skill}",
            "why": f"{top_missing_skill} appears in {top_missing_frequency} of your top matching job opportunities. Mastering it will boost your top match score above 90%.",
            "estimated_impact": "+12 match score points",
            "link": "/#tabOverview"
        }

        return {
            "target_role": candidate_profile.get("target_role", "Python Backend Developer"),
            "readiness_score": candidate_profile.get("readiness_score", 72),
            "total_matching_jobs": len(matched_jobs),
            "top_match": matched_jobs[0] if matched_jobs else None,
            "top_recommendations": top_recommendations,
            "all_jobs": matched_jobs,
            "skill_demand": skill_demand,
            "data_attribution": "Based on available CareerForge job dataset",
            "recommended_action": recommended_action
        }

    def generate_ai_job_pitch(self, job_id, candidate_profile):
        """Explains why candidate should apply to specific job."""
        job = self.get_job_by_id(job_id)
        if not job:
            return {"reply": "Job details could not be found."}

        match = self.calculate_job_match(job, candidate_profile)

        # Gemini AI pitch if configured
        if self.ai_service and self.ai_service.gemini_key:
            try:
                prompt = f"""You are an expert AI Career Coach evaluating a job candidate for a position.
Target Job: {job['title']} at {job['company']} (Match Score: {match['match_score']}%)
Location: {job['location']} ({job['work_mode']})
Salary: {job['salary']}
Matching Skills: {', '.join(match['matching_skills'])}
Missing Skills: {', '.join(match['missing_skills'])}
Candidate Readiness: {candidate_profile.get('readiness_score', 70)}%

Provide a concise 2-paragraph coach recommendation answering:
1. Why this job matches their current profile.
2. What missing skills to address or whether to click Apply now.
Keep advice direct, encouraging, and actionable."""
                raw = self.ai_service._call_gemini(prompt)
                if raw and len(raw.strip()) > 10:
                    return {"reply": raw.strip()}
            except Exception:
                pass

        # Deterministic pitch fallback
        missing_text = f"Work on closing {', '.join(match['missing_skills'][:2])} over the next 1-2 weeks." if match['missing_skills'] else "You meet all primary skill requirements!"
        pitch = f"**Why You Match:** You have a strong {match['match_score']}% match for {job['title']} at {job['company']}. Your proficiency in {', '.join(match['matching_skills'][:3]) if match['matching_skills'] else 'core programming'} directly aligns with their team's technical requirements.\n\n**Application Strategy:** We recommend clicking **Apply Now**. {missing_text} Adding your portfolio API project will maximize your callback rate."
        return {"reply": pitch}

    def _clamp(self, val, min_v, max_v):
        try:
            val_f = float(val)
            return max(min_v, min(max_v, int(round(val_f))))
        except (ValueError, TypeError):
            return min_v
