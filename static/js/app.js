document.addEventListener('DOMContentLoaded', () => {
    // Initialize Form Handler
    if (window.CareerFormHandler) {
        window.CareerFormHandler.init();
    }

    // View Elements
    const heroSection = document.getElementById('heroSection');
    const formSection = document.getElementById('formSection');
    const loaderSection = document.getElementById('loaderSection');
    const dashboardSection = document.getElementById('dashboardSection');

    // Navigation Buttons
    const navHomeBtn = document.getElementById('navHomeBtn');
    const navAnalyzeBtn = document.getElementById('navAnalyzeBtn');
    const startCareerPlanBtn = document.getElementById('startCareerPlanBtn');
    const quickResumeBtn = document.getElementById('quickResumeBtn');
    const backToHeroBtn = document.getElementById('backToHeroBtn');
    const careerForm = document.getElementById('careerForm');

    function showView(viewEl) {
        [heroSection, formSection, loaderSection, dashboardSection].forEach(el => {
            if (el) el.classList.add('hidden');
        });
        if (viewEl) viewEl.classList.remove('hidden');
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    window.AppRouter = {
        showSection: function(secId) {
            const sec = document.getElementById(secId);
            if (sec) showView(sec);
        },
        switchTab: function(tabId) {
            showView(dashboardSection);
            const btn = document.querySelector(`.tab-btn[data-tab="${tabId}"]`);
            if (btn) btn.click();
        }
    };


    if (navHomeBtn) navHomeBtn.addEventListener('click', () => showView(heroSection));
    if (navAnalyzeBtn) navAnalyzeBtn.addEventListener('click', () => showView(formSection));
    if (startCareerPlanBtn) startCareerPlanBtn.addEventListener('click', () => showView(formSection));
    if (quickResumeBtn) quickResumeBtn.addEventListener('click', () => showView(formSection));
    if (backToHeroBtn) backToHeroBtn.addEventListener('click', () => showView(heroSection));

    // Dashboard Tab Switching
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            tabBtns.forEach(b => b.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));

            btn.classList.add('active');
            const targetTab = document.getElementById(btn.dataset.tab);
            if (targetTab) targetTab.classList.add('active');
        });
    });

    // Form Submission Handler
    if (careerForm) {
        careerForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const name = document.getElementById('candidateName').value.trim() || 'Candidate';
            const targetRole = document.getElementById('targetRole').value;
            const hoursPerDay = document.getElementById('hoursPerDay').value;
            const currentSkills = window.CareerFormHandler ? window.CareerFormHandler.skills : [];
            const resumeFile = document.getElementById('resumeFile').files[0];

            if (!targetRole) {
                alert('Please select a target placement role.');
                return;
            }

            showView(loaderSection);

            try {
                // 1. Fetch Career Plan & Skill Gap Analysis
                const planPromise = fetch('/api/career-plan', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        name: name,
                        target_role: targetRole,
                        current_skills: currentSkills,
                        hours_per_day: hoursPerDay
                    })
                }).then(res => res.json());

                // 2. Fetch Visual Roadmap Flowchart
                const roadmapPromise = fetch(`/api/roadmap/${targetRole}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ current_skills: currentSkills })
                }).then(res => res.json());

                // 3. Fetch Role-Specific Job Search Links
                const jobsPromise = fetch(`/api/jobs/${targetRole}`).then(res => res.json());

                // 4. Resume File Analysis (If file selected)
                let resumePromise = Promise.resolve(null);
                if (resumeFile) {
                    const formData = new FormData();
                    formData.append('resume_file', resumeFile);
                    formData.append('target_role', targetRole);
                    formData.append('current_skills', currentSkills.join(','));

                    resumePromise = fetch('/api/analyze-resume', {
                        method: 'POST',
                        body: formData
                    }).then(res => res.json());
                }

                // Execute Loader Steps & Await API Calls
                window.CareerFormHandler.animateLoaderSteps(async () => {
                    const [planRes, roadmapRes, jobsRes, resumeRes] = await Promise.all([
                        planPromise, roadmapPromise, jobsPromise, resumePromise
                    ]);

                    if (planRes && planRes.success) {
                        window.DashboardRenderer.render(planRes.data);
                    }

                    if (roadmapRes && roadmapRes.success) {
                        window.DashboardRenderer.renderRoadmapNodes(roadmapRes.data);
                    }

                    if (jobsRes && jobsRes.success) {
                        window.DashboardRenderer.renderJobPortals(jobsRes.data);
                    }

                    if (resumeRes && resumeRes.success) {
                        window.DashboardRenderer.renderATSResults(resumeRes.data);
                    } else if (!resumeFile) {
                        // Fallback default ATS view if no file uploaded
                        window.DashboardRenderer.renderATSResults({
                            ats_score: 78,
                            score_breakdown: {
                                keyword_match: 75,
                                skills_match: 80,
                                role_relevance: 80,
                                structure: 90,
                                formatting: 90
                            },
                            bullet_rewrites: [
                                {
                                    original: "Developed a website using Python.",
                                    suggested: "Engineered a Flask-based RESTful backend service using Python, implementing structured JSON routes and error handling.",
                                    reasoning: "Uses action verbs and specifies technical framework details."
                                }
                            ]
                        });
                    }

                    showView(dashboardSection);
                });

            } catch (err) {
                console.error("API error:", err);
                alert("An error occurred while generating your career plan. Please try again.");
                showView(formSection);
            }
        });
    }
});
