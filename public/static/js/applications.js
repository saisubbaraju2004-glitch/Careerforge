document.addEventListener('DOMContentLoaded', () => {
    let applications = [];

    function getApps() {
        return applications;
    }

    async function saveApps(apps) {
        const response = await fetch('/api/applications', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ applications: apps })
        });
        const result = await response.json();
        if (!response.ok || result.success !== true) {
            throw new Error(result.error || 'Applications could not be saved.');
        }
        applications = result.data;
    }

    function renderPipeline() {
        const apps = getApps();

        const statuses = ['Wishlist', 'Applied', 'Assessment', 'Interview', 'Offer', 'Rejected'];
        const counts = { Wishlist: 0, Applied: 0, Assessment: 0, Interview: 0, Offer: 0, Rejected: 0 };

        statuses.forEach(st => {
            const container = document.getElementById(`list${st}`);
            if (container) container.innerHTML = '';
        });

        apps.forEach(app => {
            const st = app.status || 'Applied';
            counts[st] = (counts[st] || 0) + 1;

            const container = document.getElementById(`list${st}`);
            if (container) {
                const card = document.createElement('div');
                card.className = 'app-item-card';
                const company = document.createElement('div');
                company.className = 'app-company';
                company.textContent = app.company;
                const role = document.createElement('div');
                role.className = 'app-role';
                role.textContent = app.role;
                const date = document.createElement('div');
                date.className = 'app-date';
                date.textContent = app.date || '';
                const actions = document.createElement('div');
                actions.className = 'app-actions-row';
                if (app.url) {
                    const link = document.createElement('a');
                    link.href = app.url;
                    link.target = '_blank';
                    link.rel = 'noopener noreferrer';
                    link.textContent = 'Job Link';
                    actions.appendChild(link);
                }
                const buttons = document.createElement('div');
                buttons.style.display = 'flex';
                buttons.style.gap = '0.4rem';
                const edit = document.createElement('button');
                edit.type = 'button';
                edit.className = 'btn btn-sm btn-secondary';
                edit.textContent = 'Edit';
                edit.addEventListener('click', () => window.AppTracker.editApp(app.id));
                const remove = document.createElement('button');
                remove.type = 'button';
                remove.className = 'btn btn-sm btn-secondary';
                remove.textContent = 'Delete';
                remove.addEventListener('click', () => window.AppTracker.deleteApp(app.id));
                buttons.append(edit, remove);
                actions.appendChild(buttons);
                card.append(company, role, date, actions);
                container.appendChild(card);
            }
        });

        // Update counts
        document.getElementById('cntTotal').innerText = apps.length;
        document.getElementById('cntApplied').innerText = counts.Applied;
        document.getElementById('cntInterview').innerText = counts.Interview;
        document.getElementById('cntOffer').innerText = counts.Offer;
        document.getElementById('cntRejected').innerText = counts.Rejected;

        statuses.forEach(st => {
            const b = document.getElementById(`badge${st}`);
            if (b) b.innerText = counts[st] || 0;
        });
    }

    window.AppTracker = {
        editApp: function(id) {
            const apps = getApps();
            const app = apps.find(a => a.id === id);
            if (!app) return;

            document.getElementById('appIdInput').value = app.id;
            document.getElementById('appCompanyInput').value = app.company;
            document.getElementById('appRoleInput').value = app.role;
            document.getElementById('appStatusInput').value = app.status;
            document.getElementById('appDateInput').value = app.date;
            document.getElementById('appUrlInput').value = app.url || '';

            document.getElementById('appModalTitle').innerHTML = `<i class="fa-solid fa-pen text-cyan"></i> Edit Job Application`;
            document.getElementById('appModal').classList.remove('hidden');
        },

        deleteApp: async function(id) {
            if (!confirm('Are you sure you want to delete this application?')) return;
            try {
                const response = await fetch(`/api/applications/${encodeURIComponent(id)}`, { method: 'DELETE' });
                const result = await response.json();
                if (!response.ok || result.success !== true) throw new Error(result.error || 'Application could not be deleted.');
                applications = applications.filter(a => a.id !== id);
                renderPipeline();
            } catch (error) {
                alert(error.message);
            }
        }
    };

    // Modal controls
    const appModal = document.getElementById('appModal');
    const openAddAppModalBtn = document.getElementById('openAddAppModalBtn');
    const closeAppModalBtn = document.getElementById('closeAppModalBtn');
    const cancelAppModalBtn = document.getElementById('cancelAppModalBtn');
    const appForm = document.getElementById('appForm');

    if (openAddAppModalBtn) {
        openAddAppModalBtn.addEventListener('click', () => {
            document.getElementById('appIdInput').value = '';
            appForm.reset();
            document.getElementById('appDateInput').value = new Date().toISOString().split('T')[0];
            document.getElementById('appModalTitle').innerHTML = `<i class="fa-solid fa-briefcase text-cyan"></i> Add New Job Application`;
            appModal.classList.remove('hidden');
        });
    }

    if (closeAppModalBtn) closeAppModalBtn.addEventListener('click', () => appModal.classList.add('hidden'));
    if (cancelAppModalBtn) cancelAppModalBtn.addEventListener('click', () => appModal.classList.add('hidden'));

    if (appForm) {
        appForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const id = document.getElementById('appIdInput').value || String(Date.now());
            const company = document.getElementById('appCompanyInput').value.trim();
            const role = document.getElementById('appRoleInput').value.trim();
            const status = document.getElementById('appStatusInput').value;
            const date = document.getElementById('appDateInput').value;
            const url = document.getElementById('appUrlInput').value.trim();

            let apps = [...getApps()];
            const idx = apps.findIndex(a => a.id === id);
            if (idx >= 0) {
                apps[idx] = { id, company, role, status, date, url };
            } else {
                apps.unshift({ id, company, role, status, date, url });
            }

            try {
                await saveApps(apps);
                appModal.classList.add('hidden');
                renderPipeline();
            } catch (error) {
                alert(error.message);
            }
        });
    }

    fetch('/api/applications')
        .then(response => response.json().then(data => {
            if (!response.ok || data.success !== true || !Array.isArray(data.data)) {
                throw new Error(data.error || 'Applications could not be loaded.');
            }
            applications = data.data;
            renderPipeline();
        }))
        .catch(error => {
            console.error('Application load error:', error);
            alert(error.message);
        });
});
