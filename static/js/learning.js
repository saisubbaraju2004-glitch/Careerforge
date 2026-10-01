// Personalized Learning Engine JS

document.addEventListener("DOMContentLoaded", function() {
    if (document.getElementById("dailyMissionBox")) {
        initLearningPage();
    }
});

async function initLearningPage() {
    try {
        const nextRes = await fetch("/api/learning/next");
        const nextData = await nextRes.json();
        if (nextData.success && nextData.data) {
            document.getElementById("nextTitle").innerText = nextData.data.title;
            document.getElementById("nextReason").innerText = nextData.data.reason;
            document.getElementById("nextEstTime").innerText = nextData.data.est_time;
            document.getElementById("btnNextAction").href = nextData.data.action_url;
        }

        setDailyTime("1 hour");
        load30DayPlan();
    } catch (e) {
        console.error("Init learning page error:", e);
    }
}

async function setDailyTime(timeVal) {
    try {
        const res = await fetch("/api/learning/daily", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ time: timeVal })
        });
        const data = await res.json();

        const box = document.getElementById("dailyMissionBox");
        if (data.success && data.data && box) {
            const m = data.data;
            box.innerHTML = `
                <h4 style="color: #fff; margin: 0 0 0.5rem 0;">${m.topic}</h4>
                <p style="color: var(--text-muted); font-size: 0.9rem; margin-bottom: 0.75rem;">${m.theory}</p>
                <div style="margin-bottom: 0.75rem;">
                    <strong style="color: var(--accent); font-size: 0.85rem;">Coding Task:</strong>
                    <div style="background: rgba(30,41,59,0.8); padding: 0.5rem 0.8rem; border-radius: 6px; font-family: monospace; font-size: 0.85rem; margin-top: 0.2rem; color: #f8fafc;">${m.coding_task}</div>
                </div>
                <a href="${m.resource_url}" target="_blank" class="btn btn-outline btn-sm">
                    <i class="fa-solid fa-book"></i> Open Learning Docs
                </a>
            `;
        }
    } catch (e) {
        console.error("Set daily time error:", e);
    }
}

async function load30DayPlan() {
    try {
        const res = await fetch("/api/learning/plan", { method: "POST" });
        const data = await res.json();

        const tbody = document.getElementById("planTableBody");
        if (data.success && data.data && tbody) {
            tbody.innerHTML = data.data.map(p => `
                <tr>
                    <td><span class="badge badge-purple">DAY ${p.day}</span></td>
                    <td><strong style="color: #fff;">${p.skill}</strong></td>
                    <td>
                        <strong style="color: #f8fafc; font-size: 0.9rem;">${p.topic}</strong><br>
                        <span style="font-size: 0.8rem; color: var(--text-muted);">${p.description}</span>
                    </td>
                    <td><span class="badge badge-info">${p.resource}</span></td>
                    <td>
                        <a href="${p.url}" target="_blank" class="btn btn-outline btn-sm">
                            <i class="fa-solid fa-arrow-up-right-from-square"></i> Learn
                        </a>
                    </td>
                </tr>
            `).join('');
        }
    } catch (e) {
        console.error("Load 30 day plan error:", e);
    }
}
