// Placement Analytics JS

document.addEventListener("DOMContentLoaded", function() {
    if (document.getElementById("probReadiness")) {
        initPlacementAnalytics();
    }
});

async function initPlacementAnalytics() {
    try {
        const predRes = await fetch("/api/placement-analytics/prediction");
        const predData = await predRes.json();
        if (predData.success && predData.data) {
            document.getElementById("probReadiness").innerText = formatProbability(predData.data.placement_readiness_probability);
            document.getElementById("probInterview").innerText = formatProbability(predData.data.interview_probability);
            document.getElementById("probOffer").innerText = formatProbability(predData.data.offer_probability);
            document.getElementById("probDisclaimer").innerText = predData.data.disclaimer;
        }

        function formatProbability(value) {
            return Number.isFinite(value) ? `${value}%` : "Unavailable";
        }

        loadFunnel();
        loadRisks();
    } catch (e) {
        console.error("Init placement analytics error:", e);
    }
}

async function loadFunnel() {
    try {
        const res = await fetch("/api/placement-analytics/funnel");
        const data = await res.json();

        const grid = document.getElementById("funnelGrid");
        if (data.success && data.data && grid) {
            const f = data.data;
            grid.innerHTML = `
                <div class="funnel-step"><span>Applications Submitted</span><strong>${f.applications}</strong></div>
                <div class="funnel-step"><span>Online Assessments (${f.app_to_assessment_pct})</span><strong>${f.assessments}</strong></div>
                <div class="funnel-step"><span>Technical Interviews (${f.assessment_to_interview_pct})</span><strong>${f.interviews}</strong></div>
                <div class="funnel-step"><span>Final Job Offers (${f.interview_to_offer_pct})</span><strong style="color: #10b981;">${f.offers}</strong></div>
            `;
        }
    } catch (e) {
        console.error("Load funnel error:", e);
    }
}

async function loadRisks() {
    try {
        const res = await fetch("/api/placement-analytics/risks");
        const data = await res.json();

        const box = document.getElementById("riskList");
        if (data.success && data.data && box) {
            box.innerHTML = data.data.map(r => `
                <div class="glass-card" style="padding: 0.8rem; margin-bottom: 0.75rem;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.3rem;">
                        <strong style="color: #fff; font-size: 0.95rem;">${r.risk}</strong>
                        <span class="badge ${r.severity === 'HIGH' ? 'badge-danger' : 'badge-warning'}">${r.severity} RISK</span>
                    </div>
                    <p style="font-size: 0.85rem; color: var(--text-muted); margin: 0;">${r.description}</p>
                </div>
            `).join('');
        }
    } catch (e) {
        console.error("Load risks error:", e);
    }
}
