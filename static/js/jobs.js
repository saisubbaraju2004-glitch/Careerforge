document.addEventListener('DOMContentLoaded', function () {
    initJobsMatchingPage();
});

let currentJobsData = [];
let currentProfile = {};
let activeModalJob = null;

function initJobsMatchingPage() {
    // 1. Gather candidate profile context
    const storedPlan = JSON.parse(localStorage.getItem('careerforge_plan_data') || '{}');
    const storedProfile = JSON.parse(localStorage.getItem('careerforge_profile') || '{}');

    currentProfile = {
        target_role: storedPlan.target_role || storedProfile.target_role || "Python Backend Developer",
        skills: storedPlan.strong_skills || storedProfile.current_skills || ["Python", "Flask", "HTML", "CSS", "SQL", "PostgreSQL"],
        missing_skills: storedPlan.missing_skills || ["Docker", "REST APIs", "AWS"],
        readiness_score: storedPlan.readiness_score || 72,
        ats_score: storedProfile.ats_score || 76,
        projects: ["ExamCraft AI Suite"]
    };

    // 2. Fetch Job Matching API
    fetchJobMatches();

    // 3. Event Listeners for Filters & Modal
    setupFilterListeners();
    setupModalListeners();
}

function fetchJobMatches() {
    const keyword = document.getElementById('filterKeyword')?.value || '';
    const workMode = document.getElementById('filterWorkMode')?.value || 'All';
    const experience = document.getElementById('filterExperience')?.value || 'All';
    const matchScore = document.getElementById('filterMatchScore')?.value || 'All';
    const sortJobs = document.getElementById('sortJobs')?.value || 'match';

    const payload = {
        ...currentProfile,
        role_filter: keyword,
        work_mode: workMode,
        experience: experience
    };

    fetch('/api/job-match', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    })
    .then(res => res.json())
    .then(data => {
        if (data.success && data.data) {
            currentJobsData = data.data.all_jobs || [];
            
            // Apply client-side score filtering & sorting
            let processed = filterAndSortJobs(currentJobsData, matchScore, sortJobs);

            renderBannerMetrics(data.data);
            renderTopRecommendations(data.data.top_recommendations || []);
            renderJobCards(processed);
            renderMarketDemand(data.data.skill_demand || []);
        }
    })
    .catch(err => {
        console.error("Error fetching job matches:", err);
    });
}

function filterAndSortJobs(jobs, minScoreFilter, sortKey) {
    let list = [...jobs];

    // Score filter
    if (minScoreFilter !== 'All') {
        const minVal = parseInt(minScoreFilter);
        list = list.filter(j => j.match_score >= minVal);
    }

    // Sort logic
    if (sortKey === 'salary') {
        list.sort((a, b) => (b.salary || '').localeCompare(a.salary || ''));
    } else if (sortKey === 'gap') {
        list.sort((a, b) => a.missing_skills.length - b.missing_skills.length);
    } else {
        list.sort((a, b) => b.match_score - a.match_score);
    }

    return list;
}

function renderBannerMetrics(data) {
    if (document.getElementById('jobsTargetRole')) {
        document.getElementById('jobsTargetRole').textContent = data.target_role;
    }
    if (document.getElementById('jobsReadinessScore')) {
        document.getElementById('jobsReadinessScore').textContent = `${data.readiness_score}%`;
    }
    if (document.getElementById('jobsTotalCount')) {
        document.getElementById('jobsTotalCount').textContent = data.total_matching_jobs;
    }
}

function renderTopRecommendations(recs) {
    const grid = document.getElementById('topRecsGrid');
    if (!grid) return;

    grid.innerHTML = '';
    if (recs.length === 0) {
        grid.innerHTML = '<p class="text-muted">No top recommendations found for current criteria.</p>';
        return;
    }

    recs.slice(0, 3).forEach((job, idx) => {
        const card = document.createElement('div');
        card.className = 'top-rec-card';
        card.innerHTML = `
            <span class="rank-badge">#${idx + 1} Recommendation</span>
            <div class="job-title-block">
                <h3>${job.title}</h3>
                <div class="job-company">${job.company} • ${job.location}</div>
            </div>
            <div class="job-meta-row" style="margin: 0.75rem 0;">
                <span class="job-meta-pill"><i class="fa-solid fa-briefcase"></i> ${job.work_mode}</span>
                <span class="job-meta-pill"><i class="fa-solid fa-indian-rupee-sign"></i> ${job.salary}</span>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 0.5rem;">
                <div class="match-score-badge ${job.badge_color}">
                    <span class="score-num">${job.match_score}%</span>
                    <span class="score-lbl">Match</span>
                </div>
                <button type="button" class="btn btn-secondary btn-sm" onclick="openJobModal('${job.job_id}')">
                    <i class="fa-solid fa-eye"></i> View Analysis
                </button>
            </div>
        `;
        grid.appendChild(card);
    });
}

function renderJobCards(jobs) {
    const container = document.getElementById('jobCardsContainer');
    if (!container) return;

    container.innerHTML = '';
    if (jobs.length === 0) {
        container.innerHTML = '<div class="glass-card" style="grid-column: 1 / -1; padding: 2rem; text-align: center;"><p class="text-muted">No matching jobs found matching filters. Try resetting search filters.</p></div>';
        return;
    }

    jobs.forEach(job => {
        const card = document.createElement('div');
        card.className = 'job-card';

        const matchSkillsHtml = job.matching_skills.slice(0, 4).map(s => `<span class="skill-chip match">✓ ${s}</span>`).join('');
        const missingSkillsHtml = job.missing_skills.length > 0 
            ? `<span class="skill-chip missing">Missing: ${job.missing_skills.slice(0, 2).join(', ')}</span>`
            : '<span class="skill-chip match">✓ All skills matched!</span>';

        card.innerHTML = `
            <div>
                <div class="job-card-header">
                    <div class="job-title-block">
                        <h3>${job.title}</h3>
                        <div class="job-company">${job.company} <span class="data-tag-pill" style="font-size:0.7rem; padding: 0.1rem 0.4rem;">${job.data_label || 'Demo Job Data'}</span></div>
                    </div>
                    <div class="match-score-badge ${job.badge_color}">
                        <span class="score-num">${job.match_score}%</span>
                        <span class="score-lbl">Match</span>
                    </div>
                </div>
                <div class="job-meta-row" style="margin: 0.75rem 0;">
                    <span class="job-meta-pill"><i class="fa-solid fa-location-dot"></i> ${job.location}</span>
                    <span class="job-meta-pill"><i class="fa-solid fa-house-laptop"></i> ${job.work_mode}</span>
                    <span class="job-meta-pill"><i class="fa-solid fa-indian-rupee-sign"></i> ${job.salary}</span>
                    <span class="job-meta-pill"><i class="fa-solid fa-user-graduate"></i> ${job.experience}</span>
                </div>
                <div class="job-skills-wrap">
                    ${matchSkillsHtml}
                    ${missingSkillsHtml}
                </div>
            </div>
            <div class="job-card-actions">
                <button type="button" class="btn btn-secondary" onclick="openJobModal('${job.job_id}')">
                    <i class="fa-solid fa-circle-info"></i> VIEW DETAILS
                </button>
                <button type="button" class="btn btn-primary btn-glow" onclick="applyToJob('${job.job_id}')">
                    <i class="fa-solid fa-paper-plane"></i> APPLY
                </button>
            </div>
        `;
        container.appendChild(card);
    });
}

function renderMarketDemand(demandList) {
    const grid = document.getElementById('demandBarsGrid');
    if (!grid) return;

    grid.innerHTML = '';
    demandList.forEach(item => {
        const row = document.createElement('div');
        row.className = 'demand-bar-item';
        row.innerHTML = `
            <div class="demand-meta">
                <span class="demand-skill-name">${item.skill}</span>
                <span class="demand-pct">${item.percentage}% of dataset jobs</span>
            </div>
            <div class="demand-track">
                <div class="demand-fill" style="width: 0%" data-target="${item.percentage}%"></div>
            </div>
        `;
        grid.appendChild(row);
    });

    setTimeout(() => {
        document.querySelectorAll('.demand-fill').forEach(fill => {
            fill.style.width = fill.getAttribute('data-target');
        });
    }, 100);
}

function setupFilterListeners() {
    const keyword = document.getElementById('filterKeyword');
    const workMode = document.getElementById('filterWorkMode');
    const experience = document.getElementById('filterExperience');
    const matchScore = document.getElementById('filterMatchScore');
    const sortJobs = document.getElementById('sortJobs');
    const btnReset = document.getElementById('btnResetFilters');

    let debounceTimer;
    if (keyword) {
        keyword.addEventListener('input', () => {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(fetchJobMatches, 300);
        });
    }

    [workMode, experience, matchScore, sortJobs].forEach(elem => {
        if (elem) elem.addEventListener('change', fetchJobMatches);
    });

    if (btnReset) {
        btnReset.addEventListener('click', () => {
            if (keyword) keyword.value = '';
            if (workMode) workMode.value = 'All';
            if (experience) experience.value = 'All';
            if (matchScore) matchScore.value = 'All';
            if (sortJobs) sortJobs.value = 'match';
            fetchJobMatches();
        });
    }
}

function openJobModal(jobId) {
    const job = currentJobsData.find(j => j.job_id === jobId);
    if (!job) return;

    activeModalJob = job;

    document.getElementById('modalJobTitle').textContent = job.title;
    document.getElementById('modalJobMeta').textContent = `${job.company} • ${job.location} (${job.work_mode}) • ${job.salary}`;
    document.getElementById('modalScoreNum').textContent = job.match_score;
    
    const pill = document.getElementById('modalReadinessPill');
    if (pill) {
        pill.textContent = `🟢 ${job.apply_readiness}`;
    }

    document.getElementById('modalReadinessReason').textContent = job.apply_reason;

    // Matching & Missing skills
    const matchingUl = document.getElementById('modalMatchingSkills');
    matchingUl.innerHTML = job.matching_skills.map(s => `<li>✓ ${s}</li>`).join('') || '<li>Basic concepts match</li>';

    const missingUl = document.getElementById('modalMissingSkills');
    missingUl.innerHTML = job.missing_skills.map(s => `<li>⚠ ${s}</li>`).join('') || '<li>✓ No major missing skills!</li>';

    document.getElementById('modalAdvantageText').textContent = job.your_advantage;
    document.getElementById('modalGapTime').textContent = `${job.estimated_gap_days} days`;

    // Skill Checklist
    const checklistGrid = document.getElementById('modalSkillChecklist');
    checklistGrid.innerHTML = '';
    job.skill_breakdown.forEach(item => {
        const div = document.createElement('div');
        div.className = 'checklist-item';
        const color = item.type === 'matched' ? '#22c55e' : (item.type === 'gap' ? '#f59e0b' : '#ef4444');
        div.innerHTML = `
            <span>${item.skill}</span>
            <span style="font-weight: 800; color: ${color};">${item.status}</span>
        `;
        checklistGrid.appendChild(div);
    });

    document.getElementById('coachReplyBody').textContent = 'Click "Why should I apply?" for personalized AI application strategy.';

    // Setup Build Resume, Practice Interview & Apply Buttons
    const btnBuild = document.getElementById('btnModalBuildResume');
    if (btnBuild) {
        btnBuild.setAttribute('href', `/resume-builder?job_id=${job.job_id}`);
    }

    const btnPractice = document.getElementById('btnModalPracticeInterview');
    if (btnPractice) {
        btnPractice.setAttribute('href', `/interview?job_id=${job.job_id}`);
    }

    const btnApply = document.getElementById('btnModalApply');
    btnApply.onclick = function (e) {
        e.preventDefault();
        applyToJob(job.job_id);
        closeModal();
    };

    document.getElementById('jobModalBackdrop').style.display = 'flex';
}

function setupModalListeners() {
    const backdrop = document.getElementById('jobModalBackdrop');
    const btnClose = document.getElementById('btnCloseModal');
    const btnModalClose = document.getElementById('btnModalClose');
    const btnAskCoach = document.getElementById('btnAskJobCoach');

    if (btnClose) btnClose.addEventListener('click', closeModal);
    if (btnModalClose) btnModalClose.addEventListener('click', closeModal);

    if (backdrop) {
        backdrop.addEventListener('click', (e) => {
            if (e.target === backdrop) closeModal();
        });
    }

    if (btnAskCoach) {
        btnAskCoach.addEventListener('click', () => {
            if (!activeModalJob) return;
            document.getElementById('coachReplyBody').textContent = 'Analyzing job match requirements...';

            fetch('/api/job-coach', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    job_id: activeModalJob.job_id,
                    profile: currentProfile
                })
            })
            .then(res => res.json())
            .then(data => {
                if (data.success && data.data && data.data.reply) {
                    document.getElementById('coachReplyBody').textContent = data.data.reply;
                }
            })
            .catch(err => {
                document.getElementById('coachReplyBody').textContent = 'Failed to generate pitch.';
            });
        });
    }
}

function closeModal() {
    const backdrop = document.getElementById('jobModalBackdrop');
    if (backdrop) backdrop.style.display = 'none';
}

function applyToJob(jobId) {
    const job = currentJobsData.find(j => j.job_id === jobId);
    if (!job) return;

    const savedResume = JSON.parse(localStorage.getItem('careerforge_resume_data') || '{}');
    const atsEst = savedResume.summary ? 84 : 76;
    const recName = savedResume.target_role ? `${savedResume.target_role} Resume` : "Python Backend Resume";

    const confirmApply = confirm(
        `📄 RESUME CHECK FOR ${job.company.toUpperCase()}\n\n` +
        `• Resume ATS Score: ${atsEst}%\n` +
        `• Job Match Score: ${job.match_score}%\n` +
        `• Recommended Resume: ${recName}\n\n` +
        `Click OK to submit application and sync with Application Tracker (/applications).`
    );

    if (!confirmApply) return;

    // One-click Application Tracker Sync
    let apps = JSON.parse(localStorage.getItem('careerforge_applications') || '[]');
    
    // Prevent duplicate applications
    const existingIndex = apps.findIndex(a => a.id === job.job_id || a.job_url === job.apply_url);
    if (existingIndex === -1) {
        const newApp = {
            id: job.job_id,
            company: job.company,
            role: job.title,
            job_url: job.apply_url,
            location: job.location,
            salary: job.salary,
            applied_date: new Date().toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }),
            status: 'Applied',
            notes: `Matched via CareerForge AI (${job.match_score}% match)`
        };
        apps.unshift(newApp);
        localStorage.setItem('careerforge_applications', JSON.stringify(apps));
    }

    // Open target job URL in new window
    window.open(job.apply_url, '_blank');
}
