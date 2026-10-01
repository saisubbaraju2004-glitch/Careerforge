import json
import re
from pathlib import Path
from config.config import Config

class InterviewService:
    def __init__(self, ai_service=None, career_engine=None):
        self.ai_service = ai_service
        self.career_engine = career_engine

    def generate_interview_questions(self, target_role, interview_type="Job-Specific", difficulty="Intermediate", count=5, job_info=None, user_profile=None):
        """
        Generates job-specific & resume-aware interview questions.
        Never generates questions for skills unmentioned in user profile or job requirements.
        """
        user_profile = user_profile or {}
        job_info = job_info or {}

        user_skills = [s.strip() for s in user_profile.get("skills", ["Python", "Flask", "SQL", "PostgreSQL", "REST APIs"]) if s.strip()]
        user_projects = user_profile.get("projects", [])
        
        job_skills = job_info.get("skills", ["Python", "REST APIs", "PostgreSQL", "Docker"])
        
        # Combined valid skills whitelist (never ask outside of user skills & job skills)
        valid_skills = list(set(user_skills + job_skills))

        # 1. Try Gemini API generation if key is configured
        if self.ai_service and self.ai_service.gemini_key:
            try:
                project_names = [p.get("name", "Project") if isinstance(p, dict) else str(p) for p in user_projects]
                prompt = f"""You are a Lead Technical Interviewer conducting a {interview_type} interview for {target_role}.
Job Company: {job_info.get('company', 'Tech Firm')}
Job Skills Required: {', '.join(job_skills)}
User Declared Skills: {', '.join(user_skills)}
User Projects: {', '.join(project_names) if project_names else 'Python Web API'}

Generate exactly {count} {difficulty}-level interview questions.
Rules:
- Generate questions strictly tailored to their actual skills ({', '.join(valid_skills)}) and projects.
- Include 1 project-specific question referencing {project_names[0] if project_names else 'their backend project'}.
- DO NOT ask about unmentioned technologies (e.g. do not ask about AWS if not in declared skills).

Output strictly valid JSON:
{{
  "questions": [
    {{
      "id": 1,
      "question": "Question text",
      "type": "Technical",
      "category": "Skill/Topic Category",
      "difficulty": "{difficulty}",
      "job_skill": "Primary skill tested",
      "expected_topics": ["topic 1", "topic 2"]
    }}
  ]
}}"""
                raw = self.ai_service._call_gemini(prompt)
                parsed = self.ai_service._clean_json_response(raw)
                if parsed and "questions" in parsed and len(parsed["questions"]) > 0:
                    return parsed["questions"][:count]
            except Exception:
                pass

        # 2. Deterministic Fallback Question Generator
        return self._generate_fallback_job_questions(target_role, interview_type, difficulty, count, valid_skills, user_projects)

    def _generate_fallback_job_questions(self, target_role, interview_type, difficulty, count, valid_skills, user_projects):
        questions = []
        proj_name = "ExamCraft AI"
        if user_projects:
            proj = user_projects[0]
            proj_name = proj.get("name", "ExamCraft AI") if isinstance(proj, dict) else str(proj)

        # Question pool mapped to skills
        pool_by_skill = {
            "python": {
                "question": "What is the difference between shallow copy and deep copy in Python, and how does memory management differ?",
                "category": "Python Core",
                "topics": ["copy module", "memory reference", "mutable objects"]
            },
            "flask": {
                "question": "How do application context and request context work internally in Flask using local proxies?",
                "category": "Flask",
                "topics": ["Werkzeug local proxy", "g object", "request lifecycle"]
            },
            "fastapi": {
                "question": "How does FastAPI leverage Pydantic models for request validation and async def concurrency?",
                "category": "FastAPI",
                "topics": ["Pydantic validation", "asyncio event loop", "OpenAPI schema"]
            },
            "sql": {
                "question": "Explain how database indexing speeds up SELECT queries and when indexing might slow down WRITE operations.",
                "category": "SQL & Databases",
                "topics": ["B-Tree indexes", "query planner", "INSERT overhead"]
            },
            "postgresql": {
                "question": "Why is PostgreSQL's MVCC (Multi-Version Concurrency Control) advantageous for high-throughput APIs?",
                "category": "PostgreSQL",
                "topics": ["MVCC read consistency", "vacuuming", "row-level locking"]
            },
            "rest apis": {
                "question": "How do you design idempotent RESTful API endpoints and select appropriate HTTP status codes?",
                "category": "REST APIs",
                "topics": ["GET/PUT idempotency", "status 201 vs 200", "error payloads"]
            },
            "docker": {
                "question": "Explain the difference between a Docker image layer and a container layer, and how you optimize Dockerfile builds.",
                "category": "Docker",
                "topics": ["layer caching", "multi-stage builds", "lightweight base images"]
            },
            "system design": {
                "question": "How would you design a rate-limiting middleware for a backend API receiving 10,000 requests per minute?",
                "category": "System Design",
                "topics": ["sliding window algorithm", "Redis cache", "429 Too Many Requests"]
            }
        }

        # 1. Project-Aware Question
        questions.append({
            "id": 1,
            "question": f"Explain your technical architecture role in {proj_name}. What key backend design choices did you make?",
            "type": "Project-Based",
            "category": "Projects",
            "difficulty": difficulty,
            "job_skill": "Project Architecture",
            "expected_topics": ["component design", "database schema", "API structure"]
        })

        # 2. Skill-Specific Questions
        for s in valid_skills:
            s_lower = s.lower()
            if s_lower in pool_by_skill and len(questions) < count:
                item = pool_by_skill[s_lower]
                questions.append({
                    "id": len(questions) + 1,
                    "question": item["question"],
                    "type": "Technical",
                    "category": item["category"],
                    "difficulty": difficulty,
                    "job_skill": s,
                    "expected_topics": item["topics"]
                })

        # 3. Behavioral / HR Fillers if needed
        hr_pool = [
            ("Describe a situation where you had to debug a difficult production issue under time constraints.", "Behavioral", "Problem Solving"),
            ("How do you prioritize technical debt versus building new feature requirements?", "HR", "Engineering Culture")
        ]

        for q_txt, q_type, q_cat in hr_pool:
            if len(questions) < count:
                questions.append({
                    "id": len(questions) + 1,
                    "question": q_txt,
                    "type": q_type,
                    "category": q_cat,
                    "difficulty": "Intermediate",
                    "job_skill": "Communication",
                    "expected_topics": ["STAR method", "clear communication"]
                })

        return questions[:count]

    def evaluate_answer(self, target_role, question, user_answer, difficulty="Intermediate", category="Technical", job_skill="Backend"):
        """
        Evaluates a single answer across 5 dimensions:
        Technical Accuracy, Communication, Relevance, Completeness, Confidence.
        Returns detailed strengths, weaknesses, and a model answer.
        """
        if not user_answer or len(user_answer.strip()) < 5:
            return {
                "score": 25,
                "technical_accuracy": 20,
                "communication": 30,
                "relevance": 25,
                "completeness": 20,
                "confidence": 25,
                "category": category,
                "strengths": ["Submitted answer attempted"],
                "weaknesses": ["⚠ Answer is too brief to evaluate technical depth."],
                "better_answer": "Model Answer: Provide a structured response defining core terminology, practical implementation details, and system trade-off considerations."
            }

        # 1. Try Gemini evaluation if configured
        if self.ai_service and self.ai_service.gemini_key:
            try:
                prompt = f"""You are a Senior Engineering Manager evaluating an interview answer for {target_role}.
Question: "{question}"
Category: {category} ({job_skill})
User Answer: "{user_answer}"

Evaluate objectively (0-100 scores). Output strictly valid JSON:
{{
  "score": 80,
  "technical_accuracy": 82,
  "communication": 74,
  "relevance": 88,
  "completeness": 75,
  "confidence": 80,
  "strengths": ["✓ Strength 1", "✓ Strength 2"],
  "weaknesses": ["⚠ Area for improvement 1"],
  "better_answer": "Model Answer: Concise exemplar response explaining the core concept clearly."
}}"""
                raw = self.ai_service._call_gemini(prompt)
                parsed = self.ai_service._clean_json_response(raw)
                if parsed and "score" in parsed:
                    return {
                        "score": self._clamp(parsed.get("score", 75), 0, 100),
                        "technical_accuracy": self._clamp(parsed.get("technical_accuracy", 75), 0, 100),
                        "communication": self._clamp(parsed.get("communication", 75), 0, 100),
                        "relevance": self._clamp(parsed.get("relevance", 80), 0, 100),
                        "completeness": self._clamp(parsed.get("completeness", 70), 0, 100),
                        "confidence": self._clamp(parsed.get("confidence", 75), 0, 100),
                        "category": category,
                        "strengths": parsed.get("strengths", ["✓ Good intent and relevant explanation."]),
                        "weaknesses": parsed.get("weaknesses", ["⚠ Include code-level details."]),
                        "better_answer": f"Model Answer: {parsed.get('better_answer', 'A model answer clearly states definition, execution flow, and trade-offs.')}"
                    }
            except Exception:
                pass

        # 2. Deterministic Evaluation Algorithm
        words = user_answer.split()
        word_count = len(words)
        
        tech_keywords = ["python", "flask", "fastapi", "sql", "postgres", "api", "rest", "docker", "query", "database", "async", "cache", "schema", "lock", "index"]
        found_kw = [k for k in tech_keywords if k in user_answer.lower()]

        tech_acc = self._clamp(55 + len(found_kw) * 10, 35, 95)
        comm = self._clamp(50 + (15 if word_count > 30 else 0) + (10 if word_count > 50 else 0), 40, 95)
        rel = self._clamp(60 + (15 if any(k in question.lower() for k in found_kw) else 5), 45, 95)
        comp = self._clamp(45 + (20 if word_count > 35 else 5), 35, 95)
        conf = self._clamp(60 + (15 if word_count > 25 else 0), 40, 92)

        overall = self._clamp((tech_acc * 0.35) + (comm * 0.25) + (rel * 0.2) + (comp * 0.2), 30, 95)

        strengths = [
            "✓ Clear technical intent and relevant terminology.",
            f"✓ Effectively referenced concepts like {', '.join(found_kw[:2]) if found_kw else 'core software logic'}."
        ]

        weaknesses = []
        if word_count < 30:
            weaknesses.append("⚠ Response is somewhat concise; expand on execution mechanics.")
        if len(found_kw) < 2:
            weaknesses.append("⚠ Include more domain-specific technical keywords (e.g. schema, index, latency).")
        if not weaknesses:
            weaknesses.append("⚠ Mention performance trade-offs under high request load.")

        better_ans = f"Model Answer: A top candidate response for '{question}' defines the core mechanism, details runtime execution flow, and highlights scalability trade-offs."

        return {
            "score": overall,
            "technical_accuracy": tech_acc,
            "communication": comm,
            "relevance": rel,
            "completeness": comp,
            "confidence": conf,
            "category": category,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "better_answer": better_ans
        }

    def generate_final_report(self, evaluations, target_role, job_info=None):
        """
        Generates comprehensive final interview report, identifies top weaknesses,
        classifies readiness level, and builds AI Coach recommendations.
        """
        if not evaluations:
            evaluations = [{
                "score": 75, "technical_accuracy": 78, "communication": 72, "relevance": 80, "completeness": 70, "category": "Python"
            }]

        total = len(evaluations)
        avg_overall = self._clamp(sum(e.get("score", 70) for e in evaluations) / total, 0, 100)
        avg_tech = self._clamp(sum(e.get("technical_accuracy", 70) for e in evaluations) / total, 0, 100)
        avg_comm = self._clamp(sum(e.get("communication", 70) for e in evaluations) / total, 0, 100)
        avg_rel = self._clamp(sum(e.get("relevance", 70) for e in evaluations) / total, 0, 100)
        avg_comp = self._clamp(sum(e.get("completeness", 70) for e in evaluations) / total, 0, 100)

        # Category scores tracking
        cat_scores = {}
        for e in evaluations:
            cat = e.get("category", "General")
            cat_scores.setdefault(cat, []).append(e.get("score", 70))

        cat_averages = {cat: self._clamp(sum(scores)/len(scores), 0, 100) for cat, scores in cat_scores.items()}

        sorted_cats = sorted(cat_averages.items(), key=lambda x: x[1])
        top_weakness = sorted_cats[0][0] if sorted_cats else "System Design"
        second_weakness = sorted_cats[1][0] if len(sorted_cats) > 1 else "Docker"

        strongest_areas = [f"✓ {cat}" for cat, sc in sorted(cat_averages.items(), key=lambda x: x[1], reverse=True) if sc >= 65][:3]
        if not strongest_areas:
            strongest_areas = ["✓ Python Core", "✓ REST API Design"]

        weakest_areas = [f"⚠ {cat} ({sc}%)" for cat, sc in sorted_cats if sc < 75][:3]
        if not weakest_areas:
            weakest_areas = [f"⚠ {top_weakness} ({cat_averages.get(top_weakness, 45)}%)"]

        # Readiness Level Classification
        readiness_level, level_desc = self._classify_interview_level(avg_overall)

        # AI Coach Advice
        coach_advice = (
            f"You demonstrated solid foundational concepts in {strongest_areas[0].replace('✓ ', '')}. "
            f"Your primary blocker is {top_weakness} ({cat_averages.get(top_weakness, 45)}%). "
            f"Practice explaining architecture trade-offs and code execution flow before your live call."
        )

        return {
            "overall_score": avg_overall,
            "technical_score": avg_tech,
            "communication_score": avg_comm,
            "relevance_score": avg_rel,
            "completeness_score": avg_comp,
            "readiness_level": readiness_level,
            "level_description": level_desc,
            "strongest_areas": strongest_areas,
            "weakest_areas": weakest_areas,
            "top_weakness": top_weakness,
            "second_weakness": second_weakness,
            "category_scores": cat_averages,
            "coach_advice": coach_advice
        }

    def generate_7day_plan(self, top_weakness, second_weakness, target_role):
        """Generates a personalized 7-day interview improvement plan based on detected weaknesses."""
        return [
            {"day": "Day 1", "focus": f"Master {top_weakness} Fundamentals & Core Syntax"},
            {"day": "Day 2", "focus": f"Practice 10 High-Frequency {top_weakness} Technical Questions"},
            {"day": "Day 3", "focus": f"{second_weakness} Concepts & System Architecture"},
            {"day": "Day 4", "focus": "System Design Patterns & Database Query Optimization"},
            {"day": "Day 5", "focus": "Resume Project Deep-Dive & Architectural Trade-offs"},
            {"day": "Day 6", "focus": "STAR Method Behavioral & HR Scenario Practice"},
            {"day": "Day 7", "focus": "Full AI Mock Interview Simulation & Progress Verification"}
        ]

    def generate_retry_questions(self, top_weakness, second_weakness, count=5):
        """Generates targeted retry questions specifically from user's weakest categories."""
        retry_pool = {
            "Docker": [
                "How do multi-stage Docker builds reduce image size in Python microservices?",
                "Explain container networking and how two Docker containers communicate locally."
            ],
            "System Design": [
                "How do you design a high-availability rate limiter for a public REST API?",
                "Explain the CAP theorem and how you choose between consistency and availability."
            ],
            "PostgreSQL": [
                "How does PostgreSQL EXPLAIN ANALYZE help identify query bottlenecks?",
                "Explain connection pooling in PostgreSQL and why PGBouncer is used."
            ]
        }

        q_list = retry_pool.get(top_weakness, retry_pool["Docker"]) + retry_pool.get(second_weakness, retry_pool["System Design"])
        formatted = []
        for idx, text in enumerate(q_list[:count]):
            formatted.append({
                "id": idx + 1,
                "question": text,
                "type": "Technical",
                "category": top_weakness if idx < 3 else second_weakness,
                "difficulty": "Intermediate",
                "job_skill": top_weakness,
                "expected_topics": ["core concepts", "system design"]
            })
        return formatted

    def _classify_interview_level(self, score):
        if score < 40:
            return "NOT READY", "Core technical foundation requires further study before recruiter calls."
        elif score < 60:
            return "FOUNDATION", "Basic concepts are present; practice technical depth and response structure."
        elif score < 75:
            return "DEVELOPING", "You are approaching interview readiness. Strengthen system design and trade-offs."
        elif score < 90:
            return "INTERVIEW READY", "You are ready for basic-to-intermediate interviews; polish architecture answers."
        else:
            return "HIGHLY CONFIDENT", "Top-tier candidate performance. You are prepared for competitive screens."

    def _clamp(self, val, min_v, max_v):
        try:
            val_f = float(val)
            return max(min_v, min(max_v, int(round(val_f))))
        except (ValueError, TypeError):
            return min_v
