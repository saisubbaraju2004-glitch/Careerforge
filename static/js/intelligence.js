document.addEventListener('DOMContentLoaded', function () {
    initCareerIntelligence();
});

function initCareerIntelligence() {
    // 1. Gather profile context from localStorage or fallback defaults
    const storedPlan = JSON.parse(localStorage.getItem('careerforge_plan_data') || '{}');
    const storedProfile = JSON.parse(localStorage.getItem('careerforge_profile') || '{}');
    const storedInterview = JSON.parse(localStorage.getItem('careerforge_interview_state') || '{}');
    const storedApps = JSON.parse(localStorage.getItem('careerforge_applications') || '[]');

    const payload = {
        target_role: storedPlan.target_role || storedProfile.target_role || "Python Backend Developer",
        current_skills: storedPlan.strong_skills || storedProfile.current_skills || ["Python", "Flask", "HTML", "CSS", "SQL"],
        missing_skills: storedPlan.missing_skills || ["Docker", "REST APIs", "PostgreSQL"],
        readiness_score: storedPlan.readiness_score || 72,
        ats_score: storedProfile.ats_score || 76,
        interview_score: storedInterview.last_score || 62,
        roadmap_progress: storedProfile.roadmap_progress || 45,
        plan_progress: storedProfile.plan_progress || 60,
        applications: storedApps.length > 0 ? storedApps.length : 5
    };

    // 2. Fetch Career Intelligence API
    fetch('/api/career-intelligence', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    })
    .then(res => res.json())
    .then(data => {
        if (data.success && data.data) {
            renderIntelligenceDashboard(data.data);
        } else {
            console.warn("Career Intelligence API returned fallback or error:", data);
        }
    })
    .catch(err => {
        console.error("Error fetching career intelligence:", err);
    });
}

function renderIntelligenceDashboard(intel) {
    // 1. Header & Hero Readiness Level
    const roleElem = document.getElementById('intelTargetRole');
    if (roleElem) roleElem.textContent = intel.target_role;

    const scoreElem = document.getElementById('intelReadinessScore');
    if (scoreElem) animateCounter(scoreElem, intel.readiness_score);

    const levelElem = document.getElementById('intelReadinessLevel');
    if (levelElem) levelElem.textContent = intel.readiness_level;

    const descElem = document.getElementById('intelLevelDesc');
    if (descElem) descElem.textContent = intel.level_description;

    // 2. Next Best Action Card
    if (intel.next_action) {
        const titleElem = document.getElementById('intelActionTitle');
        if (titleElem) titleElem.textContent = intel.next_action.title || intel.next_action.action;

        const whyElem = document.getElementById('intelActionWhy');
        if (whyElem) whyElem.textContent = intel.next_action.why;

        const impactElem = document.getElementById('intelImpactBadge');
        if (impactElem) impactElem.textContent = intel.next_action.estimated_impact;

        const btnElem = document.getElementById('intelActionBtn');
        if (btnElem && intel.next_action.link) {
            btnElem.setAttribute('href', intel.next_action.link);
        }
    }

    // 3. Readiness Breakdown
    if (intel.readiness_breakdown) {
        const listElem = document.getElementById('breakdownList');
        if (listElem && intel.readiness_breakdown.categories) {
            listElem.innerHTML = '';
            for (const [catName, score] of Object.entries(intel.readiness_breakdown.categories)) {
                const row = document.createElement('div');
                row.className = 'breakdown-item';
                row.innerHTML = `
                    <div class="breakdown-meta">
                        <span class="breakdown-name">${catName}</span>
                        <span class="breakdown-val">${score}%</span>
                    </div>
                    <div class="breakdown-track">
                        <div class="breakdown-fill" style="width: 0%" data-target="${score}%"></div>
                    </div>
                `;
                listElem.appendChild(row);
            }
            // Animate progress fills
            setTimeout(() => {
                document.querySelectorAll('.breakdown-fill').forEach(fill => {
                    fill.style.width = fill.getAttribute('data-target');
                });
            }, 100);
        }

        const strongElem = document.getElementById('strongestAreaText');
        if (strongElem) strongElem.textContent = intel.readiness_breakdown.strongest_summary;

        const blockerElem = document.getElementById('biggestBlockerText');
        if (blockerElem) blockerElem.textContent = intel.readiness_breakdown.blocker_summary;
    }

    // 4. Readiness Simulator
    const simCur = document.getElementById('simCurrentScore');
    if (simCur) simCur.textContent = `${intel.readiness_score}%`;

    const simPot = document.getElementById('simPotentialScore');
    if (simPot) simPot.textContent = `${intel.potential_score}%`;

    const simBoostList = document.getElementById('simBoostList');
    if (simBoostList && intel.simulation_breakdown) {
        simBoostList.innerHTML = '';
        intel.simulation_breakdown.forEach(item => {
            const div = document.createElement('div');
            div.className = 'sim-boost-item';
            div.innerHTML = `
                <span>${item.label}</span>
                <span class="sim-boost-badge">${item.boost}</span>
            `;
            simBoostList.appendChild(div);
        });
    }

    // 5. AI Insights
    const insightsList = document.getElementById('insightsList');
    if (insightsList && intel.insights) {
        insightsList.innerHTML = '';
        intel.insights.forEach(insight => {
            const card = document.createElement('div');
            card.className = `insight-card ${insight.type || 'positive'}`;
            card.innerHTML = `
                <span class="insight-icon">${insight.icon || '🟢'}</span>
                <span>${insight.text}</span>
            `;
            insightsList.appendChild(card);
        });
    }

    // 6. Career Milestones Journey
    const timelineElem = document.getElementById('milestonesTimeline');
    if (timelineElem && intel.milestones) {
        timelineElem.innerHTML = '';
        intel.milestones.forEach(m => {
            const item = document.createElement('div');
            item.className = `milestone-item ${m.completed ? 'completed' : ''}`;
            item.innerHTML = `
                <div class="milestone-icon">
                    <i class="fa-solid ${m.completed ? 'fa-check' : 'fa-circle'}"></i>
                </div>
                <div class="milestone-content">
                    <div class="milestone-title">${m.title}</div>
                    <div class="milestone-desc">${m.description}</div>
                </div>
            `;
            timelineElem.appendChild(item);
        });
    }

    // 7. Weekly Review & Next Week Priorities
    if (intel.weekly_review) {
        const w = intel.weekly_review;
        if (document.getElementById('statSkills')) document.getElementById('statSkills').textContent = `+${w.skills_improved}`;
        if (document.getElementById('statInterview')) document.getElementById('statInterview').textContent = w.interview_sessions;
        if (document.getElementById('statApps')) document.getElementById('statApps').textContent = w.applications;
        if (document.getElementById('statATS')) document.getElementById('statATS').textContent = w.resume_score_trend;
        if (document.getElementById('statReadiness')) document.getElementById('statReadiness').textContent = w.readiness_trend;
        if (document.getElementById('statTasks')) document.getElementById('statTasks').textContent = w.tasks_completed;
    }

    const priorityList = document.getElementById('priorityList');
    if (priorityList && intel.next_week_priorities) {
        priorityList.innerHTML = '';
        intel.next_week_priorities.forEach(p => {
            const li = document.createElement('li');
            li.textContent = p;
            priorityList.appendChild(li);
        });
    }
}

function animateCounter(element, target) {
    let current = 0;
    const duration = 1000;
    const stepTime = 20;
    const steps = duration / stepTime;
    const increment = target / steps;

    const timer = setInterval(() => {
        current += increment;
        if (current >= target) {
            element.textContent = target;
            clearInterval(timer);
        } else {
            element.textContent = Math.floor(current);
        }
    }, stepTime);
}
