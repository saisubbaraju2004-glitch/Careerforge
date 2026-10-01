import os
import re
import json
from config.config import Config
from services.ai_service import AIService
from services.resume_parser import ResumeParser
from services.job_matching_service import DEMO_JOBS_DATASET
from services.placement_service import PlacementService

class JobMatchService:
    def __init__(self, ai_service=None):
        self.ai_service = ai_service or AIService()
        self.placement_service = PlacementService(self.ai_service)
        
    def get_candidate_profile(self, resume_text=None, user_profile=None):
        """Extracts structured candidate profile from resume text and/or profile data."""
        if not user_profile:
            user_profile = {
                "name": "Alex Morgan",
                "email": "alex.morgan@example.com",
                "degree": "B.Tech",
                "branch": "Computer Science & Engineering",
                "graduation_year": 2027,
                "cgpa": 8.4,
                "experience_years": 0.5,
                "skills": ["Python", "Flask", "SQL", "PostgreSQL", "REST APIs", "Git", "HTML", "CSS", "JavaScript", "Docker"],
                "programming_languages": ["Python", "JavaScript", "SQL", "C++"],
                "frameworks": ["Flask", "React"],
                "databases": ["PostgreSQL", "SQLite"],
                "tools": ["Git", "Docker", "VS Code", "Postman"],
                "projects": [
                    {
                        "title": "CareerForge AI Platform",
                        "description": "Full-stack AI career platform with resume parser, interview simulator, and application tracker.",
                        "tech_stack": ["Python", "Flask", "PostgreSQL", "Docker", "REST APIs"]
                    },
                    {
                        "title": "E-Commerce Microservices",
                        "description": "Scalable REST API backend for order processing with database integration.",
                        "tech_stack": ["Python", "SQL", "REST APIs", "Git"]
                    }
                ],
                "certifications": ["Python Backend Certification", "AWS Cloud Practitioner"],
                "soft_skills": ["Problem Solving", "Communication", "Team Collaboration"],
                "has_resume": True
            }

        # If custom resume_text is supplied, combine/parse
        if resume_text and len(resume_text.strip()) > 30:
            user_profile["has_resume"] = True
            extracted_skills = ResumeParser.extract_skills_from_text(resume_text)
            if extracted_skills:
                # Merge extracted skills into profile skills
                user_profile["skills"] = list(set(user_profile.get("skills", []) + extracted_skills))
        
        return user_profile

    def get_all_jobs_and_companies(self):
        """Combines standard job postings and placement companies into a unified list."""
        all_items = []
        
        # Add demo jobs from job_matching_service
        for job in DEMO_JOBS_DATASET:
            all_items.append({
                "id": job["id"],
                "type": "job_posting",
                "title": job["title"],
                "company": job["company"],
                "role": job["title"],
                "location": job.get("location", "Remote/Hybrid"),
                "work_mode": job.get("work_mode", "Hybrid"),
                "salary": job.get("salary", "₹6-9 LPA"),
                "experience_required": job.get("experience", "0-1 Years"),
                "skills": job.get("skills", []),
                "description": job.get("description", ""),
                "apply_url": job.get("apply_url", "#"),
                "min_cgpa": 6.5,
                "allowed_branches": ["CSE", "IT", "AIML", "ECE"],
                "deadline": "2026-10-30",
                "priority_tag": "High Demand"
            })
            
        # Add placement companies
        placement_companies = self.placement_service.company_db
        for comp in placement_companies:
            all_items.append({
                "id": f"placement_{comp['id']}",
                "type": "placement_company",
                "title": f"{comp['role']} @ {comp['name']}",
                "company": comp["name"],
                "role": comp["role"],
                "location": comp.get("location", "Onsite"),
                "work_mode": "Campus Drive",
                "salary": comp.get("ctc", "₹7-10 LPA"),
                "experience_required": "Fresher (2027 Batch)",
                "skills": comp.get("skills", []),
                "description": f"Campus placement drive for {comp['name']}. Rounds: {', '.join(comp.get('rounds', []))}.",
                "apply_url": f"/placements/company/{comp['id']}",
                "min_cgpa": comp.get("eligibility", {}).get("min_cgpa", 7.0),
                "allowed_branches": comp.get("eligibility", {}).get("branches", ["CSE", "IT"]),
                "deadline": comp.get("deadline", "2026-10-20"),
                "priority_tag": "Campus Target",
                "company_raw_id": comp["id"]
            })
            
        return all_items

    def match_job(self, job, candidate_profile=None):
        """Calculates multi-factor job match score for a candidate against a job."""
        if not candidate_profile:
            candidate_profile = self.get_candidate_profile()

        cand_skills = [s.lower() for s in candidate_profile.get("skills", [])]
        req_skills = [s.lower() for s in job.get("skills", [])]
        
        # 1. Skill Match Score (25%)
        if req_skills:
            matched_skills_list = [s for s in job.get("skills", []) if s.lower() in cand_skills]
            missing_skills_list = [s for s in job.get("skills", []) if s.lower() not in cand_skills]
            skill_score = int(round((len(matched_skills_list) / len(req_skills)) * 100))
        else:
            matched_skills_list = job.get("skills", [])
            missing_skills_list = []
            skill_score = 85

        # 2. Role Match Score (20%)
        cand_degree = candidate_profile.get("degree", "B.Tech").lower()
        cand_branch = candidate_profile.get("branch", "Computer Science").lower()
        job_role_lower = job.get("role", "").lower() + " " + job.get("title", "").lower()
        
        role_score = 75
        if "backend" in job_role_lower or "software" in job_role_lower or "developer" in job_role_lower:
            role_score = 90 if ("computer" in cand_branch or "it" in cand_branch or "aiml" in cand_branch) else 70

        # 3. Experience & Eligibility Score (15%)
        exp_score = 85
        cand_cgpa = candidate_profile.get("cgpa", 8.4)
        job_min_cgpa = job.get("min_cgpa", 6.5)
        if cand_cgpa >= job_min_cgpa:
            exp_score = 95
        else:
            exp_score = 60

        # 4. Education Match Score (15%)
        edu_score = 90
        allowed_branches = [b.lower() for b in job.get("allowed_branches", ["cse", "it"])]
        if any(b in cand_branch for b in allowed_branches) or "cse" in allowed_branches:
            edu_score = 95
        else:
            edu_score = 70

        # 5. Project Match Score (10%)
        proj_score = 70
        cand_projects = candidate_profile.get("projects", [])
        proj_techs = []
        for p in cand_projects:
            proj_techs.extend([t.lower() for t in p.get("tech_stack", [])])
        
        if req_skills and proj_techs:
            proj_matches = [s for s in req_skills if s in proj_techs]
            proj_score = min(100, 60 + int((len(proj_matches) / max(1, len(req_skills))) * 50))

        # 6. Resume Keyword Match Score (10%)
        keyword_score = skill_score

        # 7. ATS Compatibility Score (5%)
        ats_score = min(98, max(65, int(round((skill_score * 0.4) + (role_score * 0.3) + (exp_score * 0.3)))))

        # Composite Weighted Overall Score
        overall_match = int(round(
            (skill_score * 0.25) +
            (role_score * 0.20) +
            (exp_score * 0.15) +
            (edu_score * 0.15) +
            (proj_score * 0.10) +
            (keyword_score * 0.10) +
            (ats_score * 0.05)
        ))
        
        overall_match = min(98, max(30, overall_match))

        # Classification
        if overall_match >= 85:
            badge = "🎯 HIGH MATCH"
            color_class = "high-match"
        elif overall_match >= 70:
            badge = "🟢 GOOD MATCH"
            color_class = "good-match"
        elif overall_match >= 50:
            badge = "🟡 MODERATE MATCH"
            color_class = "moderate-match"
        else:
            badge = "🔴 LOW MATCH"
            color_class = "low-match"

        # Missing Keywords & Boost suggestions
        recommendations = []
        missing_keyword_details = []
        for skill in missing_skills_list:
            boost = round(15.0 / max(1, len(req_skills)), 1)
            missing_keyword_details.append({
                "keyword": skill,
                "category": "Technical Skill",
                "impact_boost": f"+{boost}% Boost",
                "recommendation": f"Add hands-on project or coursework demonstrating {skill}."
            })
            recommendations.append(f"Add {skill} to your skills and project tech stack to boost match by +{boost}%.")

        if not recommendations:
            recommendations.append("Your profile matches all primary technical skill requirements for this role!")

        return {
            "job_id": job["id"],
            "title": job["title"],
            "company": job["company"],
            "role": job["role"],
            "location": job.get("location", "Hybrid"),
            "salary": job.get("salary", "N/A"),
            "work_mode": job.get("work_mode", "Hybrid"),
            "deadline": job.get("deadline", "Open"),
            "type": job.get("type", "job_posting"),
            "match_score": overall_match,
            "badge": badge,
            "color_class": color_class,
            "breakdown": {
                "skill_match": skill_score,
                "role_match": role_score,
                "experience_match": exp_score,
                "education_match": edu_score,
                "project_match": proj_score,
                "keyword_match": keyword_score,
                "ats_compatibility": ats_score
            },
            "matched_skills": matched_skills_list,
            "missing_skills": missing_skills_list,
            "missing_keyword_details": missing_keyword_details,
            "recommendations": recommendations,
            "apply_url": job.get("apply_url", "#"),
            "description": job.get("description", "")
        }

    def get_all_job_matches(self, candidate_profile=None):
        """Analyzes all jobs and placement companies, sorted by match score descending."""
        jobs = self.get_all_jobs_and_companies()
        matches = [self.match_job(j, candidate_profile) for j in jobs]
        matches.sort(key=lambda x: x["match_score"], reverse=True)
        return matches

    def get_top_target_jobs(self, candidate_profile=None, count=4):
        """Returns top 4 recommended job targets."""
        all_matches = self.get_all_job_matches(candidate_profile)
        return all_matches[:count]

    def analyze_custom_job_description(self, job_title, company_name, job_description, candidate_profile=None):
        """Analyzes a custom user-pasted job description against candidate profile."""
        if not candidate_profile:
            candidate_profile = self.get_candidate_profile()

        # Extract skills from description
        extracted_skills = ResumeParser.extract_skills_from_text(job_description)
        if not extracted_skills:
            extracted_skills = ["Python", "SQL", "REST APIs", "Git", "Problem Solving"]

        custom_job = {
            "id": "custom_analysis_" + re.sub(r'\W+', '_', job_title.lower())[:20],
            "type": "custom_job",
            "title": job_title,
            "company": company_name or "Target Company",
            "role": job_title,
            "location": "Target Location",
            "work_mode": "Target Work Mode",
            "salary": "Market Rate",
            "experience_required": "0-2 Years",
            "skills": extracted_skills,
            "description": job_description,
            "apply_url": "#",
            "min_cgpa": 6.5,
            "allowed_branches": ["CSE", "IT", "ECE"],
            "deadline": "Open"
        }

        return self.match_job(custom_job, candidate_profile)

    def compare_jobs(self, job_ids, candidate_profile=None):
        """Compares 2-3 jobs side-by-side."""
        all_matches = {m["job_id"]: m for m in self.get_all_job_matches(candidate_profile)}
        comparison_results = []
        
        for jid in job_ids:
            if jid in all_matches:
                comparison_results.append(all_matches[jid])
        
        # Calculate winning recommendation among compared
        winning_job = max(comparison_results, key=lambda x: x["match_score"]) if comparison_results else None
        
        return {
            "compared_jobs": comparison_results,
            "top_recommendation": winning_job["title"] if winning_job else "",
            "winning_job_id": winning_job["job_id"] if winning_job else "",
            "reason": f"{winning_job['title']} @ {winning_job['company']} offers the highest candidate fit ({winning_job['match_score']}%) with minimal missing skill gap." if winning_job else ""
        }

    def generate_tailored_resume_improvements(self, job_title, company, job_description, candidate_profile=None):
        """Generates AI-suggested tailored resume bullet points with mandatory warning disclaimer."""
        if not candidate_profile:
            candidate_profile = self.get_candidate_profile()

        prompt = f"""
        Act as an expert ATS Resume Coach.
        Generate 3 high-impact, ATS-optimized resume bullet points specifically tailored for:
        Role: {job_title}
        Company: {company}
        Job Description: {job_description}
        Candidate Skills: {', '.join(candidate_profile.get('skills', []))}
        Candidate Projects: {json.dumps(candidate_profile.get('projects', []))}

        Instructions:
        - Use strong action verbs (e.g., Architected, Engineered, Streamlined, Implemented).
        - Include realistic quantifiable metrics (%, ms latency reduction, scale, users).
        - Naturally integrate keywords relevant to the role.
        - DO NOT fabricate fake degrees or impossible achievements.

        Return JSON format ONLY:
        {{
            "tailored_bullets": [
                "Built high-throughput RESTful API endpoints using Python Flask and PostgreSQL, reducing endpoint response latency by 28%.",
                "Engineered containerized Docker microservices integrated with Git CI/CD pipelines, streamlining deployment workflows.",
                "Optimized database query indexes and schema designs, boosting data retrieval speed across 50,000+ daily transaction records."
            ],
            "key_enhancements": [
                "Added measurable performance metrics (28% latency reduction)",
                "Used industry standard keywords (RESTful, microservices, CI/CD)"
            ]
        }}
        """

        try:
            ai_res = self.ai_service.generate_content(prompt)
            # Parse JSON
            cleaned = ai_res.strip()
            if "```json" in cleaned:
                cleaned = cleaned.split("```json")[1].split("```")[0].strip()
            elif "```" in cleaned:
                cleaned = cleaned.split("```")[1].split("```")[0].strip()
            
            data = json.loads(cleaned)
            data["disclaimer"] = "AI Suggestion — Verify before using"
            return data
        except Exception as e:
            # Deterministic fallback when Gemini is offline or rate limited
            return {
                "tailored_bullets": [
                    f"Architected modular Python & Flask backend endpoints for {job_title} requirements, achieving clean 99.5% uptime and reliable payload execution.",
                    f"Engineered optimized PostgreSQL database queries and REST API schemas tailored for {company}, reducing query execution latency by 24%.",
                    "Integrated containerized Docker environments with version-controlled Git workflows, accelerating local microservice test execution by 35%."
                ],
                "key_enhancements": [
                    "Highlighted concrete action verbs and measurable performance metrics",
                    "Aligned bullet points with target role responsibilities"
                ],
                "disclaimer": "AI Suggestion — Verify before using"
            }

    def get_missing_skills_overview(self, candidate_profile=None):
        """Returns aggregated missing skills across all target jobs to prioritize learning."""
        top_matches = self.get_top_target_jobs(candidate_profile, count=6)
        missing_count = {}
        
        for m in top_matches:
            for s in m["missing_skills"]:
                missing_count[s] = missing_count.get(s, 0) + 1

        sorted_missing = sorted(missing_count.items(), key=lambda x: x[1], reverse=True)
        
        result = []
        for skill, count in sorted_missing:
            result.append({
                "skill": skill,
                "occurrence_count": count,
                "priority": "HIGH" if count >= 3 else "MEDIUM",
                "estimated_study_hours": 10 if count >= 3 else 5,
                "potential_boost": f"+{min(15, count * 4)}% Match Boost"
            })
            
        return result

    def calculate_apply_priority(self, job_id, candidate_profile=None):
        """Calculates APPLY FIRST priority for a specific job or company."""
        jobs_dict = {j["job_id"]: j for j in self.get_all_job_matches(candidate_profile)}
        target = jobs_dict.get(job_id)
        
        if not target:
            # Fallback for unknown ID
            all_matches = self.get_all_job_matches(candidate_profile)
            target = all_matches[0] if all_matches else None

        if not target:
            return {"priority": "MEDIUM", "decision": "APPLY NOW", "score": 75, "reason": "Good profile alignment."}

        match_score = target["match_score"]

        # Calculate Priority Score (Combination of Match %, Urgency, CTC/Value)
        priority_score = match_score
        if target["type"] == "placement_company":
            priority_score += 5  # Campus placement drives have strict deadlines
            
        if priority_score >= 88:
            decision = "APPLY FIRST (HIGH PRIORITY)"
            badge_class = "priority-first"
            reason = f"Exceptional {match_score}% match with strong candidate alignment. Applying immediately yields highest interview callback probability."
        elif priority_score >= 75:
            decision = "APPLY NOW (STRONG FIT)"
            badge_class = "priority-strong"
            reason = f"Solid {match_score}% match fit. Good callback odds; submit application within 24-48 hours."
        elif priority_score >= 60:
            decision = "PREPARE BEFORE APPLYING"
            badge_class = "priority-prep"
            reason = f"Moderate {match_score}% match. Address key missing skills ({', '.join(target['missing_skills'][:2])}) to maximize callback chances."
        else:
            decision = "LOW PRIORITY TARGET"
            badge_class = "priority-low"
            reason = f"Lower match fit ({match_score}%). Focus effort on top high-match targets first."

        return {
            "job_id": target["job_id"],
            "title": target["title"],
            "company": target["company"],
            "match_score": match_score,
            "priority_score": min(99, priority_score),
            "decision": decision,
            "badge_class": badge_class,
            "reason": reason,
            "recommended_action": "1. Review AI tailored resume bullets\n2. Update resume keywords\n3. Click Apply Now"
        }
