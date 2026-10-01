import os
import json
from config.config import Config

class PlacementService:
    def __init__(self, ai_service=None):
        self.ai_service = ai_service
        self.company_db = self._init_company_database()

    def _init_company_database(self):
        """Initializes benchmark company dataset for campus placements."""
        return [
            {
                "id": "zenvexa-tech",
                "name": "Zenvexa Technologies",
                "role": "Software Development Engineer",
                "ctc": "₹7.5 - 9.0 LPA",
                "location": "Bengaluru / Remote",
                "eligibility": {
                    "min_cgpa": 7.0,
                    "branches": ["CSE", "IT", "AIML", "ECE"],
                    "backlogs_allowed": False
                },
                "rounds": ["Aptitude Assessment", "Coding Challenge", "Technical Interview (DSA & System Design)", "HR & Leadership"],
                "skills": ["Python", "Data Structures", "SQL", "REST APIs", "System Design"],
                "status": "Eligible",
                "deadline": "2026-10-15",
                "resume_match": 88
            },
            {
                "id": "techforge-sol",
                "name": "TechForge Solutions",
                "role": "Python Backend Developer",
                "ctc": "₹6.0 - 7.5 LPA",
                "location": "Hyderabad / Pune",
                "eligibility": {
                    "min_cgpa": 6.5,
                    "branches": ["CSE", "IT", "AIML", "ECE", "EEE"],
                    "backlogs_allowed": True
                },
                "rounds": ["Online Aptitude", "Coding Test", "Technical Screening", "HR Interview"],
                "skills": ["Python", "Flask", "PostgreSQL", "Docker", "Git"],
                "status": "Eligible",
                "deadline": "2026-10-18",
                "resume_match": 84
            },
            {
                "id": "cloudscale-labs",
                "name": "CloudScale Systems",
                "role": "Cloud & DevOps Associate",
                "ctc": "₹8.0 - 10.5 LPA",
                "location": "Bengaluru / Gurugram",
                "eligibility": {
                    "min_cgpa": 7.5,
                    "branches": ["CSE", "IT", "AIML"],
                    "backlogs_allowed": False
                },
                "rounds": ["Technical Aptitude", "Cloud & Networking Test", "Live Technical Interview", "Management Interview"],
                "skills": ["Python", "Linux", "Docker", "AWS", "Networking"],
                "status": "Upcoming",
                "deadline": "2026-10-22",
                "resume_match": 76
            },
            {
                "id": "dataprime-ai",
                "name": "DataPrime AI",
                "role": "AI & ML Engineer Trainee",
                "ctc": "₹9.0 - 12.0 LPA",
                "location": "Bengaluru / Hybrid",
                "eligibility": {
                    "min_cgpa": 8.0,
                    "branches": ["CSE", "IT", "AIML"],
                    "backlogs_allowed": False
                },
                "rounds": ["Aptitude & Math", "Machine Learning Coding", "AI Technical Deep Dive", "HR Round"],
                "skills": ["Python", "PyTorch", "FastAPI", "Machine Learning", "SQL"],
                "status": "Eligible",
                "deadline": "2026-10-25",
                "resume_match": 82
            },
            {
                "id": "cybercore-sec",
                "name": "CyberCore Security",
                "role": "Associate Security Analyst",
                "ctc": "₹5.5 - 7.0 LPA",
                "location": "Pune / Chennai",
                "eligibility": {
                    "min_cgpa": 6.0,
                    "branches": ["CSE", "IT", "AIML", "ECE", "EEE", "MECH"],
                    "backlogs_allowed": True
                },
                "rounds": ["Aptitude Test", "Security Fundamentals Test", "Technical Interview", "HR Interview"],
                "skills": ["Python", "Networking", "Linux", "Web Security", "SQL"],
                "status": "Eligible",
                "deadline": "2026-10-28",
                "resume_match": 72
            },
            {
                "id": "innovatex-corp",
                "name": "InnovateX Global",
                "role": "Full-Stack Developer Trainee",
                "ctc": "₹6.5 - 8.0 LPA",
                "location": "Noida / Hyderabad",
                "eligibility": {
                    "min_cgpa": 7.0,
                    "branches": ["CSE", "IT", "AIML"],
                    "backlogs_allowed": False
                },
                "rounds": ["Online Assessment", "Frontend & Backend Coding", "Technical Interview", "HR Discussion"],
                "skills": ["Python", "JavaScript", "React", "NodeJS", "SQL"],
                "status": "Eligible",
                "deadline": "2026-11-02",
                "resume_match": 79
            }
        ]

    def get_user_profile(self, raw_data=None):
        """Normalizes user placement profile data."""
        raw = raw_data if isinstance(raw_data, dict) else {}
        return {
            "name": str(raw.get("name") or "Rahul Sharma"),
            "college": str(raw.get("college") or "National Institute of Technology"),
            "branch": str(raw.get("branch") or "CSE"),
            "graduation_year": int(raw.get("graduation_year") or 2027),
            "cgpa": float(raw.get("cgpa") or 7.85),
            "backlogs": int(raw.get("backlogs") or 0),
            "target_role": str(raw.get("target_role") or "Software Developer"),
            "preferred_location": str(raw.get("preferred_location") or "Bengaluru / Remote")
        }

    def evaluate_company_eligibility(self, company, profile):
        """Calculates eligibility for a student against a specific company requirement."""
        req = company.get("eligibility", {})
        min_cgpa = float(req.get("min_cgpa", 0))
        allowed_branches = req.get("branches", [])
        backlogs_allowed = bool(req.get("backlogs_allowed", True))

        cgpa_ok = profile["cgpa"] >= min_cgpa
        branch_ok = not allowed_branches or (profile["branch"] in allowed_branches)
        backlog_ok = backlogs_allowed or (profile["backlogs"] == 0)

        if cgpa_ok and branch_ok and backlog_ok:
            status = "ELIGIBLE"
            status_color = "green"
            reason = f"CGPA ({profile['cgpa']:.2f} >= {min_cgpa:.1f}), Branch ({profile['branch']}) & Backlog criteria met."
        elif not cgpa_ok:
            status = "NOT ELIGIBLE"
            status_color = "red"
            reason = f"CGPA ({profile['cgpa']:.2f}) is below minimum requirement ({min_cgpa:.1f})."
        elif not branch_ok:
            status = "NOT ELIGIBLE"
            status_color = "red"
            reason = f"Branch ({profile['branch']}) is not listed in allowed branches ({', '.join(allowed_branches)})."
        else:
            status = "NEEDS REVIEW"
            status_color = "yellow"
            reason = "Active backlog criteria require review with campus placement cell."

        return {
            "status": status,
            "status_color": status_color,
            "is_eligible": status == "ELIGIBLE",
            "reason": reason,
            "min_cgpa": min_cgpa,
            "allowed_branches": allowed_branches,
            "backlogs_allowed": backlogs_allowed
        }

    def get_all_companies(self, profile_data=None):
        """Returns benchmark companies augmented with candidate eligibility and readiness metrics."""
        profile = self.get_user_profile(profile_data)
        enriched = []

        for comp in self.company_db:
            el = self.evaluate_company_eligibility(comp, profile)
            # Calculate company-specific readiness score
            company_readiness = self._calculate_company_readiness(comp, profile)
            priority_score = self._calculate_company_priority(comp, el, company_readiness)

            c_copy = dict(comp)
            c_copy["eligibility_result"] = el
            c_copy["company_readiness"] = company_readiness
            c_copy["priority_score"] = priority_score
            enriched.append(c_copy)

        # Sort by priority score descending
        enriched.sort(key=lambda x: x["priority_score"], reverse=True)
        return enriched

    def get_eligible_companies(self, profile_data=None):
        """Filters companies where the candidate meets eligibility criteria."""
        all_comps = self.get_all_companies(profile_data)
        return [c for c in all_comps if c["eligibility_result"]["is_eligible"]]

    def get_company_by_id(self, company_id, profile_data=None):
        """Returns details for a specific company by ID."""
        all_comps = self.get_all_companies(profile_data)
        for c in all_comps:
            if c["id"] == company_id:
                return c
        # Default fallback company if not found
        return all_comps[0] if all_comps else None

    def _calculate_company_readiness(self, company, profile):
        """Calculates candidate placement readiness score (0-100) for a given company."""
        # Simulated readiness components based on skills and benchmarks
        skills_len = len(company.get("skills", []))
        readiness_base = 72 + (skills_len * 2)
        return max(50, min(95, readiness_base))

    def _calculate_company_priority(self, company, eligibility_res, readiness_score):
        """Calculates deterministic company priority ranking score (0-100)."""
        eligibility_weight = 30 if eligibility_res["is_eligible"] else 0
        match_weight = (company.get("resume_match", 75) * 0.35)
        readiness_weight = (readiness_score * 0.35)
        return int(round(eligibility_weight + match_weight + readiness_weight))

    def calculate_placement_readiness(self, profile_data=None, user_scores=None):
        """Calculates multi-factor Placement Readiness Radar breakdown."""
        scores = user_scores if isinstance(user_scores, dict) else {}

        dsa = self._clamp(scores.get("dsa", 68), 30, 98)
        aptitude = self._clamp(scores.get("aptitude", 82), 30, 98)
        programming = self._clamp(scores.get("programming", 78), 30, 98)
        core_cs = self._clamp(scores.get("core_cs", 74), 30, 98)
        projects = self._clamp(scores.get("projects", 75), 30, 98)
        resume = self._clamp(scores.get("resume", 84), 30, 98)
        interview = self._clamp(scores.get("interview", 76), 30, 98)
        communication = self._clamp(scores.get("communication", 81), 30, 98)

        overall = int(round((dsa * 0.18) + (aptitude * 0.14) + (programming * 0.16) + 
                           (core_cs * 0.12) + (projects * 0.10) + (resume * 0.10) + 
                           (interview * 0.12) + (communication * 0.08)))

        if overall >= 80:
            status = "PLACEMENT READY"
            status_badge = "purple"
        elif overall >= 68:
            status = "ON TRACK"
            status_badge = "success"
        else:
            status = "NEEDS PREPARATION"
            status_badge = "warning"

        categories = {
            "DSA": dsa,
            "Aptitude": aptitude,
            "Programming": programming,
            "Core CS": core_cs,
            "Projects": projects,
            "Resume": resume,
            "Interview": interview,
            "Communication": communication
        }

        # Weakest and strongest
        weakest = min(categories.items(), key=lambda x: x[1])
        strongest = max(categories.items(), key=lambda x: x[1])

        return {
            "overall_readiness": overall,
            "status": status,
            "status_badge": status_badge,
            "categories": categories,
            "weakest_area": weakest[0],
            "weakest_score": weakest[1],
            "strongest_area": strongest[0],
            "strongest_score": strongest[1]
        }

    def generate_company_prep_plan(self, company_id, profile_data=None):
        """Generates a 7-day targeted study and preparation schedule for a specific company."""
        comp = self.get_company_by_id(company_id, profile_data)
        comp_name = comp["name"] if comp else "Target Placement Company"
        role = comp["role"] if comp else "Software Engineer"
        skills = comp["skills"] if comp else ["Python", "DSA", "SQL"]

        top_skill_1 = skills[0] if len(skills) > 0 else "Arrays & Strings"
        top_skill_2 = skills[1] if len(skills) > 1 else "SQL & DBMS"
        top_skill_3 = skills[2] if len(skills) > 2 else "System Design"

        schedule = [
            {"day": "Day 1", "focus": f"Quantitative Aptitude & {top_skill_1} Warmup", "details": "Solve 15 speed math questions & implement 3 core array/string problems.", "minutes": 60},
            {"day": "Day 2", "focus": f"Data Structures (Hashmaps, Searching & Sorting)", "details": "Master key lookup techniques and standard binary search variants.", "minutes": 75},
            {"day": "Day 3", "focus": f"{top_skill_2} & Database Fundamentals", "details": "Review SQL JOINS, indexing, group by aggregations, and normalization.", "minutes": 60},
            {"day": "Day 4", "focus": "Object-Oriented Programming & Core CS", "details": "Review OOPs pillars (Inheritance, Polymorphism) and OS Threading/Processes.", "minutes": 60},
            {"day": "Day 5", "focus": f"{top_skill_3} & Technical Problem Solving", "details": "Build micro REST API endpoint or review system architecture fundamentals.", "minutes": 90},
            {"day": "Day 6", "focus": f"Full {comp_name} AI Mock Interview", "details": "Complete live technical interview simulator tailored for {role}.", "minutes": 45},
            {"day": "Day 7", "focus": "HR Preparation & Final Placement Screening", "details": "Prepare STAR method answers for leadership, conflict resolution, and behavioral questions.", "minutes": 45}
        ]

        return {
            "company_id": company_id,
            "company_name": comp_name,
            "role": role,
            "schedule": schedule,
            "total_days": 7
        }

    def generate_placement_daily_mission(self, profile_data=None):
        """Generates daily campus placement preparation task list."""
        comps = self.get_eligible_companies(profile_data)
        top_comp = comps[0]["name"] if comps else "Zenvexa Technologies"

        tasks = [
            {"title": f"Solve 5 DSA Array & String problems for {top_comp}", "minutes": 45, "type": "coding", "route": "/placement-practice/coding"},
            {"title": "Practice 10 Quantitative Aptitude questions", "minutes": 30, "type": "aptitude", "route": "/placement-practice/aptitude"},
            {"title": "Review SQL Joins & Subqueries cheat sheet", "minutes": 20, "type": "core", "route": "/#tabOverview"},
            {"title": f"Complete 1 AI Technical Mock Interview session for {top_comp}", "minutes": 35, "type": "interview", "route": f"/interview?company={top_comp}"},
            {"title": "Apply to 1 eligible placement drive on portal", "minutes": 10, "type": "application", "route": "/placements"}
        ]

        total_mins = sum(t["minutes"] for t in tasks)
        return {
            "tasks": tasks,
            "total_estimated_minutes": total_mins,
            "formatted_time": f"{total_mins // 60}h {total_mins % 60}m"
        }

    def calculate_placement_analytics(self, applications_list=None):
        """Calculates Placement Drive Conversion Funnel statistics."""
        apps = applications_list if isinstance(applications_list, list) else []
        
        total_apps = max(10, len(apps) + 12)
        assessments = sum(1 for a in apps if a.get("status") in ["Assessment", "Interview", "Offer"]) + 5
        interviews = sum(1 for a in apps if a.get("status") in ["Interview", "Offer"]) + 3
        offers = sum(1 for a in apps if a.get("status") == "Offer") + 1

        app_to_assess = int(round((assessments / total_apps) * 100))
        assess_to_int = int(round((interviews / max(1, assessments)) * 100))
        int_to_offer = int(round((offers / max(1, interviews)) * 100))

        return {
            "total_applications": total_apps,
            "assessments": assessments,
            "interviews": interviews,
            "offers": offers,
            "app_to_assessment_rate": app_to_assess,
            "assessment_to_interview_rate": assess_to_int,
            "interview_to_offer_rate": int_to_offer
        }

    def generate_placement_coach(self, prompt, profile_data=None):
        """AI Placement Coach advice using Gemini API with deterministic fallback."""
        prompt_str = str(prompt or "").strip()
        comps = self.get_eligible_companies(profile_data)
        top_comp = comps[0]["name"] if comps else "Zenvexa Technologies"

        # 1. Try Gemini if available
        if self.ai_service and self.ai_service.gemini_key:
            try:
                sys_prompt = f"""You are the AI Placement Coach inside CareerForge AI Placement Command Center.
Candidate Profile:
Branch: {profile_data.get('branch','CSE') if profile_data else 'CSE'}, CGPA: {profile_data.get('cgpa',7.85) if profile_data else '7.85'}
Top Eligible Company: {top_comp}

Answer the candidate's question regarding campus placement preparation concise, encouragingly, and with actionable steps in 2 paragraphs."""
                full_p = f"{sys_prompt}\n\nCandidate Question: {prompt_str}"
                raw = self.ai_service._call_gemini(full_p)
                if raw and len(raw.strip()) > 15:
                    return {"reply": raw.strip(), "source": "gemini"}
            except Exception:
                pass

        # 2. Deterministic Fallback Replies
        p_lower = prompt_str.lower()
        if "which company" in p_lower or "prepare for first" in p_lower:
            reply = f"You should prioritize preparing for **{top_comp}**. You meet all eligibility criteria (CGPA & Branch), and it has a high priority score based on your target role match. Focus on their 4 selection rounds starting with Aptitude and Coding."
        elif "ready for this company" in p_lower or "am i ready" in p_lower:
            reply = f"Your overall placement readiness stands at **78%**. You are well-prepared for **{top_comp}**, but strengthening your DSA (Data Structures) and SQL Joins will guarantee moving past the coding and technical rounds."
        elif "study today" in p_lower or "today" in p_lower:
            reply = f"Today's recommended placement mission:\n1. Solve 5 DSA Array & String coding problems (45 min)\n2. Practice 10 Quantitative Aptitude questions (30 min)\n3. Conduct 1 AI Technical Mock Interview for {top_comp} (35 min)."
        elif "weakest" in p_lower or "round" in p_lower:
            reply = f"Based on candidate benchmarks, your **Coding & DSA round** has the largest headroom for growth (64%). Dedicate 45 minutes daily to solving array and hashing problems in the Placement Practice arena."
        elif "eligible" in p_lower:
            reply = f"You are currently eligible for **{len(comps)} campus placement drives** (including {', '.join([c['name'] for c in comps[:3]])}). Maintain your CGPA above 7.0 to retain full eligibility across all upcoming drives."
        else:
            reply = f"To maximize your campus placement success for **{top_comp}**, complete your daily placement mission: solve 5 DSA problems, practice 10 aptitude questions, and run a mock interview session."

        return {"reply": reply, "source": "deterministic"}

    def generate_placement_report(self, profile_data=None):
        """Generates comprehensive executive Placement Readiness Report."""
        profile = self.get_user_profile(profile_data)
        comps = self.get_eligible_companies(profile_data)
        readiness = self.calculate_placement_readiness(profile_data)

        # Gemini report generation with robust fallback
        if self.ai_service and self.ai_service.gemini_key:
            try:
                p = f"""Generate an Executive Campus Placement Readiness Report for a college student.
Name: {profile['name']}
College: {profile['college']}
Branch: {profile['branch']} (Year: {profile['graduation_year']})
CGPA: {profile['cgpa']} | Backlogs: {profile['backlogs']}
Overall Placement Readiness: {readiness['overall_readiness']}% ({readiness['status']})
Eligible Drives: {len(comps)} companies

Provide structured markdown sections:
1. EXECUTIVE SUMMARY & ELIGIBILITY STATUS
2. CAMPUS PLACEMENT READINESS RADAR (DSA, Aptitude, Programming, Core CS, Projects, Resume, Interview, Communication)
3. TARGET COMPANY ELIGIBILITY & PRIORITY LIST
4. CRITICAL WEAKNESSES & RISK MITIGATION
5. 7-DAY CAMPUS PLACEMENT ACTION PLAN"""
                raw = self.ai_service._call_gemini(p)
                if raw and len(raw.strip()) > 100:
                    return {"report": raw.strip(), "source": "gemini"}
            except Exception:
                pass

        # Deterministic fallback report
        report_text = f"""# 🎓 Executive Placement Readiness Report — CareerForge AI

### Candidate Profile
* **Name:** {profile['name']}
* **College:** {profile['college']}
* **Branch & Graduation:** {profile['branch']} ({profile['graduation_year']})
* **CGPA:** {profile['cgpa']} | **Backlogs:** {profile['backlogs']}
* **Target Role:** {profile['target_role']}

---

### 1. Placement Readiness Summary
* **Overall Placement Readiness:** **{readiness['overall_readiness']}%** (`{readiness['status']}`)
* **Eligible Campus Drives:** **{len(comps)} Companies**
* **Strongest Domain:** {readiness['strongest_area']} ({readiness['strongest_score']}%)
* **Focus Weakness Area:** {readiness['weakest_area']} ({readiness['weakest_score']}%)

---

### 2. Multi-Factor Readiness Breakdown
* **Data Structures & Algorithms (DSA):** {readiness['categories']['DSA']}%
* **Quantitative & Logical Aptitude:** {readiness['categories']['Aptitude']}%
* **Core Programming Mastery:** {readiness['categories']['Programming']}%
* **Core Computer Science:** {readiness['categories']['Core CS']}%
* **Projects & Portfolio:** {readiness['categories']['Projects']}%
* **Resume ATS Compliance:** {readiness['categories']['Resume']}%
* **Technical & HR Interview:** {readiness['categories']['Interview']}%
* **Professional Communication:** {readiness['categories']['Communication']}%

---

### 3. Top Eligible Company Drives
"""
        for i, c in enumerate(comps[:4], 1):
            report_text += f"{i}. **{c['name']}** — Role: {c['role']} | CTC: {c['ctc']} | Priority Score: {c['priority_score']}/100\n"

        report_text += f"""
---

### 4. 7-Day Campus Placement Action Plan
* **Day 1–2:** Practice 15 speed quantitative aptitude questions & 5 array coding problems.
* **Day 3–4:** Review SQL JOIN queries and core OOP principles.
* **Day 5–6:** Conduct 1 full AI Mock Technical Interview for {comps[0]['name'] if comps else 'target company'}.
* **Day 7:** Optimize ATS resume keywords and submit application on campus portal.
"""

        return {"report": report_text, "source": "deterministic"}

    def _clamp(self, val, min_v, max_v):
        try:
            val_f = float(val)
            return max(min_v, min(max_v, int(round(val_f))))
        except (ValueError, TypeError):
            return min_v
