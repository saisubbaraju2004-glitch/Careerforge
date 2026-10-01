document.addEventListener('DOMContentLoaded', function () {
    initResumeBuilder();
});

let resumeData = {};
let currentTemplate = 'modern';
let activeJobContext = null;

function initResumeBuilder() {
    // 1. Check job_id query parameter
    const urlParams = new URLSearchParams(window.location.search);
    const jobId = urlParams.get('job_id');

    if (jobId) {
        fetch(`/api/jobs/${jobId}`)
            .then(res => res.json())
            .then(data => {
                if (data.success && data.data) {
                    activeJobContext = data.data;
                    document.getElementById('rbTargetRole').textContent = activeJobContext.title;
                    loadInitialResumeData(activeJobContext);
                } else {
                    loadInitialResumeData();
                }
            })
            .catch(() => loadInitialResumeData());
    } else {
        loadInitialResumeData();
    }

    // 2. Setup event listeners
    setupFormListeners();
    setupTemplateSelector();
    setupActionButtons();
}

function loadInitialResumeData(jobContext = null) {
    const saved = localStorage.getItem('careerforge_resume_data');
    const profile = JSON.parse(localStorage.getItem('careerforge_profile') || '{}');
    const plan = JSON.parse(localStorage.getItem('careerforge_plan_data') || '{}');

    if (saved) {
        try {
            resumeData = JSON.parse(saved);
        } catch (e) {
            resumeData = getDefaultResumeState(profile, plan, jobContext);
        }
    } else {
        resumeData = getDefaultResumeState(profile, plan, jobContext);
    }

    if (jobContext) {
        resumeData.target_role = jobContext.title;
    }

    populateFormFromData();
    renderLivePreview();
    analyzeResumeATS();
    loadSavedVersionsList();
}

function getDefaultResumeState(profile, plan, jobContext) {
    return {
        personal: {
            name: profile.name || "G.Subbaraju",
            email: profile.email || "subbaraju@example.com",
            phone: profile.phone || "+91 98765 43210",
            location: profile.location || "Bengaluru, India",
            linkedin: profile.linkedin || "linkedin.com/in/subbaraju",
            github: profile.github || "github.com/subbaraju"
        },
        target_role: jobContext ? jobContext.title : (plan.target_role || "Python Backend Developer"),
        summary: "Results-oriented Computer Science candidate targeting Python Backend Developer positions. Proficient in Python, Flask, SQL, and REST APIs, with hands-on experience developing modular application components, backend endpoints, and database schemas.",
        skills: plan.strong_skills || ["Python", "Flask", "FastAPI", "SQL", "PostgreSQL", "REST APIs", "Git", "Docker"],
        projects: [
            {
                name: "ExamCraft AI Suite",
                technologies: "Python, Flask, PostgreSQL, REST APIs",
                description: "Production-grade automated exam generation platform utilizing Flask microservices and database connection pools."
            }
        ],
        experience: [
            {
                company: "TechForge Solutions",
                role: "Backend Software Developer Intern",
                duration: "Jun 2026 – Aug 2026",
                description: "Engineered clean OpenAPI endpoints using Python Flask, optimized SQL database query latency, and authored unit tests."
            }
        ],
        education: {
            degree: "B.Tech in Computer Science",
            college: "Engineering College",
            year: "2027",
            cgpa: "8.5 / 10"
        },
        certifications: "Python Professional Certificate, REST API Specialist",
        achievements: "Secured 1st Rank in College CodeForge Hackathon 2026. Member of Core Developer Club."
    };
}

function populateFormFromData() {
    const p = resumeData.personal || {};
    document.getElementById('piName').value = p.name || '';
    document.getElementById('piEmail').value = p.email || '';
    document.getElementById('piPhone').value = p.phone || '';
    document.getElementById('piLocation').value = p.location || '';
    document.getElementById('piLinkedin').value = p.linkedin || '';
    document.getElementById('piGithub').value = p.github || '';

    document.getElementById('summaryText').value = resumeData.summary || '';

    // Skills split across categories
    const s = resumeData.skills || [];
    document.getElementById('skillsProg').value = s.filter(sk => ['Python', 'SQL', 'JavaScript', 'HTML', 'CSS', 'C++'].includes(sk)).join(', ') || 'Python, SQL, JavaScript';
    document.getElementById('skillsFw').value = s.filter(sk => ['Flask', 'FastAPI', 'Django', 'REST APIs', 'React'].includes(sk)).join(', ') || 'Flask, FastAPI, REST APIs';
    document.getElementById('skillsDb').value = s.filter(sk => ['PostgreSQL', 'SQLite', 'Redis', 'MySQL'].includes(sk)).join(', ') || 'PostgreSQL, SQLite, Redis';
    document.getElementById('skillsTools').value = s.filter(sk => ['Git', 'Docker', 'VS Code', 'Linux', 'AWS'].includes(sk)).join(', ') || 'Git, Docker, Linux';

    // Projects list
    renderProjectsForm();

    // Experience list
    renderExperienceForm();

    // Education
    const ed = resumeData.education || {};
    document.getElementById('eduDegree').value = ed.degree || '';
    document.getElementById('eduCollege').value = ed.college || '';
    document.getElementById('eduYear').value = ed.year || '';
    document.getElementById('eduCgpa').value = ed.cgpa || '';

    document.getElementById('certificationsText').value = resumeData.certifications || '';
    document.getElementById('achievementsText').value = resumeData.achievements || '';
}

function renderProjectsForm() {
    const container = document.getElementById('projectsContainer');
    if (!container) return;

    container.innerHTML = '';
    (resumeData.projects || []).forEach((proj, idx) => {
        const item = document.createElement('div');
        item.className = 'project-form-item';
        item.style.marginBottom = '1rem';
        item.style.borderBottom = '1px solid rgba(255,255,255,0.05)';
        item.style.paddingBottom = '0.75rem';

        item.innerHTML = `
            <div class="grid-2">
                <div class="form-group">
                    <label>Project Name</label>
                    <input type="text" class="form-control proj-name" data-idx="${idx}" value="${proj.name || ''}">
                </div>
                <div class="form-group">
                    <label>Technologies Used</label>
                    <input type="text" class="form-control proj-tech" data-idx="${idx}" value="${proj.technologies || ''}">
                </div>
            </div>
            <div class="form-group" style="margin-top: 0.5rem;">
                <label>Description & Contribution</label>
                <textarea class="form-control proj-desc" data-idx="${idx}" rows="2">${proj.description || ''}</textarea>
                <button type="button" class="btn-bullet-improve" onclick="improveProjectBullet(${idx})">
                    <i class="fa-solid fa-wand-magic-sparkles"></i> IMPROVE BULLET
                </button>
            </div>
        `;
        container.appendChild(item);
    });
}

function renderExperienceForm() {
    const container = document.getElementById('experienceContainer');
    if (!container) return;

    container.innerHTML = '';
    (resumeData.experience || []).forEach((exp, idx) => {
        const item = document.createElement('div');
        item.className = 'exp-form-item';
        item.style.marginBottom = '1rem';
        item.style.borderBottom = '1px solid rgba(255,255,255,0.05)';
        item.style.paddingBottom = '0.75rem';

        item.innerHTML = `
            <div class="grid-2">
                <div class="form-group">
                    <label>Company</label>
                    <input type="text" class="form-control exp-company" data-idx="${idx}" value="${exp.company || ''}">
                </div>
                <div class="form-group">
                    <label>Role</label>
                    <input type="text" class="form-control exp-role" data-idx="${idx}" value="${exp.role || ''}">
                </div>
            </div>
            <div class="form-group" style="margin-top: 0.5rem;">
                <label>Duration</label>
                <input type="text" class="form-control exp-dur" data-idx="${idx}" value="${exp.duration || ''}">
            </div>
            <div class="form-group" style="margin-top: 0.5rem;">
                <label>Responsibilities & Impact</label>
                <textarea class="form-control exp-desc" data-idx="${idx}" rows="2">${exp.description || ''}</textarea>
                <button type="button" class="btn-bullet-improve" onclick="improveExperienceBullet(${idx})">
                    <i class="fa-solid fa-wand-magic-sparkles"></i> IMPROVE BULLET
                </button>
            </div>
        `;
        container.appendChild(item);
    });
}

function updateDataFromForm() {
    resumeData.personal = {
        name: document.getElementById('piName').value,
        email: document.getElementById('piEmail').value,
        phone: document.getElementById('piPhone').value,
        location: document.getElementById('piLocation').value,
        linkedin: document.getElementById('piLinkedin').value,
        github: document.getElementById('piGithub').value
    };

    resumeData.summary = document.getElementById('summaryText').value;

    const prog = document.getElementById('skillsProg').value.split(',').map(s => s.strip ? s.strip() : s.trim()).filter(Boolean);
    const fw = document.getElementById('skillsFw').value.split(',').map(s => s.trim()).filter(Boolean);
    const db = document.getElementById('skillsDb').value.split(',').map(s => s.trim()).filter(Boolean);
    const tools = document.getElementById('skillsTools').value.split(',').map(s => s.trim()).filter(Boolean);

    resumeData.skills = Array.from(new Set([...prog, ...fw, ...db, ...tools]));

    // Read Projects
    document.querySelectorAll('.project-form-item').forEach((item, idx) => {
        if (resumeData.projects[idx]) {
            resumeData.projects[idx].name = item.querySelector('.proj-name').value;
            resumeData.projects[idx].technologies = item.querySelector('.proj-tech').value;
            resumeData.projects[idx].description = item.querySelector('.proj-desc').value;
        }
    });

    // Read Experience
    document.querySelectorAll('.exp-form-item').forEach((item, idx) => {
        if (resumeData.experience[idx]) {
            resumeData.experience[idx].company = item.querySelector('.exp-company').value;
            resumeData.experience[idx].role = item.querySelector('.exp-role').value;
            resumeData.experience[idx].duration = item.querySelector('.exp-dur').value;
            resumeData.experience[idx].description = item.querySelector('.exp-desc').value;
        }
    });

    resumeData.education = {
        degree: document.getElementById('eduDegree').value,
        college: document.getElementById('eduCollege').value,
        year: document.getElementById('eduYear').value,
        cgpa: document.getElementById('eduCgpa').value
    };

    resumeData.certifications = document.getElementById('certificationsText').value;
    resumeData.achievements = document.getElementById('achievementsText').value;

    // Save current draft state to localStorage
    localStorage.setItem('careerforge_resume_data', JSON.stringify(resumeData));
}

function setupFormListeners() {
    const form = document.getElementById('resumeForm');
    if (form) {
        form.addEventListener('input', () => {
            updateDataFromForm();
            renderLivePreview();
            analyzeResumeATS();
        });
    }

    // Accordions
    document.querySelectorAll('.accordion-title').forEach(title => {
        title.addEventListener('click', (e) => {
            if (e.target.closest('.btn-ai-sparkle')) return;
            const accordion = title.parentElement;
            accordion.classList.toggle('active');
        });
    });

    // Add item buttons
    document.getElementById('btnAddProject').addEventListener('click', () => {
        resumeData.projects = resumeData.projects || [];
        resumeData.projects.push({ name: "New Project", technologies: "Python", description: "Project description..." });
        renderProjectsForm();
        updateDataFromForm();
        renderLivePreview();
    });

    document.getElementById('btnAddExperience').addEventListener('click', () => {
        resumeData.experience = resumeData.experience || [];
        resumeData.experience.push({ company: "Company Name", role: "Developer Intern", duration: "2026", description: "Responsibilities..." });
        renderExperienceForm();
        updateDataFromForm();
        renderLivePreview();
    });
}

function setupTemplateSelector() {
    document.querySelectorAll('.tmpl-chip').forEach(chip => {
        chip.addEventListener('click', () => {
            document.querySelectorAll('.tmpl-chip').forEach(c => c.classList.remove('active'));
            chip.classList.add('active');
            currentTemplate = chip.getAttribute('data-tmpl');

            const doc = document.getElementById('resumeDocument');
            if (doc) {
                doc.className = `resume-document template-${currentTemplate}`;
            }
            renderLivePreview();
        });
    });
}

function setupActionButtons() {
    // Generate AI Summary
    document.getElementById('btnGenSummary').addEventListener('click', () => {
        updateDataFromForm();
        fetch('/api/resume-builder/generate-summary', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(resumeData)
        })
        .then(res => res.json())
        .then(data => {
            if (data.success && data.data && data.data.summary) {
                document.getElementById('summaryText').value = data.data.summary;
                updateDataFromForm();
                renderLivePreview();
                analyzeResumeATS();
            }
        });
    });

    // Optimize Resume Button
    document.getElementById('btnOptimizeResume').addEventListener('click', openOptimizationModal);
    document.getElementById('btnCloseOptModal').addEventListener('click', closeOptModal);
    document.getElementById('btnCancelOpt').addEventListener('click', closeOptModal);

    // Save Version
    document.getElementById('btnSaveVersion').addEventListener('click', () => {
        updateDataFromForm();
        let versions = JSON.parse(localStorage.getItem('careerforge_resume_versions') || '[]');
        const vName = prompt("Enter a name for this resume version:", `${resumeData.target_role} - ${new Date().toLocaleDateString()}`);
        if (vName) {
            versions.unshift({
                name: vName,
                timestamp: new Date().toISOString(),
                data: JSON.parse(JSON.stringify(resumeData))
            });
            localStorage.setItem('careerforge_resume_versions', JSON.stringify(versions));
            loadSavedVersionsList();
            alert(`Saved "${vName}" to Version History!`);
        }
    });

    // Restore Version
    document.getElementById('btnRestoreVersion').addEventListener('click', () => {
        const select = document.getElementById('versionSelect');
        const val = select.value;
        if (val === 'current') return;

        let versions = JSON.parse(localStorage.getItem('careerforge_resume_versions') || '[]');
        const target = versions[parseInt(val)];
        if (target && target.data) {
            resumeData = target.data;
            populateFormFromData();
            renderLivePreview();
            analyzeResumeATS();
            alert(`Restored "${target.name}"!`);
        }
    });

    // Print & Download PDF
    document.getElementById('btnPrintPdf').addEventListener('click', () => window.print());
    document.getElementById('btnDownloadPdf').addEventListener('click', () => window.print());
}

function renderLivePreview() {
    const doc = document.getElementById('resumeDocument');
    if (!doc) return;

    const p = resumeData.personal || {};
    const ed = resumeData.education || {};
    const s = resumeData.skills || [];

    const contactParts = [p.email, p.phone, p.location, p.linkedin, p.github].filter(Boolean);
    const contactHtml = contactParts.map(c => `<span>${c}</span>`).join(' • ');

    // Skills breakdown
    const skillsHtml = s.length > 0
        ? `<div class="rd-section">
            <div class="rd-section-title">Technical Skills</div>
            <div class="rd-summary">${s.join(' • ')}</div>
           </div>`
        : '';

    // Projects
    let projectsHtml = '';
    if (resumeData.projects && resumeData.projects.length > 0) {
        const items = resumeData.projects.map(proj => `
            <div class="rd-item">
                <div class="rd-item-header">
                    <span>${proj.name}</span>
                    <span style="font-weight: 400; color: #64748b;">${proj.technologies || ''}</span>
                </div>
                <div class="rd-summary">${proj.description}</div>
            </div>
        `).join('');
        projectsHtml = `<div class="rd-section"><div class="rd-section-title">Projects</div>${items}</div>`;
    }

    // Experience
    let expHtml = '';
    if (resumeData.experience && resumeData.experience.length > 0) {
        const items = resumeData.experience.map(exp => `
            <div class="rd-item">
                <div class="rd-item-header">
                    <span>${exp.role} — ${exp.company}</span>
                    <span style="font-weight: 400; color: #64748b;">${exp.duration}</span>
                </div>
                <div class="rd-summary">${exp.description}</div>
            </div>
        `).join('');
        expHtml = `<div class="rd-section"><div class="rd-section-title">Experience</div>${items}</div>`;
    }

    // Education
    let eduHtml = '';
    if (ed.degree || ed.college) {
        eduHtml = `
            <div class="rd-section">
                <div class="rd-section-title">Education</div>
                <div class="rd-item">
                    <div class="rd-item-header">
                        <span>${ed.degree || ''} — ${ed.college || ''}</span>
                        <span style="font-weight: 400; color: #64748b;">${ed.year || ''}</span>
                    </div>
                    <div class="rd-item-sub">CGPA / Marks: ${ed.cgpa || '8.5 / 10'}</div>
                </div>
            </div>
        `;
    }

    // Certifications & Achievements
    let certHtml = resumeData.certifications
        ? `<div class="rd-section"><div class="rd-section-title">Certifications</div><div class="rd-summary">${resumeData.certifications}</div></div>`
        : '';

    let achHtml = resumeData.achievements
        ? `<div class="rd-section"><div class="rd-section-title">Key Achievements</div><div class="rd-summary">${resumeData.achievements}</div></div>`
        : '';

    doc.innerHTML = `
        <div class="rd-header">
            <h1 class="rd-name">${p.name || 'Candidate Name'}</h1>
            <div class="rd-contact-row">${contactHtml}</div>
        </div>
        ${resumeData.summary ? `<div class="rd-section"><div class="rd-section-title">Professional Summary</div><div class="rd-summary">${resumeData.summary}</div></div>` : ''}
        ${skillsHtml}
        ${projectsHtml}
        ${expHtml}
        ${eduHtml}
        ${certHtml}
        ${achHtml}
    `;
}

function analyzeResumeATS() {
    const payload = {
        ...resumeData,
        job_id: activeJobContext ? activeJobContext.job_id : null
    };

    fetch('/api/resume-builder/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    })
    .then(res => res.json())
    .then(data => {
        if (data.success && data.data) {
            const res = data.data;
            document.getElementById('rbAtsScore').textContent = `${res.ats_score}%`;
            if (res.job_match_score) {
                document.getElementById('rbJobMatch').textContent = `${res.job_match_score}%`;
            }

            // Matched & Missing Keywords
            const mTags = document.getElementById('matchedKeywordsTags');
            if (mTags) {
                mTags.innerHTML = (res.matched_keywords || []).map(k => `<span class="kw-tag match">✓ ${k}</span>`).join('') || '<span class="text-muted">None</span>';
            }

            const missTags = document.getElementById('missingKeywordsTags');
            if (missTags) {
                missTags.innerHTML = (res.missing_keywords || []).map(k => `<span class="kw-tag missing">⚠ ${k}</span>`).join('') || '<span class="kw-tag match">✓ All core keywords covered!</span>';
            }

            // Insights
            const insightsList = document.getElementById('resumeInsightsList');
            if (insightsList) {
                insightsList.innerHTML = '';
                (res.strengths || []).forEach(s => {
                    const d = document.createElement('div');
                    d.innerHTML = `🟢 ${s}`;
                    insightsList.appendChild(d);
                });
                (res.missing_elements || []).forEach(m => {
                    const d = document.createElement('div');
                    d.innerHTML = `🟡 ${m}`;
                    insightsList.appendChild(d);
                });
            }
        }
    });
}

function openOptimizationModal() {
    const payload = {
        ...resumeData,
        job_id: activeJobContext ? activeJobContext.job_id : null
    };

    fetch('/api/resume-builder/optimize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    })
    .then(res => res.json())
    .then(data => {
        if (data.success && data.data) {
            const body = document.getElementById('optModalBody');
            body.innerHTML = '';

            const sugs = data.data.suggestions || [];
            if (sugs.length === 0) {
                body.innerHTML = '<p style="color:#4ade80;">✓ Your resume is already highly optimized for this target role!</p>';
            } else {
                sugs.forEach(s => {
                    const box = document.createElement('div');
                    box.style.background = 'rgba(15,23,42,0.6)';
                    box.style.padding = '1rem';
                    box.style.borderRadius = '8px';
                    box.style.marginBottom = '1rem';
                    box.innerHTML = `
                        <h4 style="color:#c084fc; margin:0 0 0.5rem 0;">${s.field} Optimization</h4>
                        <div style="font-size:0.85rem; margin-bottom:0.4rem;"><strong>BEFORE:</strong> ${s.before}</div>
                        <div style="font-size:0.85rem; color:#4ade80; margin-bottom:0.4rem;"><strong>AFTER:</strong> ${s.after}</div>
                        <div style="font-size:0.75rem; color:var(--text-muted);">${s.reason}</div>
                    `;
                    body.appendChild(box);
                });
            }
            document.getElementById('optModalBackdrop').style.display = 'flex';
        }
    });
}

function closeOptModal() {
    document.getElementById('optModalBackdrop').style.display = 'none';
}

function improveProjectBullet(idx) {
    if (!resumeData.projects[idx]) return;
    const bullet = resumeData.projects[idx].description;

    fetch('/api/resume-builder/improve-bullet', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ bullet: bullet, context: resumeData.target_role })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success && data.data && data.data.improved) {
            resumeData.projects[idx].description = data.data.improved;
            renderProjectsForm();
            updateDataFromForm();
            renderLivePreview();
            alert(`Improved Bullet Point:\n\n"${data.data.improved}"\n\n${data.data.disclaimer}`);
        }
    });
}

function improveExperienceBullet(idx) {
    if (!resumeData.experience[idx]) return;
    const bullet = resumeData.experience[idx].description;

    fetch('/api/resume-builder/improve-bullet', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ bullet: bullet, context: resumeData.target_role })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success && data.data && data.data.improved) {
            resumeData.experience[idx].description = data.data.improved;
            renderExperienceForm();
            updateDataFromForm();
            renderLivePreview();
            alert(`Improved Bullet Point:\n\n"${data.data.improved}"\n\n${data.data.disclaimer}`);
        }
    });
}

function loadSavedVersionsList() {
    const select = document.getElementById('versionSelect');
    if (!select) return;

    let versions = JSON.parse(localStorage.getItem('careerforge_resume_versions') || '[]');
    select.innerHTML = '<option value="current">Current Draft</option>';
    versions.forEach((v, idx) => {
        const opt = document.createElement('option');
        opt.value = idx;
        opt.textContent = v.name;
        select.appendChild(opt);
    });
}
