document.addEventListener('DOMContentLoaded', function () {
    initApplicationIntelligence();
});

let currentAppsList = [];
let analyticsData = {};

function initApplicationIntelligence() {
    loadApplicationsData();
    setupEventListeners();
}

function loadApplicationsData() {
    let saved = JSON.parse(localStorage.getItem('careerforge_applications') || '[]');

    if (saved.length === 0) {
        saved = [
            {
                id: "app_demo_01",
                job_id: "job_py_01",
                company: "TechForge Solutions",
                role: "Python Backend Developer",
                location: "Bengaluru (Hybrid)",
                status: "Interview",
                applied_date: "25 Sep 2026",
                days_waiting: 5,
                match_score: 87,
                ats_score: 84,
                interview_score: 78,
                resume_version: "Python Backend Resume v2",
                notes: "Technical round scheduled for Oct 5",
                job_url: "https://careers.techforgesolutions.com/jobs/py-backend"
            },
            {
                id: "app_demo_02",
                job_id: "job_py_02",
                company: "Nexus Systems",
                role: "Junior Backend Engineer",
                location: "Remote",
                status: "Applied",
                applied_date: "22 Sep 2026",
                days_waiting: 8,
                match_score: 81,
                ats_score: 80,
                interview_score: null,
                resume_version: "Python Backend Resume v1",
                notes: "Pending recruiter initial screen",
                job_url: "https://nexus-systems.io/careers/junior-backend"
            },
            {
                id: "app_demo_03",
                job_id: "job_py_03",
                company: "CloudScale AI",
                role: "FastAPI & Cloud Engineer",
                location: "Hyderabad",
                status: "Assessment",
                applied_date: "28 Sep 2026",
                days_waiting: 2,
                match_score: 76,
                ats_score: 78,
                interview_score: null,
                resume_version: "Python Backend Resume v2",
                notes: "Coding assignment due Oct 3",
                job_url: "https://cloudscale.ai/jobs/fastapi-backend"
            },
            {
                id: "app_demo_04",
                job_id: "job_py_04",
                company: "Innovate Labs",
                role: "Full Stack Python Developer",
                location: "Pune",
                status: "Offer",
                applied_date: "15 Sep 2026",
                days_waiting: 15,
                match_score: 89,
                ats_score: 85,
                interview_score: 88,
                resume_version: "Python Backend Resume v2",
                notes: "Received formal offer letter. ₹7.5 LPA",
                job_url: "https://innovate-labs.co/careers/fullstack-py"
            }
        ];
        localStorage.setItem('careerforge_applications', JSON.stringify(saved));
    }

    currentAppsList = saved;
    fetchAnalyticsData();
}

function fetchAnalyticsData() {
    fetch('/api/applications/analytics', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ applications: currentAppsList })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success && data.data) {
            analyticsData = data.data;
            renderMetricsBanner(analyticsData);
            renderAnalyticsSection(analyticsData);
            processAndRenderCards();
        }
    })
    .catch(() => {
        processAndRenderCards();
    });
}

function renderMetricsBanner(a) {
    if (document.getElementById('cntTotal')) document.getElementById('cntTotal').textContent = a.total_applications || 0;
    if (document.getElementById('cntInterview')) document.getElementById('cntInterview').textContent = a.interview || 0;
    if (document.getElementById('cntOffers')) document.getElementById('cntOffers').textContent = a.offers || 0;
    if (document.getElementById('rateResponse')) document.getElementById('rateResponse').textContent = `${a.response_rate || 0}%`;
    if (document.getElementById('rateInterview')) document.getElementById('rateInterview').textContent = `${a.interview_rate || 0}%`;
}

function processAndRenderCards() {
    const keyword = document.getElementById('appSearch')?.value.toLowerCase() || '';
    const statusFilter = document.getElementById('appStatusFilter')?.value || 'All';
    const sortVal = document.getElementById('appSort')?.value || 'priority';

    let filtered = currentAppsList.filter(app => {
        if (keyword && !app.company.toLowerCase().includes(keyword) && !app.role.toLowerCase().includes(keyword)) {
            return false;
        }
        if (statusFilter !== 'All' && app.status !== statusFilter) {
            return false;
        }
        return true;
    });

    // Calculate priority & health for each app
    const promises = filtered.map(app => {
        return fetch('/api/applications/priority', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(app)
        })
        .then(res => res.json())
        .then(data => {
            return {
                ...app,
                priority_info: data.data || { priority_score: 75, tier: "MEDIUM PRIORITY", health: "Healthy", health_badge: "green" }
            };
        })
        .catch(() => ({
            ...app,
            priority_info: { priority_score: 75, tier: "MEDIUM PRIORITY", health: "Healthy", health_badge: "green" }
        }));
    });

    Promise.all(promises).then(enriched => {
        // Sort enriched list
        if (sortVal === 'newest') {
            enriched.sort((a, b) => new Date(b.applied_date || 0) - new Date(a.applied_date || 0));
        } else if (sortVal === 'match') {
            enriched.sort((a, b) => (b.match_score || 0) - (a.match_score || 0));
        } else if (sortVal === 'followup') {
            enriched.sort((a, b) => (b.days_waiting || 0) - (a.days_waiting || 0));
        } else {
            enriched.sort((a, b) => b.priority_info.priority_score - a.priority_info.priority_score);
        }

        renderTopFocusCards(enriched.slice(0, 3));
        renderApplicationCards(enriched);
    });
}

function renderTopFocusCards(focusApps) {
    const grid = document.getElementById('topFocusGrid');
    if (!grid) return;
    grid.innerHTML = '';

    if (focusApps.length === 0) {
        grid.innerHTML = '<p class="text-muted">No high-priority applications to focus on.</p>';
        return;
    }

    focusApps.forEach((app, idx) => {
        const div = document.createElement('div');
        div.className = 'focus-card';
        div.innerHTML = `
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <span class="focus-prio-badge">Priority #${idx + 1} (${app.priority_info.priority_score} pts)</span>
                <span class="status-pill ${app.status}">${app.status}</span>
            </div>
            <strong style="color:#ffffff; font-size:1rem; margin-top:0.25rem;">${app.company}</strong>
            <span style="font-size:0.85rem; color:#a5b4fc;">${app.role}</span>
            <span style="font-size:0.775rem; color:var(--text-muted); margin-top:0.25rem;">Next Action: ${app.priority_info.next_action}</span>
        `;
        grid.appendChild(div);
    });
}

function renderApplicationCards(apps) {
    const container = document.getElementById('appCardsContainer');
    if (!container) return;

    container.innerHTML = '';
    if (apps.length === 0) {
        container.innerHTML = '<div class="glass-card" style="grid-column: 1 / -1; padding: 2rem; text-align: center;"><p class="text-muted">No applications found matching search criteria.</p></div>';
        return;
    }

    apps.forEach(app => {
        const card = document.createElement('div');
        card.className = 'app-card';

        const pInfo = app.priority_info;
        const intBtn = app.status === 'Interview'
            ? `<a href="/interview?application_id=${app.id}" class="btn btn-secondary"><i class="fa-solid fa-microphone"></i> PRACTICE INTERVIEW</a>`
            : '';

        card.innerHTML = `
            <div>
                <div class="app-card-header">
                    <div class="app-title-block">
                        <h3>${app.role}</h3>
                        <div class="app-company">${app.company} • ${app.location || 'Remote'}</div>
                    </div>
                    <span class="status-pill ${app.status}">${app.status}</span>
                </div>

                <div class="app-meta-row" style="margin: 0.75rem 0;">
                    <span class="job-meta-pill"><span class="health-dot ${pInfo.health_badge}"></span> ${pInfo.health}</span>
                    <span class="job-meta-pill"><i class="fa-solid fa-percent"></i> Match: ${app.match_score || 80}%</span>
                    <span class="job-meta-pill"><i class="fa-solid fa-file-contract"></i> ATS: ${app.ats_score || 84}%</span>
                    <span class="job-meta-pill"><i class="fa-solid fa-calendar"></i> ${app.applied_date || 'Recent'}</span>
                </div>

                <div style="font-size: 0.8rem; color: var(--text-muted); margin-bottom: 0.5rem;">
                    <strong>Next Action:</strong> ${pInfo.next_action}
                </div>
            </div>

            <div class="app-card-actions">
                <a href="/applications/${app.id}" class="btn btn-secondary"><i class="fa-solid fa-eye"></i> VIEW</a>
                <button type="button" class="btn btn-secondary" onclick="updateAppStatus('${app.id}')"><i class="fa-solid fa-pen-to-square"></i> STATUS</button>
                <button type="button" class="btn btn-secondary" onclick="triggerFollowup('${app.company}', '${app.role}', ${app.days_waiting || 7}, '${app.status}')"><i class="fa-solid fa-paper-plane"></i> FOLLOW UP</button>
                ${intBtn}
            </div>
        `;
        container.appendChild(card);
    });
}

function renderAnalyticsSection(analytics) {
    // Resume Performance
    const resList = document.getElementById('resumePerfList');
    if (resList) {
        resList.innerHTML = (analytics.resume_performance || []).map(r => `
            <div class="perf-row">
                <span>${r.version} (${r.applications} apps)</span>
                <strong style="color:var(--secondary);">${r.conversion} Interview Conv.</strong>
            </div>
        `).join('') || '<div class="text-muted">No resume performance data yet.</div>';
    }

    // Match Conversion
    const matchList = document.getElementById('matchPerfList');
    if (matchList && analytics.match_performance) {
        const m = analytics.match_performance;
        matchList.innerHTML = `
            <div class="perf-row"><span>80%+ Match Range</span><strong>${m.high.ints} interviews / ${m.high.apps} apps</strong></div>
            <div class="perf-row"><span>60–79% Match Range</span><strong>${m.medium.ints} interviews / ${m.medium.apps} apps</strong></div>
            <div class="perf-row"><span>Below 60% Range</span><strong>${m.low.ints} interviews / ${m.low.apps} apps</strong></div>
        `;
    }

    // Rejection Patterns
    const rejList = document.getElementById('rejectionPatternsList');
    if (rejList && analytics.rejection_patterns) {
        rejList.innerHTML = Object.entries(analytics.rejection_patterns).map(([reason, cnt]) => `
            <div class="perf-row"><span>${reason} Rejections</span><strong>${cnt}</strong></div>
        `).join('');
    }
}

function setupEventListeners() {
    const search = document.getElementById('appSearch');
    const filter = document.getElementById('appStatusFilter');
    const sort = document.getElementById('appSort');

    if (search) search.addEventListener('input', processAndRenderCards);
    if (filter) filter.addEventListener('change', processAndRenderCards);
    if (sort) sort.addEventListener('change', processAndRenderCards);

    // Add Application Button
    document.getElementById('btnAddApplication').addEventListener('click', () => {
        const comp = prompt("Enter Company Name:", "TechCorp");
        if (!comp) return;
        const role = prompt("Enter Role Title:", "Python Backend Developer");

        const newApp = {
            id: `app_${Date.now()}`,
            company: comp,
            role: role || "Software Engineer",
            location: "Bengaluru",
            status: "Applied",
            applied_date: new Date().toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }),
            days_waiting: 0,
            match_score: 82,
            ats_score: 84,
            resume_version: "Python Backend Resume v2",
            notes: "Manually added to tracker"
        };

        currentAppsList.unshift(newApp);
        localStorage.setItem('careerforge_applications', JSON.stringify(currentAppsList));
        fetchAnalyticsData();
        alert(`Added "${role}" at ${comp} to Application Command Center!`);
    });

    // Export CSV
    document.getElementById('btnExportCsv').addEventListener('click', () => {
        fetch('/api/applications/export', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ applications: currentAppsList })
        })
        .then(res => res.blob())
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = "careerforge_applications_report.csv";
            document.body.appendChild(a);
            a.click();
            a.remove();
        });
    });

    // Print Report
    document.getElementById('btnPrintReport').addEventListener('click', () => window.print());

    // AI Coach Prompts
    document.querySelectorAll('.prompt-chip').forEach(chip => {
        chip.addEventListener('click', () => {
            const promptText = chip.getAttribute('data-prompt');
            const box = document.getElementById('appCoachReply');
            box.textContent = "Analyzing application pipeline metrics...";

            fetch('/api/applications/coach', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    prompt: promptText,
                    analytics: analyticsData,
                    applications: currentAppsList
                })
            })
            .then(res => res.json())
            .then(data => {
                if (data.success && data.data && data.data.reply) {
                    box.textContent = data.data.reply;
                }
            });
        });
    });
}

function updateAppStatus(appId) {
    const app = currentAppsList.find(a => a.id === appId);
    if (!app) return;

    const newStatus = prompt("Enter new status (Wishlist, Applied, Assessment, Interview, Offer, Rejected):", app.status);
    if (newStatus && ["Wishlist", "Applied", "Assessment", "Interview", "Offer", "Rejected"].includes(newStatus)) {
        app.status = newStatus;
        if (newStatus === "Rejected") {
            const reason = prompt("Select rejection reason (Resume, Skills, Interview, Experience, Unknown):", "Interview");
            app.rejection_reason = reason || "Unknown";
        }
        localStorage.setItem('careerforge_applications', JSON.stringify(currentAppsList));
        fetchAnalyticsData();
    }
}

function triggerFollowup(company, role, days, status) {
    fetch('/api/applications/follow-up', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ company: company, role: role, days_since_application: days, status: status })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success && data.data && data.data.message) {
            alert(`RECOMMENDED FOLLOW-UP MESSAGE:\n\n${data.data.message}`);
        }
    });
}
