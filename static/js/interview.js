document.addEventListener('DOMContentLoaded', function () {
    initInterviewIntelligence();
});

let currentJobInfo = null;
let currentProfile = {};
let activeQuestions = [];
let currentQIndex = 0;
let sessionEvaluations = [];
let sessionTimer = null;
let timerSeconds = 0;
let isRetrySession = false;
let previousScore = 0;

function initInterviewIntelligence() {
    // 1. Check query parameters
    const urlParams = new URLSearchParams(window.location.search);
    const jobId = urlParams.get('job_id');
    const appId = urlParams.get('application_id');

    // 2. Load candidate profile context
    const plan = JSON.parse(localStorage.getItem('careerforge_plan_data') || '{}');
    const profile = JSON.parse(localStorage.getItem('careerforge_profile') || '{}');
    const resume = JSON.parse(localStorage.getItem('careerforge_resume_data') || '{}');

    currentProfile = {
        target_role: plan.target_role || profile.target_role || "Python Backend Developer",
        skills: plan.strong_skills || profile.current_skills || ["Python", "Flask", "FastAPI", "SQL", "PostgreSQL", "REST APIs", "Docker"],
        projects: resume.projects || plan.projects || [{ name: "ExamCraft AI Suite" }],
        ats_score: profile.ats_score || 84
    };

    if (appId) {
        const apps = JSON.parse(localStorage.getItem('careerforge_applications') || '[]');
        const matchedApp = apps.find(a => String(a.id) === String(appId));
        if (matchedApp) {
            currentJobInfo = {
                id: matchedApp.id,
                title: matchedApp.role,
                company: matchedApp.company,
                match_score: matchedApp.matchScore || 85
            };
            renderJobTargetBanner(currentJobInfo);
        } else if (jobId) {
            fetchJobBanner(jobId);
        } else {
            renderDefaultBanner();
        }
    } else if (jobId) {
        fetchJobBanner(jobId);
    } else {
        renderDefaultBanner();
    }

    // 3. Setup listeners
    setupInterviewListeners();
    renderHistoryAndGrowth();
}

function fetchJobBanner(jobId) {
    fetch(`/api/jobs/${jobId}`)
        .then(res => res.json())
        .then(data => {
            if (data.success && data.data) {
                currentJobInfo = data.data;
                renderJobTargetBanner(currentJobInfo);
            } else {
                renderDefaultBanner();
            }
        })
        .catch(() => renderDefaultBanner());
}

function renderJobTargetBanner(job) {
    const banner = document.getElementById('jobTargetBanner');
    if (!banner) return;

    document.getElementById('targetJobTitle').textContent = job.title;
    document.getElementById('targetJobCompany').textContent = job.company;
    document.getElementById('targetJobMatch').textContent = `${job.match_score || 83}%`;
    document.getElementById('targetResumeAts').textContent = `${currentProfile.ats_score}%`;

    const optJob = document.getElementById('optSelectJob');
    if (optJob) {
        optJob.textContent = `Target Job: ${job.title} (${job.company})`;
        optJob.selected = true;
    }

    banner.style.display = 'flex';
}

function renderDefaultBanner() {
    const banner = document.getElementById('jobTargetBanner');
    if (banner) banner.style.display = 'none';
}

function setupInterviewListeners() {
    const btnStart = document.getElementById('btnStartInterview');
    const btnSubmit = document.getElementById('btnSubmitAnswer');
    const btnSkip = document.getElementById('btnSkipQuestion');
    const btnNext = document.getElementById('btnNextQuestion');
    const btnPracticeWeak = document.getElementById('btnPracticeWeak');
    const btnNewSession = document.getElementById('btnNewSession');

    if (btnStart) btnStart.addEventListener('click', startInterviewSession);
    if (btnSubmit) btnSubmit.addEventListener('click', submitCurrentAnswer);
    if (btnSkip) btnSkip.addEventListener('click', skipCurrentQuestion);
    if (btnNext) btnNext.addEventListener('click', advanceToNextQuestion);
    if (btnPracticeWeak) btnPracticeWeak.addEventListener('click', startRetrySession);
    if (btnNewSession) btnNewSession.addEventListener('click', resetToSetup);
}

function startInterviewSession() {
    const targetRole = currentProfile.target_role;
    const interviewType = document.getElementById('selectType').value;
    const difficulty = document.getElementById('selectDifficulty').value;
    const count = parseInt(document.getElementById('selectCount').value);

    const payload = {
        target_role: targetRole,
        interview_type: interviewType,
        difficulty: difficulty,
        count: count,
        job_id: currentJobInfo ? currentJobInfo.id : null,
        skills: currentProfile.skills,
        projects: currentProfile.projects
    };

    fetch('/api/interview/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    })
    .then(res => res.json())
    .then(data => {
        if (data.success && data.data && data.data.questions) {
            activeQuestions = data.data.questions;
            currentQIndex = 0;
            sessionEvaluations = [];
            isRetrySession = false;

            document.getElementById('setupCard').style.display = 'none';
            document.getElementById('finalReportCard').style.display = 'none';
            document.getElementById('liveInterviewCard').style.display = 'block';

            renderCurrentQuestion();
        }
    });
}

function renderCurrentQuestion() {
    if (currentQIndex >= activeQuestions.length) {
        finishInterviewSession();
        return;
    }

    const q = activeQuestions[currentQIndex];
    const total = activeQuestions.length;

    document.getElementById('qCounter').textContent = `QUESTION ${currentQIndex + 1} / ${total}`;
    document.getElementById('qCategory').textContent = q.category || 'Technical';
    document.getElementById('qDifficulty').textContent = q.difficulty || 'Intermediate';
    document.getElementById('qSkill').textContent = q.job_skill || 'Backend';

    const pct = Math.round(((currentQIndex + 1) / total) * 100);
    document.getElementById('qProgressFill').style.width = `${pct}%`;

    document.getElementById('questionText').textContent = q.question;
    document.getElementById('answerInput').value = '';
    document.getElementById('evalDrawer').style.display = 'none';

    // Start Question Timer
    startTimer();
}

function startTimer() {
    clearInterval(sessionTimer);
    timerSeconds = 0;
    updateTimerDisplay();

    sessionTimer = setInterval(() => {
        timerSeconds++;
        updateTimerDisplay();
    }, 1000);
}

function updateTimerDisplay() {
    const mins = String(Math.floor(timerSeconds / 60)).padStart(2, '0');
    const secs = String(timerSeconds % 60).padStart(2, '0');
    const disp = document.getElementById('timerDisplay');
    if (disp) disp.textContent = `${mins}:${secs}`;
}

function stopTimer() {
    clearInterval(sessionTimer);
}

function submitCurrentAnswer() {
    const answer = document.getElementById('answerInput').value.trim();
    if (!answer) {
        alert("Please enter your answer response before submitting.");
        return;
    }

    stopTimer();
    const q = activeQuestions[currentQIndex];

    const payload = {
        target_role: currentProfile.target_role,
        question: q.question,
        user_answer: answer,
        difficulty: q.difficulty,
        category: q.category,
        job_skill: q.job_skill
    };

    fetch('/api/interview/evaluate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    })
    .then(res => res.json())
    .then(data => {
        if (data.success && data.data) {
            const ev = data.data;
            sessionEvaluations.push(ev);
            renderEvaluationDrawer(ev);
        }
    });
}

function skipCurrentQuestion() {
    stopTimer();
    const q = activeQuestions[currentQIndex];
    sessionEvaluations.push({
        score: 20,
        technical_accuracy: 15,
        communication: 25,
        relevance: 20,
        completeness: 20,
        confidence: 20,
        category: q.category || 'Technical',
        strengths: ['Skipped question'],
        weaknesses: ['⚠ Question was skipped.'],
        better_answer: 'Model Answer: Review core syntax and execution steps for this question.'
    });

    currentQIndex++;
    renderCurrentQuestion();
}

function renderEvaluationDrawer(ev) {
    document.getElementById('evalScoreNum').textContent = ev.score;
    document.getElementById('evalCategoryLabel').textContent = `Category: ${ev.category || 'Technical'}`;
    
    document.getElementById('evalTech').textContent = `${ev.technical_accuracy}%`;
    document.getElementById('evalComm').textContent = `${ev.communication}%`;
    document.getElementById('evalRel').textContent = `${ev.relevance}%`;
    document.getElementById('evalComp').textContent = `${ev.completeness}%`;

    const strUl = document.getElementById('evalStrengths');
    strUl.innerHTML = (ev.strengths || []).map(s => `<li>${s}</li>`).join('');

    const weakUl = document.getElementById('evalWeaknesses');
    weakUl.innerHTML = (ev.weaknesses || []).map(w => `<li>${w}</li>`).join('');

    document.getElementById('evalBetterAnswer').textContent = ev.better_answer;

    document.getElementById('evalDrawer').style.display = 'block';
}

function advanceToNextQuestion() {
    currentQIndex++;
    renderCurrentQuestion();
}

function finishInterviewSession() {
    stopTimer();
    document.getElementById('liveInterviewCard').style.display = 'none';

    const payload = {
        evaluations: sessionEvaluations,
        target_role: currentProfile.target_role,
        job_info: currentJobInfo || {}
    };

    fetch('/api/interview/final-report', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    })
    .then(res => res.json())
    .then(data => {
        if (data.success && data.data) {
            const report = data.data;
            renderFinalReport(report);
            fetchImprovementPlan(report.top_weakness, report.second_weakness);
            saveSessionToHistory(report);
        }
    });
}

function renderFinalReport(report) {
    document.getElementById('reportScore').textContent = report.overall_score;
    document.getElementById('reportReadinessLevel').textContent = report.readiness_level;
    document.getElementById('reportLevelDesc').textContent = report.level_description;

    document.getElementById('repTech').textContent = `${report.technical_score}%`;
    document.getElementById('fillTech').style.width = `${report.technical_score}%`;

    document.getElementById('repComm').textContent = `${report.communication_score}%`;
    document.getElementById('fillComm').style.width = `${report.communication_score}%`;

    document.getElementById('repRel').textContent = `${report.relevance_score}%`;
    document.getElementById('fillRel').style.width = `${report.relevance_score}%`;

    document.getElementById('repComp').textContent = `${report.completeness_score}%`;
    document.getElementById('fillComp').style.width = `${report.completeness_score}%`;

    document.getElementById('reportStrongest').textContent = (report.strongest_areas || []).join(', ');
    document.getElementById('reportWeakest').textContent = (report.weakest_areas || []).join(', ');
    document.getElementById('reportCoachText').textContent = report.coach_advice;

    if (isRetrySession) {
        const delta = report.overall_score - previousScore;
        const sign = delta >= 0 ? '+' : '';
        alert(`Retry Session Complete!\n\nPrevious Score: ${previousScore}%\nCurrent Score: ${report.overall_score}%\nImprovement: ${sign}${delta}%`);
    }

    previousScore = report.overall_score;
    document.getElementById('finalReportCard').style.display = 'block';
}

function fetchImprovementPlan(topW, secondW) {
    fetch('/api/interview/improvement-plan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            top_weakness: topW,
            second_weakness: secondW,
            target_role: currentProfile.target_role
        })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success && data.data) {
            const grid = document.getElementById('planDaysGrid');
            if (grid) {
                grid.innerHTML = '';
                data.data.forEach(item => {
                    const div = document.createElement('div');
                    div.className = 'plan-day-tile';
                    div.innerHTML = `
                        <span class="day-tag">${item.day}</span>
                        <span class="day-focus">${item.focus}</span>
                    `;
                    grid.appendChild(div);
                });
            }
        }
    });
}

function startRetrySession() {
    const topW = "Docker";
    const secondW = "System Design";

    fetch('/api/interview/retry', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            top_weakness: topW,
            second_weakness: secondW,
            count: 5
        })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success && data.data && data.data.questions) {
            activeQuestions = data.data.questions;
            currentQIndex = 0;
            sessionEvaluations = [];
            isRetrySession = true;

            document.getElementById('finalReportCard').style.display = 'none';
            document.getElementById('liveInterviewCard').style.display = 'block';

            renderCurrentQuestion();
        }
    });
}

function resetToSetup() {
    document.getElementById('finalReportCard').style.display = 'none';
    document.getElementById('liveInterviewCard').style.display = 'none';
    document.getElementById('setupCard').style.display = 'block';
}

function saveSessionToHistory(report) {
    let history = JSON.parse(localStorage.getItem('careerforge_interview_history') || '[]');
    const newEntry = {
        date: new Date().toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }),
        role: currentProfile.target_role,
        company: currentJobInfo ? currentJobInfo.company : "Target Practice",
        score: report.overall_score,
        technical: report.technical_score,
        communication: report.communication_score,
        weaknesses: report.top_weakness
    };

    history.unshift(newEntry);
    localStorage.setItem('careerforge_interview_history', JSON.stringify(history));

    // Also update state for V3 Career Intelligence
    localStorage.setItem('careerforge_interview_state', JSON.stringify({
        last_score: report.overall_score,
        last_weakness: report.top_weakness
    }));

    renderHistoryAndGrowth();
}

function renderHistoryAndGrowth() {
    let history = JSON.parse(localStorage.getItem('careerforge_interview_history') || '[]');

    if (history.length === 0) {
        history = [
            { date: "Sep 28, 2026", role: "Python Backend Developer", company: "Target Practice", score: 61, technical: 65, communication: 60, weaknesses: "SQL" },
            { date: "Sep 29, 2026", role: "Python Backend Developer", company: "Target Practice", score: 68, technical: 72, communication: 65, weaknesses: "System Design" },
            { date: "Sep 30, 2026", role: "Python Backend Developer", company: "TechForge Solutions", score: 78, technical: 82, communication: 74, weaknesses: "Docker" }
        ];
    }

    const scores = history.map(h => h.score);
    const best = Math.max(...scores);
    const avg = Math.round(scores.reduce((a, b) => a + b, 0) / scores.length);
    const growth = scores[0] - scores[scores.length - 1];
    const sign = growth >= 0 ? '+' : '';

    if (document.getElementById('histBest')) document.getElementById('histBest').textContent = `${best}%`;
    if (document.getElementById('histAvg')) document.getElementById('histAvg').textContent = `${avg}%`;
    if (document.getElementById('histCount')) document.getElementById('histCount').textContent = history.length;
    if (document.getElementById('histGrowth')) document.getElementById('histGrowth').textContent = `${sign}${growth}%`;

    const list = document.getElementById('historyList');
    if (list) {
        list.innerHTML = '';
        history.slice(0, 5).forEach((h, idx) => {
            const item = document.createElement('div');
            item.style.display = 'flex';
            item.style.justifyContent = 'space-between';
            item.style.alignItems = 'center';
            item.style.padding = '0.6rem 0.85rem';
            item.style.background = 'rgba(15, 23, 42, 0.5)';
            item.style.borderRadius = '6px';
            item.style.marginBottom = '0.4rem';
            item.style.fontSize = '0.875rem';

            item.innerHTML = `
                <div>
                    <strong style="color: #ffffff;">Session #${history.length - idx} • ${h.company}</strong>
                    <div style="font-size: 0.775rem; color: var(--text-muted);">${h.role} • ${h.date}</div>
                </div>
                <div style="text-align: right;">
                    <span style="font-weight: 800; color: var(--secondary); font-size: 1.1rem;">${h.score}%</span>
                    <div style="font-size: 0.75rem; color: #f59e0b;">Weakness: ${h.weaknesses}</div>
                </div>
            `;
            list.appendChild(item);
        });
    }
}
