window.DashboardRenderer = {
    render: function(data) {
        if (!data) return;

        // Render AI Fallback Banner if Gemini is unavailable
        const noticeContainer = document.getElementById('aiFallbackNotice');
        if (noticeContainer) {
            if (data.ai_fallback_notice) {
                noticeContainer.innerHTML = `<div class="ai-verify-notice" style="margin-bottom: 1rem;"><i class="fa-solid fa-triangle-exclamation"></i> <span>${data.ai_fallback_notice}</span></div>`;
                noticeContainer.classList.remove('hidden');
            } else {
                noticeContainer.classList.add('hidden');
            }
        }

        // 1. Meta & Readiness Score Gauge
        document.getElementById('dashCandidateName').innerText = data.candidate_name || 'Candidate';
        document.getElementById('dashTargetRole').innerText = data.target_role || 'Software Engineer';
        
        const score = data.readiness_score || 50;
        document.getElementById('dashReadinessScore').innerText = score + '%';
        
        const strongCnt = (data.strong_skills || []).length;
        const totalReq = Math.max(1, strongCnt + (data.missing_skills || []).length);
        const coveragePct = Math.round((strongCnt / totalReq) * 100);
        const covEl = document.getElementById('dashSkillCoverage');
        if (covEl) covEl.innerText = `${coveragePct}%`;

        // Save persistent profile in localStorage
        try {
            localStorage.setItem('careerforge_profile', JSON.stringify({
                candidateName: data.candidate_name,
                targetRole: data.target_role,
                skills: data.strong_skills,
                readinessScore: score,
                atsScore: 83,
                planDay: 12
            }));
        } catch (e) {}

        // 2. Next Best Action
        if (data.next_best_action) {
            this.renderNextBestAction(data.next_best_action);
        }

        // 3. Skill Gap Lists
        this.renderTags('strongSkillsList', data.strong_skills, 'strong');
        this.renderTags('improveSkillsList', data.improvement_skills, 'improve');
        this.renderTags('missingSkillsList', data.missing_skills, 'missing');

        // 4. Skill Heatmap
        if (data.skill_heatmap) {
            this.renderSkillHeatmap(data.skill_heatmap);
        }

        // 5. Career Diagnosis
        this.renderDiagnosis(data.diagnosis);

        // 6. 30-Day Plan Timeline
        this.render30DayPlan(data.thirty_day_plan, data.resources);

        // 7. Portfolio Project
        this.renderProject(data.recommended_project);

        this.loadMissionState();
    },

    renderNextBestAction: function(act) {
        const titleEl = document.getElementById('nextActionTitle');
        const whyEl = document.getElementById('nextActionWhy');
        const btnEl = document.getElementById('nextActionBtn');

        if (titleEl) titleEl.innerText = act.action;
        if (whyEl) whyEl.innerText = act.why;
        if (btnEl) {
            btnEl.innerText = act.button_text || 'Start Action';
            btnEl.onclick = () => {
                if (window.AppRouter && act.target_tab) {
                    if (act.target_tab.startsWith('tab')) {
                        window.AppRouter.switchTab(act.target_tab);
                    } else {
                        window.location.href = `/${act.target_tab}`;
                    }
                }
            };
        }
    },

    renderSkillHeatmap: function(heatmapData) {
        const container = document.getElementById('heatmapGridContainer');
        if (!container || !heatmapData) return;

        let html = '';
        for (const [catName, skills] of Object.entries(heatmapData)) {
            html += `
                <div class="skill-category-block">
                    <h4 class="skill-cat-title"><i class="fa-solid fa-code text-cyan"></i> ${catName}</h4>
                    <div style="display: flex; flex-direction: column; gap: 0.6rem; margin-top: 0.5rem;">
                        ${skills.map(s => {
                            const bg = s.status === 'GREEN' ? 'var(--success)' : s.status === 'YELLOW' ? 'var(--warning)' : s.status === 'RED' ? 'var(--danger)' : 'rgba(255,255,255,0.2)';
                            return `
                                <div>
                                    <div style="display: flex; justify-content: space-between; font-size: 0.8rem; font-weight: 600; margin-bottom: 0.2rem;">
                                        <span>${s.name}</span>
                                        <span style="color: ${bg};">${s.label} (${s.level}/5)</span>
                                    </div>
                                    <div class="factor-bar-bg" style="height: 6px;">
                                        <div class="factor-bar-fill" style="width: ${s.percentage}%; background: ${bg};"></div>
                                    </div>
                                </div>
                            `;
                        }).join('')}
                    </div>
                </div>
            `;
        }
        container.innerHTML = html;
    },

    saveMissionState: function() {
        const chks = document.querySelectorAll('.mission-chk');
        const state = {};
        chks.forEach(c => state[c.id] = c.checked);
        try {
            localStorage.setItem('careerforge_mission_state', JSON.stringify(state));
        } catch (e) {}
    },

    loadMissionState: function() {
        try {
            const state = JSON.parse(localStorage.getItem('careerforge_mission_state') || '{}');
            for (const [id, checked] of Object.entries(state)) {
                const el = document.getElementById(id);
                if (el) el.checked = checked;
            }
        } catch (e) {}
    },


    renderTags: function(containerId, skills, typeClass) {
        const container = document.getElementById(containerId);
        if (!container) return;

        if (!skills || skills.length === 0) {
            container.innerHTML = '<span style="color: var(--text-muted); font-size: 0.85rem;">None identified</span>';
            return;
        }

        container.innerHTML = skills.map(skill => 
            `<span class="tag-pill ${typeClass}">${skill}</span>`
        ).join('');
    },

    renderDiagnosis: function(diagnosis) {
        if (!diagnosis) return;

        const summaryEl = document.getElementById('diagnosisSummary');
        if (summaryEl) summaryEl.innerText = diagnosis.diagnosis_summary || '';

        const blockersList = document.getElementById('blockersList');
        if (blockersList && diagnosis.blockers) {
            blockersList.innerHTML = diagnosis.blockers.map(b => `
                <div class="blocker-item ${b.impact}">
                    <div class="blocker-rank">${b.rank || '01'}</div>
                    <div class="blocker-info">
                        <h5>${b.skill} <span class="badge badge-${b.impact === 'HIGH' ? 'danger' : 'warning'}">${b.impact} IMPACT</span></h5>
                        <p>${b.reason}</p>
                    </div>
                </div>
            `).join('');
        }

        const adviceEl = document.getElementById('priorityAdviceText');
        if (adviceEl && diagnosis.priority_advice) {
            adviceEl.innerText = diagnosis.priority_advice;
        }
    },

    renderRoadmapNodes: function(roadmapData) {
        const container = document.getElementById('roadmapNodesFlow');
        if (!container || !roadmapData || !roadmapData.nodes) return;

        container.innerHTML = roadmapData.nodes.map((node, index) => {
            const arrowHtml = index < roadmapData.nodes.length - 1 ? `<div class="roadmap-arrow"><i class="fa-solid fa-arrow-down"></i></div>` : '';
            return `
                <div class="roadmap-node-card ${node.status}">
                    <div class="node-left">
                        <span class="node-number">${index + 1}</span>
                        <span class="node-title">${node.name}</span>
                    </div>
                    <div class="node-status-pill ${node.status}">
                        <span>${node.badge}</span>
                        <span>${node.status_label}</span>
                    </div>
                </div>
                ${arrowHtml}
            `;
        }).join('');
    },

    render30DayPlan: function(plan, resources) {
        const container = document.getElementById('thirtyDayTimeline');
        if (!container) return;

        if (!plan || plan.length === 0) {
            container.innerHTML = '<p style="color: var(--text-muted);">No timeline plan available.</p>';
            return;
        }

        // Store plan data on window object for filtering
        window._currentPlan = plan;
        window._currentResources = resources;

        // Render week filter buttons and day cards container
        let html = `
            <div class="plan-week-filters" style="display: flex; gap: 0.5rem; margin-bottom: 1.25rem; flex-wrap: wrap;">
                <button class="btn btn-sm btn-secondary week-filter-btn active" onclick="window.DashboardRenderer.filterPlanWeek('all')">All Days (30)</button>
                <button class="btn btn-sm btn-secondary week-filter-btn" onclick="window.DashboardRenderer.filterPlanWeek(1)">Week 1 (Days 1-7)</button>
                <button class="btn btn-sm btn-secondary week-filter-btn" onclick="window.DashboardRenderer.filterPlanWeek(2)">Week 2 (Days 8-14)</button>
                <button class="btn btn-sm btn-secondary week-filter-btn" onclick="window.DashboardRenderer.filterPlanWeek(3)">Week 3 (Days 15-21)</button>
                <button class="btn btn-sm btn-secondary week-filter-btn" onclick="window.DashboardRenderer.filterPlanWeek(4)">Week 4 (Days 22-30)</button>
            </div>
            <div id="planDaysContainer" class="timeline-day-cards-list"></div>
        `;
        container.innerHTML = html;
        this.filterPlanWeek('all');
    },

    filterPlanWeek: function(weekNum) {
        const container = document.getElementById('planDaysContainer');
        const plan = window._currentPlan;
        const resources = window._currentResources;
        if (!container || !plan) return;

        // Highlight active filter button
        document.querySelectorAll('.week-filter-btn').forEach(btn => {
            btn.classList.remove('active');
            btn.classList.remove('btn-primary');
        });

        let filteredPlan = plan;
        if (weekNum === 1) filteredPlan = plan.filter(d => d.day >= 1 && d.day <= 7);
        else if (weekNum === 2) filteredPlan = plan.filter(d => d.day >= 8 && d.day <= 14);
        else if (weekNum === 3) filteredPlan = plan.filter(d => d.day >= 15 && d.day <= 21);
        else if (weekNum === 4) filteredPlan = plan.filter(d => d.day >= 22 && d.day <= 30);

        container.innerHTML = filteredPlan.map((item, idx) => {
            const chks = item.checkpoints || [];
            const resUrl = item.resource || (resources && resources[item.topic] ? resources[item.topic].documentation : null);
            const resLinkHtml = resUrl ? `<a href="${resUrl}" target="_blank" rel="noopener" class="chk-item" style="color: var(--secondary); text-decoration: none;"><i class="fa-solid fa-up-right-from-square"></i> Learning Link</a>` : '';
            
            // Expand first item by default for quick view
            const isExpanded = idx === 0 ? 'expanded' : '';

            return `
                <div class="timeline-day-card collapsible-card ${isExpanded}" id="dayCard-${item.day}">
                    <div class="day-card-header" onclick="window.DashboardRenderer.toggleDayCard(${item.day})">
                        <div style="display: flex; align-items: center; gap: 0.85rem;">
                            <div class="day-badge">Day ${item.day}</div>
                            <h4 style="margin: 0; font-size: 1rem;">${item.topic} <span style="font-size: 0.8rem; font-weight: normal; color: var(--secondary);">(${item.time_est})</span></h4>
                        </div>
                        <i class="fa-solid fa-chevron-down day-toggle-icon"></i>
                    </div>
                    <div class="day-card-body">
                        ${item.learning_objectives ? `<p style="font-size: 0.88rem; color: var(--text-muted); margin-bottom: 0.5rem;"><strong>Objectives:</strong> ${item.learning_objectives.join(', ')}</p>` : ''}
                        <p class="day-task" style="margin-bottom: 0.6rem;"><strong>Hands-on Task:</strong> ${item.hands_on_task}</p>
                        <div class="day-checkpoints">
                            ${chks.map(c => `<span class="chk-item">${c}</span>`).join('')}
                            ${resLinkHtml}
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    },

    toggleDayCard: function(dayNum) {
        const card = document.getElementById(`dayCard-${dayNum}`);
        if (card) {
            card.classList.toggle('expanded');
        }
    },


    renderProject: function(project) {
        if (!project) return;

        const titleEl = document.getElementById('projTitle');
        if (titleEl) titleEl.innerText = project.title || 'Portfolio Capstone API';

        const whyEl = document.getElementById('projWhy');
        if (whyEl) whyEl.innerText = project.why_this_project || '';

        const techContainer = document.getElementById('projTechTags');
        if (techContainer && project.technologies) {
            techContainer.innerHTML = project.technologies.map(t => `<span class="tag-pill strong">${t}</span>`).join('');
        }

        const weeksContainer = document.getElementById('projWeeksGrid');
        if (weeksContainer && project.roadmap) {
            weeksContainer.innerHTML = project.roadmap.map(w => `
                <div class="week-card">
                    <h5>${w.week}</h5>
                    <p>${w.focus}</p>
                </div>
            `).join('');
        }
    },

    renderATSResults: function(atsData) {
        if (!atsData) return;

        const scoreNum = document.getElementById('atsScoreNum');
        if (scoreNum) scoreNum.innerText = atsData.ats_score || 75;

        const factorBars = document.getElementById('atsFactorBars');
        if (factorBars && atsData.score_breakdown) {
            const b = atsData.score_breakdown;
            factorBars.innerHTML = `
                ${this._renderFactorRow('Keyword Match', b.keyword_match)}
                ${this._renderFactorRow('Skills Match', b.skills_match)}
                ${this._renderFactorRow('Target Role Relevance', b.role_relevance)}
                ${this._renderFactorRow('Resume Structure', b.structure)}
                ${this._renderFactorRow('Formatting', b.formatting)}
            `;
        }

        const rewritesList = document.getElementById('bulletRewritesList');
        if (rewritesList && atsData.bullet_rewrites) {
            rewritesList.innerHTML = atsData.bullet_rewrites.map(rw => `
                <div class="rewrite-card">
                    <div class="rw-original"><i class="fa-solid fa-xmark"></i> "${rw.original}"</div>
                    <div class="rw-suggested"><i class="fa-solid fa-check"></i> "${rw.suggested}"</div>
                    <div class="rw-reasoning"><i class="fa-solid fa-circle-info"></i> ${rw.reasoning}</div>
                    <div style="margin-top: 0.5rem; font-size: 0.75rem; color: var(--warning); font-style: italic;">
                        <i class="fa-solid fa-triangle-exclamation"></i> AI Suggestion — Verify that this accurately represents your real experience.
                    </div>
                </div>
            `).join('');
        }
    },


    _renderFactorRow: function(label, pct) {
        return `
            <div class="factor-row">
                <div class="factor-label-row">
                    <span>${label}</span>
                    <span>${pct}%</span>
                </div>
                <div class="factor-bar-bg">
                    <div class="factor-bar-fill" style="width: ${pct}%;"></div>
                </div>
            </div>
        `;
    },

    renderJobPortals: function(jobLinks) {
        const container = document.getElementById('jobPortalsGrid');
        if (!container || !jobLinks) return;

        container.innerHTML = jobLinks.map(j => `
            <div class="portal-card">
                <div class="portal-icon"><i class="fa-brands fa-${j.icon || 'linkedin'}"></i></div>
                <h4>${j.portal_name}</h4>
                <a href="${j.url}" target="_blank" rel="noopener" class="btn btn-secondary btn-sm">
                    Search Jobs <i class="fa-solid fa-arrow-up-right-from-square"></i>
                </a>
            </div>
        `).join('');
    }
};
