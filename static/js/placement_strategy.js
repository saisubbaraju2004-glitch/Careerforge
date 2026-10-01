document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('rankingsGrid')) {
        initPlacementStrategy();
    }
});

let currentStrategyProfile = {};

function initPlacementStrategy() {
    currentStrategyProfile = JSON.parse(localStorage.getItem('careerforge_placement_profile') || '{}');

    fetch('/api/placement-strategy/next-action', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ profile: currentStrategyProfile })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success && data.data) {
            renderStrategyHero(data.data);
        }
    });

    fetch('/api/placement-strategy/daily-command', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ profile: currentStrategyProfile })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success && data.data) {
            renderDailyCommand(data.data);
        }
    });

    fetch('/api/placement-strategy/rankings')
        .then(res => res.json())
        .then(data => {
            if (data.success && data.data) {
                renderCompanyRankings(data.data);
            }
        });
}

function renderStrategyHero(action) {
    if (!action) return;
    document.getElementById('stratActionTitle').textContent = action.action;
    document.getElementById('stratActionReason').textContent = action.reason;
    document.getElementById('stratActionPriority').textContent = `${action.priority} PRIORITY`;
    document.getElementById('stratActionTime').innerHTML = `<i class="fa-solid fa-clock"></i> ${action.estimated_minutes} minutes`;
    
    const btnStart = document.getElementById('btnStratStartAction');
    if (btnStart) btnStart.href = action.route || "/placement-practice/coding";
}

function renderDailyCommand(cmd) {
    if (!cmd) return;
    document.getElementById('stratCommandTarget').textContent = `Primary Target Drive: ${cmd.target_company}`;
    document.getElementById('commandProgress').textContent = `${cmd.completed_count} / ${cmd.total_count} completed`;
    document.getElementById('commandEstTime').textContent = cmd.formatted_time;

    const container = document.getElementById('commandTasksList');
    if (!container || !cmd.tasks) return;

    container.innerHTML = cmd.tasks.map(t => `
        <div class="command-task-row ${t.completed ? 'done' : ''}">
            <div style="display: flex; align-items: center; gap: 0.75rem;">
                <i class="fa-solid ${t.completed ? 'fa-circle-check text-success' : 'fa-circle text-muted'}"></i>
                <span style="color: #fff; font-weight: 600; font-size: 0.9rem;">${t.title}</span>
            </div>
            <div style="display: flex; gap: 0.75rem; align-items: center;">
                <span class="badge badge-info">${t.minutes} min</span>
                <a href="${t.route}" class="btn btn-outline btn-sm"><i class="fa-solid fa-arrow-right"></i></a>
            </div>
        </div>
    `).join('');
}

function renderCompanyRankings(rankings) {
    const container = document.getElementById('rankingsGrid');
    if (!container || !rankings) return;

    const apps = JSON.parse(localStorage.getItem('careerforge_applications') || '[]');

    container.innerHTML = rankings.map((c, idx) => {
        const matchedApp = apps.find(a => a.company === c.name);
        const appStatus = matchedApp ? matchedApp.status : "Not Applied";

        return `
            <div class="ranking-card">
                <div>
                    <div class="ranking-card-top">
                        <div>
                            <span class="badge ${c.badge_class}" style="margin-bottom: 0.3rem;">${c.classification}</span>
                            <h3 style="font-size: 1.25rem; font-weight: 700; color: #fff; margin: 0;">${c.name}</h3>
                            <div style="font-size: 0.875rem; color: var(--secondary); font-weight: 600;">${c.role}</div>
                        </div>
                        <div class="ranking-score-pill" title="Target Ranking Score">
                            ${c.target_score}
                        </div>
                    </div>

                    <div style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 0.75rem;">
                        <div><i class="fa-solid fa-money-bill-wave text-success"></i> CTC: <strong style="color:#fff;">${c.ctc}</strong></div>
                        <div><i class="fa-solid fa-clock text-warning"></i> Deadline: <strong>${c.deadline}</strong> (${c.deadline_urgency})</div>
                    </div>

                    <p style="font-size: 0.825rem; color: #cbd5e1; background: rgba(15,23,42,0.6); padding: 0.6rem 0.85rem; border-radius: 6px; margin-bottom: 1rem; line-height: 1.4;">
                        ${c.ranking_reason}
                    </p>
                </div>

                <div>
                    <div style="font-size: 0.775rem; color: var(--text-muted); margin-bottom: 0.6rem;">
                        Status: <span class="badge badge-info">${appStatus}</span>
                    </div>

                    <div style="display: flex; gap: 0.4rem;">
                        <a href="/placement-strategy/company/${c.id}" class="btn btn-primary btn-sm" style="flex:1; text-align:center;"><i class="fa-solid fa-shield-halved"></i> WAR ROOM</a>
                        <a href="/placements/company/${c.id}" class="btn btn-outline btn-sm" style="flex:1; text-align:center;">PREPARE</a>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

function loadCompanyWarRoomView(companyId) {
    fetch(`/api/placement-strategy/company/${companyId}`)
        .then(res => res.json())
        .then(data => {
            if (data.success && data.data) {
                const w = data.data;
                const c = w.company;

                if (document.getElementById('warCompName')) document.getElementById('warCompName').textContent = c.name;
                if (document.getElementById('warCompRole')) document.getElementById('warCompRole').textContent = c.role;
                if (document.getElementById('warCompCtc')) document.getElementById('warCompCtc').textContent = c.ctc;
                if (document.getElementById('warCompMatch')) document.getElementById('warCompMatch').innerHTML = `Role Match: <strong>${c.resume_match}%</strong>`;
                if (document.getElementById('warTargetStatus')) document.getElementById('warTargetStatus').textContent = c.classification;

                // SHOULD YOU APPLY?
                const dec = w.apply_decision;
                if (document.getElementById('applyDecisionBadge')) {
                    document.getElementById('applyDecisionBadge').textContent = dec.decision;
                    document.getElementById('applyDecisionBadge').className = `badge ${dec.badge_class}`;
                }
                const reasonsContainer = document.getElementById('applyDecisionReasons');
                if (reasonsContainer) {
                    reasonsContainer.innerHTML = dec.reasons.map(r => `
                        <div style="font-size: 0.9rem; color: #fff; margin-bottom: 0.3rem;"><i class="fa-solid fa-check text-success"></i> ${r}</div>
                    `).join('');
                }

                // WHY THIS COMPANY?
                const whyContainer = document.getElementById('warWhyList');
                if (whyContainer) {
                    whyContainer.innerHTML = w.why_list.map(item => `
                        <div class="why-item">
                            <i class="fa-solid fa-circle-check text-success"></i>
                            <span>${item.text}</span>
                        </div>
                    `).join('');
                }

                // WHAT TO PREPARE
                const skillsContainer = document.getElementById('warSkillsList');
                if (skillsContainer) {
                    skillsContainer.innerHTML = w.skills_breakdown.map(s => `
                        <div class="skill-gap-row">
                            <div>
                                <strong style="color:#fff;">${s.skill}</strong>
                                <div style="font-size: 0.775rem; color: var(--text-muted);">Current: ${s.current}% | Required: ${s.required}%</div>
                            </div>
                            <div style="text-align: right;">
                                <span class="badge ${s.gap > 10 ? 'badge-danger' : (s.gap > 0 ? 'badge-warning' : 'badge-success')}">
                                    ${s.gap > 0 ? `Gap: -${s.gap}%` : 'Covered'}
                                </span>
                            </div>
                        </div>
                    `).join('');
                }

                // ROUND-BY-ROUND TIMELINE
                const timelineContainer = document.getElementById('warRoundsTimeline');
                if (timelineContainer) {
                    timelineContainer.innerHTML = w.rounds_timeline.map(r => `
                        <div class="round-card">
                            <div style="display: flex; justify-content: space-between; font-size: 0.8rem; color: var(--secondary); font-weight: 800; margin-bottom: 0.4rem;">
                                <span>ROUND ${r.step}</span>
                                <span class="badge badge-info">${r.readiness}% Readiness</span>
                            </div>
                            <h4 style="font-size: 1rem; color: #fff; margin: 0 0 0.4rem 0;">${r.name}</h4>
                            <div style="font-size: 0.775rem; color: var(--text-muted); margin-bottom: 0.75rem;">
                                Est. Time: ${r.est_time} | Gap: ${r.gap}
                            </div>
                            <a href="${r.route}" class="btn btn-primary btn-sm" style="width: 100%; text-align: center;">${r.button_text}</a>
                        </div>
                    `).join('');
                }

                // 7-DAY WAR PLAN
                const planContainer = document.getElementById('warPlanGrid');
                if (planContainer && w.war_plan) {
                    planContainer.innerHTML = w.war_plan.map(p => `
                        <div style="background: rgba(15,23,42,0.6); border: 1px solid rgba(255,255,255,0.08); border-radius: 8px; padding: 1rem;">
                            <div style="display: flex; justify-content: space-between; margin-bottom: 0.4rem;">
                                <strong style="color: var(--secondary); font-size: 0.85rem;">${p.day}</strong>
                                <span class="badge badge-info">${p.minutes} min</span>
                            </div>
                            <h4 style="color: #fff; margin: 0 0 0.3rem 0; font-size: 0.95rem;">${p.focus}</h4>
                            <p style="font-size: 0.8rem; color: var(--text-muted); margin: 0;">${p.task}</p>
                        </div>
                    `).join('');
                }
            }
        });
}

function applyFromWarRoom() {
    const compName = document.getElementById('warCompName').textContent || "Zenvexa Technologies";
    const roleName = document.getElementById('warCompRole').textContent || "Software Engineer";

    let apps = JSON.parse(localStorage.getItem('careerforge_applications') || '[]');
    let existing = apps.find(a => a.company === compName);
    if (existing) {
        alert(`You have already applied to ${compName}. Status: ${existing.status}`);
        return;
    }

    const newApp = {
        id: Date.now(),
        company: compName,
        role: roleName,
        status: "Applied",
        dateApplied: new Date().toISOString().split('T')[0],
        matchScore: 87,
        atsScore: 84,
        daysWaiting: 0,
        resume_version: "Standard Resume v2"
    };

    apps.unshift(newApp);
    localStorage.setItem('careerforge_applications', JSON.stringify(apps));

    alert(`🎉 Application Submitted from War Room!\n\nDrive: ${compName}\nRole: ${roleName}\nStatus: Applied\n\nSynced with Application Intelligence Command Center!`);
}

function completeAllCommandTasks() {
    let streak = parseInt(localStorage.getItem('careerforge_streak') || '8');
    streak++;
    localStorage.setItem('careerforge_streak', streak.toString());
    alert(`🎯 Today's Placement Command Mission Completed!\n\nStreak updated to 🔥 ${streak} Days!`);
}
