// AI Career OS JS

document.addEventListener("DOMContentLoaded", function() {
    if (document.getElementById("ovReadiness")) {
        initCareerOS();
    }
});

async function initCareerOS() {
    try {
        const res = await fetch("/api/career-os/overview");
        const data = await res.json();

        if (data.success && data.data) {
            const ov = data.data.overview;
            const act = data.data.next_action;
            const cmd = data.data.command_center;

            document.getElementById("ovReadiness").innerText = formatScore(ov.overall_readiness);
            document.getElementById("ovPlacement").innerText = formatScore(ov.placement_readiness);
            document.getElementById("ovJobMatch").innerText = formatScore(ov.job_match_score);
            document.getElementById("ovATS").innerText = formatScore(ov.ats_score);
            document.getElementById("ovInterview").innerText = formatScore(ov.interview_score);
            document.getElementById("ovSkill").innerText = `${ov.skill_progress}%`;
            document.getElementById("ovApp").innerText = `${ov.application_progress} recorded`;
            document.getElementById("ovMomentum").innerText = ov.career_momentum;
            document.getElementById("osHealthBadge").innerText = ov.health_status;

            document.getElementById("osActionTitle").innerText = act.title;
            document.getElementById("osActionWhy").innerText = act.why;
            document.getElementById("btnOSStartAction").href = act.action_url;

            // Render Command center
            const cmdBox = document.getElementById("commandList");
            if (cmdBox && cmd) {
                cmdBox.innerHTML = cmd.map(t => `
                    <div style="display: flex; justify-content: space-between; align-items: center; background: rgba(15,23,42,0.6); padding: 0.6rem 0.8rem; border-radius: 6px; margin-bottom: 0.5rem;">
                        <div>
                            <span class="badge badge-purple" style="font-size: 0.7rem;">${t.category}</span>
                            <span style="color: #fff; font-size: 0.85rem; margin-left: 0.4rem;">${t.task}</span>
                        </div>
                        <input type="checkbox" ${t.done ? 'checked' : ''} onchange="toggleOSTask('${t.id}', this.checked)">
                    </div>
                `).join('');
            }
        }
    } catch (e) {
        console.error("Init career OS error:", e);
    }
}

function formatScore(value) {
    return Number.isFinite(value) ? `${value}%` : "Not available";
}

async function toggleOSTask(taskId, completed) {
    try {
        const response = await fetch("/api/career-os/action", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ task_id: taskId, completed })
        });
        const data = await response.json();
        if (!response.ok || data.success !== true) throw new Error(data.error || "Task status could not be saved.");
    } catch (e) {
        console.error("Toggle OS task error:", e);
        alert(e.message);
    }
}

async function sendOSChatMessage() {
    const input = document.getElementById("chatInput");
    const text = input?.value;
    if (!text || text.trim() === "") return;

    const history = document.getElementById("osChatHistory");
    appendOSChatMessage(history, "user", text);
    input.value = "";
    history.scrollTop = history.scrollHeight;

    try {
        const res = await fetch("/api/career-os/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: text })
        });
        const data = await res.json();

        if (data.success && data.data) {
            appendOSChatMessage(history, "ai", data.data.reply);
            history.scrollTop = history.scrollHeight;
        }
    } catch (e) {
        console.error("Chat error:", e);
    }
}

function appendOSChatMessage(history, role, message) {
    const bubble = document.createElement("div");
    bubble.className = `chat-msg ${role}`;
    bubble.textContent = message;
    history.appendChild(bubble);
}

async function executeGlobalSearch() {
    const q = document.getElementById("globalSearchInput")?.value;
    if (!q || q.length < 2) return;

    try {
        const res = await fetch(`/api/career-os/search?q=${encodeURIComponent(q)}`);
        const data = await res.json();
        if (data.success) {
            console.log("Search results:", data.data);
        }
    } catch (e) {
        console.error("Search error:", e);
    }
}
