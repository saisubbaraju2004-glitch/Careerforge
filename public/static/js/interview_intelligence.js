// Advanced Interview Intelligence Frontend Logic

let currentSession = null;

document.addEventListener("DOMContentLoaded", function() {
    if (document.getElementById("intelOverallScore")) {
        initInterviewIntelligence();
    }
});

async function initInterviewIntelligence() {
    try {
        const res = await fetch("/api/interview-intelligence/readiness");
        const data = await res.json();

        if (data.success && data.data) {
            const m = data.data.metrics;
            document.getElementById("intelOverallScore").innerText = Number.isFinite(data.data.score) ? `${data.data.score} / 100` : "Not enough data";
            document.getElementById("intelReadinessBadge").innerText = data.data.status;

            document.getElementById("scoreTech").innerText = formatInterviewScore(m.technical);
            document.getElementById("scoreComm").innerText = formatInterviewScore(m.communication);
            document.getElementById("scoreConf").innerText = formatInterviewScore(m.confidence);
            document.getElementById("scorePS").innerText = formatInterviewScore(m.problem_solving);
            document.getElementById("scoreHR").innerText = formatInterviewScore(m.hr);
            document.getElementById("scoreProj").innerText = formatInterviewScore(m.project_explanation);
        }

        // Auto start mock session question
        startNewSessionModal();
        load7DayPlan();
    } catch (e) {
        console.error("Init interview intelligence error:", e);
    }
}

async function startNewSessionModal() {
    try {
        const res = await fetch("/api/interview-intelligence/start", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ role: "Python Backend Developer", company: "TechForge Solutions" })
        });
        const data = await res.json();

        if (data.success) {
            currentSession = data.data;
            const q = currentSession.current_question;
            document.getElementById("simQuestionText").innerText = q.question;
            document.getElementById("simMeta").innerText = `Target: ${currentSession.target_role} @ ${currentSession.company} (${q.category})`;
            document.getElementById("userAnswerInput").value = "";
            document.getElementById("analysisFeedbackBox").style.display = "none";
        }
    } catch (e) {
        console.error("Start session error:", e);
    }
}

async function submitAnswerForAnalysis() {
    const answer = document.getElementById("userAnswerInput")?.value;
    if (!answer || answer.trim().length < 10) {
        alert("Please provide a detailed response for evaluation.");
        return;
    }

    try {
        const res = await fetch("/api/interview-intelligence/analyze", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                question: currentSession?.current_question?.question || "",
                answer: answer,
                role: currentSession?.target_role || "Python Backend Developer",
                expected_keywords: currentSession?.current_question?.expected_keywords || [],
                session_id: currentSession?.session_id
            })
        });
        const data = await res.json();

        if (data.success) {
            const ana = data.data;
            document.getElementById("anaGood").innerText = ana.what_was_good;
            document.getElementById("anaMissing").innerText = ana.what_was_missing;
            document.getElementById("anaImproved").innerText = ana.improved_answer;
            document.getElementById("analysisFeedbackBox").style.display = "block";

        }
    } catch (e) {
        console.error("Submit answer error:", e);
    }
}

function formatInterviewScore(value) {
    return Number.isFinite(value) ? `${value}%` : "—";
}

async function load7DayPlan() {
    try {
        const res = await fetch("/api/interview-intelligence/final-report", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ answers: [] })
        });
        const data = await res.json();

        const grid = document.getElementById("sevenDayPlanGrid");
        if (!grid) return;

        if (data.success && data.data && data.data.seven_day_plan) {
            grid.innerHTML = data.data.seven_day_plan.map(d => `
                <div class="day-plan-card">
                    <span class="badge badge-purple" style="margin-bottom: 0.4rem;">DAY ${d.day}</span>
                    <strong style="display: block; color: #fff; font-size: 0.95rem; margin-bottom: 0.3rem;">${d.focus}</strong>
                    <p style="font-size: 0.85rem; color: var(--text-muted); margin: 0;">${d.action}</p>
                </div>
            `).join('');
        }
    } catch (e) {
        console.error("Load 7 day plan error:", e);
    }
}
