window.CareerFormHandler = {
    skills: ["Python", "Flask", "HTML", "CSS", "JavaScript", "SQL"],

    init: function() {
        this.renderSkills();
        this.bindEvents();
    },

    bindEvents: function() {
        const skillInput = document.getElementById('skillInput');
        if (skillInput) {
            skillInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    const val = skillInput.value.trim();
                    if (val && !this.skills.includes(val)) {
                        this.skills.push(val);
                        this.renderSkills();
                        skillInput.value = '';
                    }
                }
            });
        }

        const roleSelect = document.getElementById('targetRole');
        if (roleSelect) {
            roleSelect.addEventListener('change', (e) => {
                this.updateSuggestedSkills(e.target.value);
            });
        }

        const fileInput = document.getElementById('resumeFile');
        const fileNameDisplay = document.getElementById('fileNameDisplay');
        const uploadWrapper = document.querySelector('.file-upload-wrapper');

        if (fileInput && fileNameDisplay) {
            fileInput.addEventListener('change', (e) => {
                if (e.target.files.length > 0) {
                    const icon = document.createElement('i');
                    icon.className = 'fa-solid fa-file-circle-check';
                    icon.style.color = 'var(--success)';
                    fileNameDisplay.replaceChildren(icon, document.createTextNode(` ${e.target.files[0].name}`));
                    fileNameDisplay.style.color = 'var(--text-main)';
                }
            });
        }

        if (uploadWrapper) {
            ['dragenter', 'dragover'].forEach(eventName => {
                uploadWrapper.addEventListener(eventName, (e) => {
                    e.preventDefault();
                    uploadWrapper.style.borderColor = 'var(--secondary)';
                    uploadWrapper.style.background = 'rgba(6, 182, 212, 0.1)';
                }, false);
            });

            ['dragleave', 'drop'].forEach(eventName => {
                uploadWrapper.addEventListener(eventName, (e) => {
                    e.preventDefault();
                    uploadWrapper.style.borderColor = '';
                    uploadWrapper.style.background = '';
                }, false);
            });
        }
    },


    renderSkills: function() {
        const container = document.getElementById('skillsTagContainer');
        if (!container) return;

        container.innerHTML = this.skills.map(s => `
            <span class="skill-tag" onclick="window.CareerFormHandler.removeSkill('${s}')">
                ${s} <i class="fa-solid fa-xmark"></i>
            </span>
        `).join('');
    },

    removeSkill: function(skillName) {
        this.skills = this.skills.filter(s => s !== skillName);
        this.renderSkills();
    },

    addSuggestedSkill: function(skillName) {
        if (!this.skills.includes(skillName)) {
            this.skills.push(skillName);
            this.renderSkills();
        }
    },

    updateSuggestedSkills: function(roleId) {
        const suggestionsMap = {
            python_backend_developer: ["REST APIs", "PostgreSQL", "Docker", "Git", "Testing"],
            frontend_developer: ["React", "Tailwind CSS", "TypeScript", "REST APIs", "Git"],
            fullstack_developer: ["Node.js", "React", "Docker", "PostgreSQL", "Git"],
            ai_engineer: ["NumPy", "Pandas", "PyTorch", "LLM APIs", "Scikit-Learn"]
        };

        const suggs = suggestionsMap[roleId] || ["Git", "REST APIs", "Docker"];
        const container = document.getElementById('suggestedSkills');
        if (container) {
            container.innerHTML = suggs.map(s => `
                <span class="sugg-pill" onclick="window.CareerFormHandler.addSuggestedSkill('${s}')">
                    + ${s}
                </span>
            `).join('');
        }
    },

    animateLoaderSteps: function(callback) {
        const steps = [
            { id: 'step1', delay: 400 },
            { id: 'step2', delay: 900 },
            { id: 'step3', delay: 1400 },
            { id: 'step4', delay: 1900 },
            { id: 'step5', delay: 2400 }
        ];

        steps.forEach((s) => {
            setTimeout(() => {
                const el = document.getElementById(s.id);
                if (el) {
                    el.classList.add('completed');
                    el.innerHTML = `<i class="fa-solid fa-circle-check text-success"></i> Completed step`;
                }
            }, s.delay);
        });

        setTimeout(() => {
            if (callback) callback();
        }, 2800);
    }
};
