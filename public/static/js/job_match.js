// AI Resume + Job Matching Engine Frontend Logic

let allJobMatches = [];
let selectedJobIds = new Set();

document.addEventListener("DOMContentLoaded", function() {
    if (document.getElementById("topJobsGrid")) {
        initJobMatchPage();
    }
});

async function initJobMatchPage() {
    try {
        const response = await fetch("/api/job-match/jobs");
        const data = await response.json();

        if (data.success) {
            allJobMatches = data.jobs;
            renderTopTargetJobs(allJobMatches.slice(0, 4));
            renderJobsTable(allJobMatches);
            loadMissingSkillsOverview();
        }
    } catch (err) {
        console.error("Error loading job matches:", err);
    }
}

function renderTopTargetJobs(topJobs) {
    const container = document.getElementById("topJobsGrid");
    if (!container) return;

    if (!topJobs || topJobs.length === 0) {
        container.innerHTML = `<p style="color: var(--text-muted);">No top target jobs found.</p>`;
        return;
    }

    container.innerHTML = topJobs.map(job => `
        <div class="top-job-card">
            <div>
                <div class="match-ring-box">
                    <span class="badge ${job.color_class}">${job.badge}</span>
                    <span class="match-percentage ${job.color_class}">${job.match_score}%</span>
                </div>
                <h4 style="font-size: 1.15rem; font-weight: 700; color: #fff; margin: 0 0 0.2rem 0;">${job.title}</h4>
                <p style="font-size: 0.85rem; color: var(--text-muted); margin: 0 0 0.75rem 0;">${job.company} &bull; ${job.location}</p>

                <div style="margin-bottom: 0.75rem;">
                    <div style="font-size: 0.75rem; color: var(--text-muted); margin-bottom: 0.3rem;">SKILLS MATCHED:</div>
                    <div class="skills-flex">
                        ${job.matched_skills.slice(0, 4).map(s => `<span class="skill-tag matched">${s}</span>`).join('')}
                    </div>
                </div>
            </div>

            <div style="margin-top: 1rem; display: flex; gap: 0.5rem;">
                <a href="/job-match/job/${job.job_id}" class="btn btn-primary btn-sm" style="flex: 1; text-align: center;">
                    <i class="fa-solid fa-chart-line"></i> View Breakdown
                </a>
            </div>
        </div>
    `).join('');
}

function renderJobsTable(jobs) {
    const tbody = document.getElementById("jobsTableBody");
    if (!tbody) return;

    if (!jobs || jobs.length === 0) {
        tbody.innerHTML = `<tr><td colspan="7" style="text-align: center; color: var(--text-muted);">No jobs match your filter.</td></tr>`;
        return;
    }

    tbody.innerHTML = jobs.map(job => {
        const isChecked = selectedJobIds.has(job.job_id) ? "checked" : "";
        const missingSkillList = job.missing_skills.length > 0
            ? job.missing_skills.slice(0, 3).map(s => `<span class="skill-tag missing">${s}</span>`).join(' ')
            : `<span style="color: #10b981; font-weight: 600;">100% Skill Fit</span>`;

        return `
            <tr>
                <td>
                    <input type="checkbox" value="${job.job_id}" ${isChecked} onchange="toggleJobSelection('${job.job_id}', this.checked)">
                </td>
                <td>
                    <strong style="color: #fff;">${job.title}</strong><br>
                    <span style="font-size: 0.8rem; color: var(--text-muted);">${job.company} (${job.work_mode})</span>
                </td>
                <td>
                    <span class="badge ${job.color_class}" style="font-family: 'JetBrains Mono'; font-weight: 700;">${job.match_score}%</span>
                </td>
                <td>
                    <span style="font-size: 0.85rem;">${job.matched_skills.length} / ${job.matched_skills.length + job.missing_skills.length} Skills</span>
                </td>
                <td>
                    <div class="skills-flex">${missingSkillList}</div>
                </td>
                <td>
                    <span class="badge badge-info" style="font-size: 0.75rem;">${job.deadline !== 'Open' ? 'Campus Drive' : 'Direct Apply'}</span>
                </td>
                <td>
                    <a href="/job-match/job/${job.job_id}" class="btn btn-outline btn-sm">
                        <i class="fa-solid fa-eye"></i> Detail
                    </a>
                </td>
            </tr>
        `;
    }).join('');
}

function toggleJobSelection(jobId, isChecked) {
    if (isChecked) {
        selectedJobIds.add(jobId);
    } else {
        selectedJobIds.delete(jobId);
    }
    const countEl = document.getElementById("compareCount");
    if (countEl) countEl.innerText = selectedJobIds.size;
}

function toggleSelectAllJobs(masterCheckbox) {
    const checkboxes = document.querySelectorAll("#jobsTableBody input[type='checkbox']");
    checkboxes.forEach(cb => {
        cb.checked = masterCheckbox.checked;
        toggleJobSelection(cb.value, cb.checked);
    });
}

function filterJobsTable() {
    const searchVal = (document.getElementById("jobSearchInput")?.value || "").toLowerCase();
    const filterLevel = document.getElementById("matchFilterSelect")?.value || "all";

    let filtered = allJobMatches.filter(j => {
        const textMatch = j.title.toLowerCase().includes(searchVal) ||
                          j.company.toLowerCase().includes(searchVal) ||
                          j.matched_skills.some(s => s.toLowerCase().includes(searchVal));

        if (!textMatch) return false;

        if (filterLevel === "high") return j.match_score >= 85;
        if (filterLevel === "good") return j.match_score >= 70 && j.match_score < 85;
        if (filterLevel === "moderate") return j.match_score >= 50 && j.match_score < 70;

        return true;
    });

    renderJobsTable(filtered);
}

async function loadMissingSkillsOverview() {
    try {
        const res = await fetch("/api/job-match/skills");
        const data = await res.json();

        const grid = document.getElementById("skillsGapGrid");
        if (!grid) return;

        if (data.success && data.skills && data.skills.length > 0) {
            grid.innerHTML = data.skills.map(s => `
                <div class="glass-card" style="padding: 1rem;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                        <strong style="color: #fff; font-size: 1rem;">${s.skill}</strong>
                        <span class="badge badge-warning">${s.potential_boost}</span>
                    </div>
                    <p style="font-size: 0.8rem; color: var(--text-muted); margin: 0;">
                        Required across <strong>${s.occurrence_count}</strong> target jobs. Estimated learning effort: <strong>${s.estimated_study_hours}h</strong>.
                    </p>
                </div>
            `).join('');
        } else {
            grid.innerHTML = `<p style="color: var(--text-muted);">No major skill gaps identified across target roles!</p>`;
        }
    } catch (e) {
        console.error("Error loading missing skills:", e);
    }
}

async function triggerCompareModal() {
    if (selectedJobIds.size < 2) {
        alert("Please select at least 2 jobs using checkboxes to compare side-by-side.");
        return;
    }

    try {
        const res = await fetch("/api/job-match/compare", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ job_ids: Array.from(selectedJobIds) })
        });
        const data = await res.json();

        if (data.success && data.comparison) {
            renderComparisonBody(data.comparison);
            document.getElementById("compareModal").classList.add("active");
        }
    } catch (e) {
        console.error("Compare jobs error:", e);
    }
}

function renderComparisonBody(comp) {
    const body = document.getElementById("compareModalBody");
    if (!body) return;

    const jobs = comp.compared_jobs;
    body.innerHTML = `
        <div style="background: rgba(15,23,42,0.8); border: 1px solid rgba(16,185,129,0.3); border-radius: 10px; padding: 1rem; margin-bottom: 1.5rem;">
            <h4 style="color: #10b981; margin: 0 0 0.3rem 0;"><i class="fa-solid fa-trophy"></i> Top Recommended Target: ${comp.top_recommendation}</h4>
            <p style="color: var(--text-muted); font-size: 0.85rem; margin: 0;">${comp.reason}</p>
        </div>

        <div style="display: grid; grid-template-columns: repeat(${jobs.length}, 1fr); gap: 1rem;">
            ${jobs.map(j => `
                <div class="glass-card" style="padding: 1rem;">
                    <span class="badge ${j.color_class}" style="margin-bottom: 0.5rem;">${j.match_score}% MATCH</span>
                    <h4 style="color: #fff; margin: 0 0 0.3rem 0; font-size: 1rem;">${j.title}</h4>
                    <p style="font-size: 0.8rem; color: var(--text-muted); margin: 0 0 1rem 0;">${j.company} &bull; ${j.salary}</p>

                    <div style="margin-bottom: 0.75rem;">
                        <strong style="font-size: 0.75rem; color: var(--text-muted);">MATCHED SKILLS:</strong>
                        <div class="skills-flex" style="margin-top: 0.2rem;">
                            ${j.matched_skills.map(s => `<span class="skill-tag matched">${s}</span>`).join('')}
                        </div>
                    </div>

                    <div>
                        <strong style="font-size: 0.75rem; color: var(--text-muted);">MISSING GAPS:</strong>
                        <div class="skills-flex" style="margin-top: 0.2rem;">
                            ${j.missing_skills.length > 0 ? j.missing_skills.map(s => `<span class="skill-tag missing">${s}</span>`).join('') : '<span style="color:#10b981; font-size:0.8rem;">None</span>'}
                        </div>
                    </div>
                </div>
            `).join('')}
        </div>
    `;
}

function closeCompareModal() {
    document.getElementById("compareModal")?.classList.remove("active");
}

function openCustomAnalyzeModal() {
    document.getElementById("customJDModal")?.classList.add("active");
}

function closeCustomAnalyzeModal() {
    document.getElementById("customJDModal")?.classList.remove("active");
}

async function submitCustomJDAnalysis() {
    const title = document.getElementById("customRoleTitle")?.value;
    const company = document.getElementById("customCompany")?.value;
    const description = document.getElementById("customJDText")?.value;

    if (!description || description.trim().length < 20) {
        alert("Please paste a complete job description.");
        return;
    }

    try {
        const res = await fetch("/api/job-match/analyze", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ title, company, description })
        });
        const data = await res.json();

        if (data.success && data.match) {
            closeCustomAnalyzeModal();
            window.location.href = `/job-match/job/${data.match.job_id}`;
        }
    } catch (e) {
        console.error("Custom JD error:", e);
    }
}

// Detail Page JS Loader
async function loadJobMatchDetail(jobId) {
    try {
        const res = await fetch(`/api/job-match/job/${jobId}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" }
        });
        const data = await res.json();

        if (!data.success) {
            alert("Error loading job details: " + data.error);
            return;
        }

        const job = data.job;
        const prio = data.apply_priority;

        document.getElementById("detailJobTitle").innerText = job.title;
        document.getElementById("detailCompanySub").innerText = `${job.company} • ${job.location} • ${job.salary}`;

        const badgeEl = document.getElementById("detailMatchBadge");
        badgeEl.className = `badge ${job.color_class}`;
        badgeEl.innerText = `${job.match_score}% ${job.badge}`;

        document.getElementById("detailOverallScore").innerText = `${job.match_score}%`;
        document.getElementById("detailDecisionTitle").innerText = prio.decision;
        document.getElementById("detailDecisionReason").innerText = prio.reason;

        const prioBadge = document.getElementById("detailPriorityBadge");
        prioBadge.className = `badge ${prio.badge_class || 'badge-purple'}`;
        prioBadge.innerText = `PRIORITY SCORE ${prio.priority_score}/100`;

        const applyLink = document.getElementById("btnApplyNowLink");
        if (applyLink) applyLink.href = job.apply_url || "#";

        const interviewLink = document.getElementById("btnStartInterviewLink");
        if (interviewLink) interviewLink.href = `/interview?job_id=${job.job_id}`;

        // Render 7-factor breakdown
        renderFactorBreakdown(job.breakdown);

        // Render skills
        document.getElementById("detailMatchedSkills").innerHTML = job.matched_skills.map(s => `<span class="skill-tag matched">${s}</span>`).join(' ');
        document.getElementById("detailMissingSkills").innerHTML = job.missing_skills.length > 0
            ? job.missing_skills.map(s => `<span class="skill-tag missing">${s}</span>`).join(' ')
            : `<span style="color: #10b981; font-weight: 600;">No skill gaps missing!</span>`;

        // Generate tailored bullets
        generateDetailBulletSuggestions(job);

    } catch (e) {
        console.error("Load job detail error:", e);
    }
}

function renderFactorBreakdown(breakdown) {
    const grid = document.getElementById("factorBreakdownGrid");
    if (!grid || !breakdown) return;

    const factors = [
        { name: "Technical Skill Match", val: breakdown.skill_match, color: "#10b981" },
        { name: "Target Role Relevance", val: breakdown.role_match, color: "#3b82f6" },
        { name: "Academic / Eligibility Fit", val: breakdown.education_match, color: "#8b5cf6" },
        { name: "Experience Alignment", val: breakdown.experience_match, color: "#ec4899" },
        { name: "Project Stack Fit", val: breakdown.project_match, color: "#06b6d4" },
        { name: "Resume Keyword Match", val: breakdown.keyword_match, color: "#f59e0b" },
        { name: "ATS Compatibility", val: breakdown.ats_compatibility, color: "#6366f1" }
    ];

    grid.innerHTML = factors.map(f => `
        <div class="factor-card">
            <div class="factor-header">
                <span style="color: var(--text-muted);">${f.name}</span>
                <span style="color: ${f.color};">${f.val}%</span>
            </div>
            <div class="factor-progress-bar">
                <div class="factor-progress-fill" style="width: ${f.val}%; background: ${f.color};"></div>
            </div>
        </div>
    `).join('');
}

async function generateDetailBulletSuggestions(jobData) {
    const container = document.getElementById("tailoredBulletsList");
    if (!container) return;

    container.innerHTML = `<p style="color: var(--text-muted); font-size: 0.9rem;"><i class="fa-solid fa-spinner fa-spin"></i> Generating tailored ATS bullet suggestions...</p>`;

    try {
        const title = jobData ? jobData.title : document.getElementById("detailJobTitle")?.innerText;
        const company = jobData ? jobData.company : "";

        const res = await fetch("/api/job-match/resume-improvements", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ title, company })
        });
        const data = await res.json();

        if (data.success && data.improvements) {
            const bullets = data.improvements.tailored_bullets || [];
            container.innerHTML = bullets.map(b => `
                <div class="tailored-bullet-item">
                    <i class="fa-solid fa-circle-dot text-accent" style="font-size: 0.7rem; margin-right: 0.4rem;"></i>
                    ${b}
                </div>
            `).join('');
        }
    } catch (e) {
        console.error("Bullet generation error:", e);
        container.innerHTML = `<p style="color: #ef4444;">Unable to generate bullet suggestions right now.</p>`;
    }
}
