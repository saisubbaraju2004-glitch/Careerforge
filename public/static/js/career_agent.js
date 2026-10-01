document.addEventListener('DOMContentLoaded', () => {
    initCareerAgent();
    setupAgentChatListener();
});

let currentAgentContext = {};
let selectedTimeMinutes = 60;

function getStoredContext() {
    const profile = JSON.parse(localStorage.getItem('careerforge_profile') || '{}');
    const plan = JSON.parse(localStorage.getItem('careerforge_plan_data') || '{}');
    const resume = JSON.parse(localStorage.getItem('careerforge_resume_data') || '{}');
    const intHist = JSON.parse(localStorage.getItem('careerforge_interview_history') || '[]');
    const apps = JSON.parse(localStorage.getItem('careerforge_applications') || '[]');
    const intState = JSON.parse(localStorage.getItem('careerforge_interview_state') || '{}');

    const latestInt = intHist.length > 0 ? intHist[0].score : (intState.last_score || 78);
    const weakInt = intHist.length > 0 && intHist[0].weaknesses ? [intHist[0].weaknesses] : ["Docker", "System Architecture"];

    return {
        target_role: plan.target_role || profile.target_role || "Python Backend Developer",
        readiness_score: profile.readinessScore || 78,
        ats_score: profile.atsScore || 84,
        job_match_score: profile.jobMatchScore || 87,
        interview_score: latestInt,
        skills: profile.current_skills || plan.strong_skills || ["Python", "Flask", "FastAPI", "SQL", "PostgreSQL", "REST APIs"],
        missing_skills: profile.missing_skills || ["Docker", "Machine Learning", "Kubernetes"],
        applications: apps,
        interview_weaknesses: weakInt,
        resume_gaps: ["Quantifiable Impact Metrics", "Cloud Certifications"]
    };
}

function initCareerAgent() {
    currentAgentContext = getStoredContext();
    loadStreakAndNotifications();

    fetch('/api/career-agent/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(currentAgentContext)
    })
    .then(res => res.json())
    .then(data => {
        if (data.success && data.data) {
            const resData = data.data;
            renderHeroAction(resData.primary_action);
            renderSnapshot(resData.snapshot);
            renderTop3Actions(resData.top_3_actions);
            renderMomentum(resData.momentum);
            renderRisks(resData.risks);
        }
    })
    .catch(err => console.error("Agent analyze failed:", err));

    loadDailyMission(selectedTimeMinutes);
    loadWeeklyReview();
    renderCareerGoal();
}

function loadStreakAndNotifications() {
    const streak = parseInt(localStorage.getItem('careerforge_streak') || '7');
    const streakEl = document.getElementById('streakCount');
    if (streakEl) streakEl.textContent = streak;
}

function renderHeroAction(action) {
    if (!action) return;
    document.getElementById('primaryActionTitle').textContent = action.action;
    document.getElementById('primaryActionReason').textContent = action.reason;
    document.getElementById('primaryPriorityBadge').textContent = `${action.priority} PRIORITY`;

    document.getElementById('primaryPriorityBadge').className = action.priority === 'HIGH' ? 'badge badge-danger' : 'badge badge-warning';
    document.getElementById('primaryTime').textContent = `${action.estimated_minutes} minutes`;
    document.getElementById('primaryImpact').textContent = action.impact || "+10 readiness points";
    document.getElementById('primarySource').textContent = action.source || "AI Career Agent";

    const btnStart = document.getElementById('btnStartPrimary');
    if (btnStart) btnStart.href = action.route || "/interview";
}

function renderSnapshot(snap) {
    if (!snap) return;
    if (document.getElementById('snapOverall')) document.getElementById('snapOverall').textContent = `${snap.overall}%`;
    if (document.getElementById('snapSkills')) document.getElementById('snapSkills').textContent = `${snap.skills}%`;
    if (document.getElementById('snapResume')) document.getElementById('snapResume').textContent = `${snap.resume}%`;
    if (document.getElementById('snapJobMatch')) document.getElementById('snapJobMatch').textContent = `${snap.job_match}%`;
    if (document.getElementById('snapInterview')) document.getElementById('snapInterview').textContent = `${snap.interview}%`;
    if (document.getElementById('snapApps')) document.getElementById('snapApps').textContent = `${snap.applications}%`;
}

function renderTop3Actions(actions) {
    const container = document.getElementById('topActionsGrid');
    if (!container || !actions) return;

    container.innerHTML = actions.slice(0, 3).map((act, idx) => `
        <div class="top-action-card">
            <div class="top-action-rank">
                <span>#${idx + 1} ${act.priority} PRIORITY</span>
                <span class="badge badge-info">${act.estimated_minutes}m</span>
            </div>
            <h4 class="top-action-title">${act.action}</h4>
            <p class="top-action-why">${act.reason}</p>
            <div style="font-size: 0.775rem; color: var(--secondary); margin-bottom: 0.75rem;">
                <i class="fa-solid fa-bolt"></i> Impact: ${act.impact}
            </div>
            <a href="${act.route}" class="btn btn-outline btn-sm" style="width: 100%; text-align: center;">
                <i class="fa-solid fa-play"></i> START
            </a>
        </div>
    `).join('');
}

function renderMomentum(momentum) {
    if (!momentum) return;
    document.getElementById('momentumScore').textContent = momentum.score;
    document.getElementById('momentumLabel').textContent = `${momentum.label} MOMENTUM`;

    const badge = document.getElementById('momentumBadge');
    if (badge) {
        badge.textContent = momentum.label;
        badge.className = momentum.label === 'EXCELLENT' ? 'badge badge-purple' : (momentum.label === 'STRONG' ? 'badge badge-success' : 'badge badge-warning');
    }
}

function renderRisks(risks) {
    const container = document.getElementById('riskList');
    if (!container || !risks) return;

    if (risks.length === 0) {
        container.innerHTML = `<div style="font-size: 0.85rem; color: var(--text-muted); text-align: center; padding: 1rem;">🟢 No critical risks detected. Your career momentum is active!</div>`;
        return;
    }

    container.innerHTML = risks.map(r => `
        <div class="risk-item ${r.type}">
            <div>
                <strong style="color: #fff; font-size: 0.85rem;">${r.title}</strong>
                <div style="font-size: 0.775rem; color: var(--text-muted); margin-top: 0.15rem;">${r.message}</div>
            </div>
            <a href="${r.route}" class="btn btn-outline btn-sm" style="white-space: nowrap;">${r.action}</a>
        </div>
    `).join('');
}

function selectAvailableTime(minutes) {
    selectedTimeMinutes = minutes;
    document.querySelectorAll('.time-btn').forEach(btn => {
        btn.classList.toggle('active', btn.textContent.includes(minutes === 180 ? '3+' : (minutes === 60 ? '1 hour' : (minutes === 120 ? '2 hours' : '30 min'))));
    });
    loadDailyMission(minutes);
}

function loadDailyMission(minutes) {
    const payload = { ...currentAgentContext, time_available: minutes };

    fetch('/api/career-agent/daily-mission', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    })
    .then(res => res.json())
    .then(data => {
        if (data.success && data.data) {
            const m = data.data;
            document.getElementById('missionTotalTime').textContent = m.total_estimated_time;

            const list = document.getElementById('missionTaskList');
            if (list) {
                list.innerHTML = m.tasks.map(t => `
                    <div class="mission-task-item">
                        <div class="mission-task-info">
                            <i class="fa-solid ${t.icon} text-secondary"></i>
                            <span style="color: #fff; font-weight: 600; font-size: 0.9rem;">${t.title}</span>
                        </div>
                        <div style="display: flex; gap: 0.75rem; align-items: center;">
                            <span class="badge badge-info">${t.minutes} min</span>
                            <a href="${t.route}" class="btn btn-outline btn-sm"><i class="fa-solid fa-arrow-right"></i></a>
                        </div>
                    </div>
                `).join('');
            }
        }
    });
}

function loadWeeklyReview() {
    fetch('/api/career-agent/weekly-review', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(currentAgentContext)
    })
    .then(res => res.json())
    .then(data => {
        if (data.success && data.data) {
            const w = data.data;
            const grid = document.getElementById('weeklyMetricsGrid');
            if (grid) {
                grid.innerHTML = w.metrics.map(m => `
                    <div class="weekly-metric-card">
                        <div style="font-size: 0.8rem; color: var(--text-muted);"><i class="fa-solid ${m.icon}"></i> ${m.label}</div>
                        <div style="font-size: 1.5rem; font-weight: 800; color: #fff; margin: 0.3rem 0;">${m.value}</div>
                        <div class="weekly-change text-${m.color}">${m.change}</div>
                    </div>
                `).join('');
            }
            if (document.getElementById('weeklyHighlight')) {
                document.getElementById('weeklyHighlight').textContent = w.highlight;
            }
        }
    });
}

function markPrimaryComplete() {
    const actName = document.getElementById('primaryActionTitle').textContent;
    fetch('/api/career-agent/complete-action', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: actName, duration: 45 })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            let streak = parseInt(localStorage.getItem('careerforge_streak') || '7');
            streak++;
            localStorage.setItem('careerforge_streak', streak.toString());
            loadStreakAndNotifications();
            alert(`🎉 Action Completed!\n\n${actName}\n\nCareer Streak updated to 🔥 ${streak} Days!`);
        }
    });
}

function completeFullMission() {
    let streak = parseInt(localStorage.getItem('careerforge_streak') || '7');
    streak++;
    localStorage.setItem('careerforge_streak', streak.toString());
    loadStreakAndNotifications();
    alert(`🎯 Incredible work! All daily career mission tasks completed.\n\nCareer Streak updated to 🔥 ${streak} Days!`);
}

function renderCareerGoal() {
    let goal = JSON.parse(localStorage.getItem('careerforge_goal') || 'null');
    if (!goal) {
        goal = {
            target_role: "AI Engineer",
            target_date: "30 June 2027",
            milestones: [
                { title: "Master Python Core & Async", completed: true },
                { title: "Complete ML & Data Fundamentals", completed: true },
                { title: "Build AI Production API", completed: true },
                { title: "Create ATS Optimized Resume", completed: true },
                { title: "Complete 10 AI Mock Interviews", completed: false },
                { title: "Apply to 50 Matching Positions", completed: false },
                { title: "Qualify for Live Recruiter Screens", completed: false },
                { title: "Receive First Offer Letter", completed: false }
            ]
        };
        localStorage.setItem('careerforge_goal', JSON.stringify(goal));
    }

    if (document.getElementById('dispGoalRole')) document.getElementById('dispGoalRole').textContent = goal.target_role;
    if (document.getElementById('dispGoalDate')) document.getElementById('dispGoalDate').textContent = `Target Date: ${goal.target_date}`;

    const doneCnt = goal.milestones.filter(m => m.completed).length;
    const pct = Math.round((doneCnt / max(1, goal.milestones.length)) * 100);

    if (document.getElementById('dispGoalPct')) document.getElementById('dispGoalPct').textContent = `${pct}%`;
    if (document.getElementById('dispGoalFill')) document.getElementById('dispGoalFill').style.width = `${pct}%`;

    const checklist = document.getElementById('milestoneChecklist');
    if (checklist) {
        checklist.innerHTML = goal.milestones.map((m, idx) => `
            <div class="milestone-item ${m.completed ? 'checked' : ''}" onclick="toggleMilestone(${idx})">
                <i class="fa-regular ${m.completed ? 'fa-square-check text-success' : 'fa-square text-muted'}"></i>
                <span>${m.title}</span>
            </div>
        `).join('');
    }
}

function max(a, b) { return a > b ? a : b; }

function toggleMilestone(index) {
    let goal = JSON.parse(localStorage.getItem('careerforge_goal') || '{}');
    if (goal.milestones && goal.milestones[index]) {
        goal.milestones[index].completed = !goal.milestones[index].completed;
        localStorage.setItem('careerforge_goal', JSON.stringify(goal));
        renderCareerGoal();
    }
}

function toggleEditGoalForm() {
    const f = document.getElementById('goalEditForm');
    if (f) f.style.display = f.style.display === 'none' ? 'block' : 'none';
}

function saveCareerGoal() {
    const role = document.getElementById('goalTargetRole').value || "AI Engineer";
    const date = document.getElementById('goalTargetDate').value || "30 June 2027";

    let goal = JSON.parse(localStorage.getItem('careerforge_goal') || '{}');
    goal.target_role = role;
    goal.target_date = date;

    localStorage.setItem('careerforge_goal', JSON.stringify(goal));
    toggleEditGoalForm();
    renderCareerGoal();
}

function openNotificationDrawer() {
    const p = document.getElementById('notifPanel');
    if (p) p.style.display = p.style.display === 'none' ? 'block' : 'none';
}

function setupAgentChatListener() {
    const form = document.getElementById('agentInputForm');
    if (form) {
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            const input = document.getElementById('agentQueryInput');
            const txt = input.value.trim();
            if (txt) {
                sendAgentPrompt(txt);
                input.value = '';
            }
        });
    }
}

function sendAgentPrompt(promptText) {
    const windowEl = document.getElementById('agentChatWindow');
    if (!windowEl) return;

    // Append user bubble
    const userDiv = document.createElement('div');
    userDiv.className = 'chat-bubble user';
    userDiv.textContent = promptText;
    windowEl.appendChild(userDiv);
    windowEl.scrollTop = windowEl.scrollHeight;

    // Loading indicator
    const loadDiv = document.createElement('div');
    loadDiv.className = 'chat-bubble ai';
    loadDiv.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Analyzing unified context...';
    windowEl.appendChild(loadDiv);
    windowEl.scrollTop = windowEl.scrollHeight;

    fetch('/api/career-agent/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: promptText, context: currentAgentContext })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success && data.data) {
        loadDiv.textContent = data.data.reply;
            windowEl.scrollTop = windowEl.scrollHeight;
        }
    })
    .catch(() => {
        loadDiv.textContent = "I've analyzed your state. Spend 30 minutes practicing your top missing skill area to maximize interview readiness.";
    });
}

function generateCareerReport() {
    const modal = document.getElementById('reportModal');
    if (modal) modal.style.display = 'block';

    const container = document.getElementById('reportMarkdownContainer');
    if (container) {
        container.innerHTML = `<div style="text-align: center; padding: 2rem;"><i class="fa-solid fa-spinner fa-spin fa-2x text-secondary"></i><br><br>Generating executive report...</div>`;
    }

    fetch('/api/career-agent/career-report', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(currentAgentContext)
    })
    .then(res => res.json())
    .then(data => {
        if (data.success && data.data && container) {
            const rawMd = data.data.report;
            // Simple markdown parser for report display
            let html = rawMd
                .replace(/^# (.*$)/gim, '<h1 style="color:#fff; font-size:1.6rem; border-bottom:1px solid rgba(255,255,255,0.1); padding-bottom:0.4rem;">$1</h1>')
                .replace(/^### (.*$)/gim, '<h3 style="color:var(--secondary); font-size:1.1rem; margin-top:1rem;">$1</h3>')
                .replace(/^> (.*$)/gim, '<blockquote style="border-left:3px solid var(--secondary); background:rgba(15,23,42,0.6); padding:0.5rem 1rem; margin:0.5rem 0; color:#fff;">$1</blockquote>')
                .replace(/\*\*(.*?)\*\*/g, '<strong style="color:#fff;">$1</strong>')
                .replace(/`([^`]+)`/g, '<code style="background:rgba(255,255,255,0.1); padding:0.1rem 0.4rem; border-radius:4px; font-family:JetBrains Mono;">$1</code>')
                .replace(/\n/g, '<br>');

            container.innerHTML = html;
        }
    });
}

function closeCareerReport() {
    const modal = document.getElementById('reportModal');
    if (modal) modal.style.display = 'none';
}
