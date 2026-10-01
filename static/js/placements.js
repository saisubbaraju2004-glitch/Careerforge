document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('companyCardsGrid')) {
        initPlacements();
        setupPlacementCoachListener();
    }
});

let currentPlacementProfile = {};
let allCompanyDrives = [];

function getStoredPlacementProfile() {
    let p = JSON.parse(localStorage.getItem('careerforge_placement_profile') || 'null');
    if (!p) {
        p = {
            name: "Rahul Sharma",
            college: "National Institute of Technology",
            branch: "CSE",
            graduation_year: 2027,
            cgpa: 7.85,
            backlogs: 0,
            target_role: "Software Developer",
            preferred_location: "Bengaluru / Remote"
        };
        localStorage.setItem('careerforge_placement_profile', JSON.stringify(p));
    }
    return p;
}

function initPlacements() {
    currentPlacementProfile = getStoredPlacementProfile();
    renderProfileHeader();

    fetch('/api/placements/companies')
        .then(res => res.json())
        .then(data => {
            if (data.success && data.data) {
                allCompanyDrives = data.data;
                renderCompanyCards(allCompanyDrives);
                updateDashboardCounters(allCompanyDrives);
            }
        });

    fetch('/api/placements/readiness', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ profile: currentPlacementProfile })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success && data.data) {
            renderRadarBreakdown(data.data);
        }
    });

    loadPlacementDailyMission();
}

function renderProfileHeader() {
    const p = currentPlacementProfile;
    if (document.getElementById('dispPlacementReadiness')) document.getElementById('dispPlacementReadiness').textContent = `78%`;
    if (document.getElementById('dispCandidateMeta')) {
        document.getElementById('dispCandidateMeta').textContent = `${p.name} • ${p.branch} (Batch ${p.graduation_year}) • ${p.college} • CGPA ${p.cgpa}`;
    }
    if (document.getElementById('dispTargetRole')) document.getElementById('dispTargetRole').textContent = p.target_role;
    if (document.getElementById('dispGradYear')) document.getElementById('dispGradYear').textContent = p.graduation_year;
    if (document.getElementById('dispBacklogs')) document.getElementById('dispBacklogs').textContent = `${p.backlogs} Active`;
}

function updateDashboardCounters(comps) {
    const eligibleCnt = comps.filter(c => c.eligibility_result.is_eligible).length;
    const apps = JSON.parse(localStorage.getItem('careerforge_applications') || '[]');

    if (document.getElementById('cntEligible')) document.getElementById('cntEligible').textContent = eligibleCnt;
    if (document.getElementById('cntApplied')) document.getElementById('cntApplied').textContent = apps.length || 8;
    if (document.getElementById('cntAssessments')) document.getElementById('cntAssessments').textContent = 4;
    if (document.getElementById('cntInterviews')) document.getElementById('cntInterviews').textContent = 3;
    if (document.getElementById('cntOffers')) document.getElementById('cntOffers').textContent = 1;
    if (document.getElementById('cntScore')) document.getElementById('cntScore').textContent = "78%";
}

function renderRadarBreakdown(readiness) {
    const container = document.getElementById('radarList');
    if (!container || !readiness) return;

    const cats = readiness.categories;
    container.innerHTML = Object.keys(cats).map(k => `
        <div class="radar-item">
            <div style="display: flex; justify-content: space-between; font-size: 0.85rem; color: #fff; margin-bottom: 0.3rem;">
                <span>${k}</span>
                <strong style="color: var(--secondary);">${cats[k]}%</strong>
            </div>
            <div class="funnel-bar-bg">
                <div class="funnel-bar-fill" style="width: ${cats[k]}%; background: linear-gradient(90deg, var(--secondary), var(--cyan));"></div>
            </div>
        </div>
    `).join('');
}

function renderCompanyCards(comps) {
    const container = document.getElementById('companyCardsGrid');
    if (!container || !comps) return;

    const apps = JSON.parse(localStorage.getItem('careerforge_applications') || '[]');

    container.innerHTML = comps.map(c => {
        const isEligible = c.eligibility_result.is_eligible;
        const matchedApp = apps.find(a => a.company === c.name);
        const appStatus = matchedApp ? matchedApp.status : "Not Applied";

        return `
            <div class="c-card">
                <div>
                    <div class="c-card-header">
                        <div>
                            <h3 class="c-card-title">${c.name}</h3>
                            <div class="c-card-role">${c.role}</div>
                        </div>
                        <span class="badge ${isEligible ? 'badge-success' : 'badge-danger'}">
                            ${isEligible ? '✓ Eligible' : '✕ Not Eligible'}
                        </span>
                    </div>

                    <div style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 0.75rem;">
                        <div><i class="fa-solid fa-money-bill-wave text-success"></i> CTC: <strong style="color:#fff;">${c.ctc}</strong></div>
                        <div><i class="fa-solid fa-location-dot text-cyan"></i> ${c.location}</div>
                    </div>

                    <div style="background: rgba(15,23,42,0.6); padding: 0.6rem 0.85rem; border-radius: 6px; margin-bottom: 1rem;">
                        <div style="display: flex; justify-content: space-between; font-size: 0.8rem; color: var(--text-muted);">
                            <span>Placement Readiness</span>
                            <strong style="color: var(--secondary);">${c.company_readiness}%</strong>
                        </div>
                        <div style="display: flex; justify-content: space-between; font-size: 0.8rem; color: var(--text-muted); margin-top: 0.2rem;">
                            <span>Resume Match</span>
                            <strong style="color: var(--cyan);">${c.resume_match}%</strong>
                        </div>
                    </div>
                </div>

                <div>
                    <div style="font-size: 0.775rem; color: var(--text-muted); margin-bottom: 0.6rem;">
                        Status: <span class="badge badge-info">${appStatus}</span>
                    </div>

                    <div style="display: flex; gap: 0.4rem;">
                        <a href="/placements/company/${c.id}" class="btn btn-outline btn-sm" style="flex:1; text-align:center;">Details</a>
                        <a href="/placements/company/${c.id}" class="btn btn-secondary btn-sm" style="flex:1; text-align:center;">Prepare</a>
                        <button class="btn btn-primary btn-sm" style="flex:1;" onclick="applyToDrive('${c.id}', '${c.name}', '${c.role}')">Apply</button>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

function applyToDrive(companyId, companyName, roleName) {
    let apps = JSON.parse(localStorage.getItem('careerforge_applications') || '[]');
    
    // Check if already applied
    let existing = apps.find(a => a.company === companyName);
    if (existing) {
        alert(`You have already applied to ${companyName} (${roleName}). Application Status: ${existing.status}`);
        return;
    }

    const newApp = {
        id: Date.now(),
        company: companyName || "Zenvexa Technologies",
        role: roleName || "Software Engineer",
        status: "Applied",
        dateApplied: new Date().toISOString().split('T')[0],
        matchScore: 88,
        atsScore: 84,
        daysWaiting: 0,
        resume_version: "Standard Resume v2"
    };

    apps.unshift(newApp);
    localStorage.setItem('careerforge_applications', JSON.stringify(apps));

    alert(`🎉 Application Submitted Successfully!\n\nDrive: ${newApp.company}\nRole: ${newApp.role}\nStatus: Applied\n\nSynced with Application Intelligence Pipeline!`);
    initPlacements();
}

function filterCompanies(type) {
    if (type === 'eligible') {
        const elig = allCompanyDrives.filter(c => c.eligibility_result.is_eligible);
        renderCompanyCards(elig);
    } else {
        renderCompanyCards(allCompanyDrives);
    }
}

function loadPlacementDailyMission() {
    fetch('/api/placements/daily-mission', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ profile: currentPlacementProfile })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success && data.data) {
            const container = document.getElementById('placementMissionList');
            if (container) {
                container.innerHTML = data.data.tasks.map(t => `
                    <div class="mission-task-row">
                        <div style="display: flex; align-items: center; gap: 0.75rem;">
                            <i class="fa-solid fa-circle-check text-success"></i>
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

function loadCompanyDetailView(companyId) {
    fetch(`/api/placements/company/${companyId}`)
        .then(res => res.json())
        .then(data => {
            if (data.success && data.data) {
                const c = data.data;
                if (document.getElementById('cName')) document.getElementById('cName').textContent = c.name;
                if (document.getElementById('cRole')) document.getElementById('cRole').textContent = c.role;
                if (document.getElementById('cCtc')) document.getElementById('cCtc').textContent = c.ctc;
                if (document.getElementById('cLocation')) document.getElementById('cLocation').innerHTML = `<i class="fa-solid fa-location-dot"></i> ${c.location}`;
                
                if (document.getElementById('cReadinessScore')) document.getElementById('cReadinessScore').textContent = `${c.company_readiness}% Readiness`;
                if (document.getElementById('cResumeMatch')) document.getElementById('cResumeMatch').textContent = `${c.resume_match}% Resume Match`;

                const skillsContainer = document.getElementById('cSkillsList');
                if (skillsContainer) {
                    skillsContainer.innerHTML = c.skills.map(s => `
                        <span class="badge badge-accent"><i class="fa-solid fa-check"></i> ${s}</span>
                    `).join('');
                }
            }
        });
}

function generateCompanyPrepPlan() {
    const planCard = document.getElementById('prepPlanCard');
    if (planCard) planCard.style.display = 'block';

    const companyId = window.location.pathname.split('/').pop() || "zenvexa-tech";

    fetch('/api/placements/company-plan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ company_id: companyId, profile: currentPlacementProfile })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success && data.data) {
            const list = document.getElementById('prepScheduleList');
            if (list) {
                list.innerHTML = data.data.schedule.map(s => `
                    <div style="background: rgba(15,23,42,0.6); border: 1px solid rgba(255,255,255,0.08); border-radius: 8px; padding: 1rem;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 0.4rem;">
                            <strong style="color: var(--secondary); font-size: 0.85rem;">${s.day}</strong>
                            <span class="badge badge-info">${s.minutes} min</span>
                        </div>
                        <h4 style="color: #fff; margin: 0 0 0.3rem 0; font-size: 1rem;">${s.focus}</h4>
                        <p style="font-size: 0.825rem; color: var(--text-muted); margin: 0;">${s.details}</p>
                    </div>
                `).join('');
            }
        }
    });
}

function openProfileModal() {
    const m = document.getElementById('profileModal');
    if (m) m.style.display = 'block';
}

function closeProfileModal() {
    const m = document.getElementById('profileModal');
    if (m) m.style.display = 'none';
}

function savePlacementProfile(e) {
    e.preventDefault();
    const updated = {
        name: document.getElementById('profName').value || "Rahul Sharma",
        college: document.getElementById('profCollege').value || "National Institute of Technology",
        branch: document.getElementById('profBranch').value || "CSE",
        graduation_year: parseInt(document.getElementById('profYear').value || 2027),
        cgpa: parseFloat(document.getElementById('profCgpa').value || 7.85),
        backlogs: parseInt(document.getElementById('profBacklogs').value || 0),
        target_role: "Software Developer",
        preferred_location: "Bengaluru / Remote"
    };

    localStorage.setItem('careerforge_placement_profile', JSON.stringify(updated));
    closeProfileModal();
    initPlacements();
}

function setupPlacementCoachListener() {
    const form = document.getElementById('placementInputForm');
    if (form) {
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            const input = document.getElementById('placementQueryInput');
            const txt = input.value.trim();
            if (txt) {
                sendPlacementPrompt(txt);
                input.value = '';
            }
        });
    }
}

function sendPlacementPrompt(promptText) {
    const windowEl = document.getElementById('placementChatWindow');
    if (!windowEl) return;

    const userDiv = document.createElement('div');
    userDiv.className = 'chat-bubble user';
    userDiv.textContent = promptText;
    windowEl.appendChild(userDiv);
    windowEl.scrollTop = windowEl.scrollHeight;

    const loadDiv = document.createElement('div');
    loadDiv.className = 'chat-bubble ai';
    loadDiv.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Evaluating placement drive requirements...';
    windowEl.appendChild(loadDiv);
    windowEl.scrollTop = windowEl.scrollHeight;

    fetch('/api/placements/coach', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: promptText, profile: currentPlacementProfile })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success && data.data) {
        loadDiv.textContent = data.data.reply;
            windowEl.scrollTop = windowEl.scrollHeight;
        }
    })
    .catch(() => {
        loadDiv.textContent = "Prioritize preparing for your top eligible drive. Solve 5 DSA problems and run a mock technical interview.";
    });
}

function generatePlacementReport() {
    const modal = document.getElementById('placementReportModal');
    if (modal) modal.style.display = 'block';

    const container = document.getElementById('placementReportContainer');
    if (container) {
        container.innerHTML = `<div style="text-align: center; padding: 2rem;"><i class="fa-solid fa-spinner fa-spin fa-2x text-secondary"></i><br><br>Generating campus placement report...</div>`;
    }

    fetch('/api/placements/report', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ profile: currentPlacementProfile })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success && data.data && container) {
            const rawMd = data.data.report;
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

function closePlacementReport() {
    const modal = document.getElementById('placementReportModal');
    if (modal) modal.style.display = 'none';
}
