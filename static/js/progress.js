document.addEventListener('DOMContentLoaded', () => {
    function loadProgressMetrics() {
        const profile = JSON.parse(localStorage.getItem('careerforge_profile') || '{}');
        const intHist = JSON.parse(localStorage.getItem('careerforge_interview_history') || '[]');
        const apps = JSON.parse(localStorage.getItem('careerforge_applications') || '[]');
        
        const readiness = profile.readinessScore || 72;
        const ats = profile.atsScore || 83;
        const latestInt = intHist.length > 0 ? intHist[intHist.length - 1].score : 78;

        document.getElementById('progReadiness').innerText = `${readiness}%`;
        document.getElementById('progInterview').innerText = `${latestInt}%`;
        document.getElementById('progATS').innerText = `${ats}%`;
        
        const sessionsEl = document.getElementById('progSessions');
        if (sessionsEl) sessionsEl.innerText = `${intHist.length || 3} Sessions Completed`;

        const planDay = profile.planDay || 12;
        document.getElementById('progPlanDay').innerText = `Day ${planDay}`;

        // Populate conversion funnel
        const totalApps = apps.length;
        const responses = apps.filter(a => a.status && a.status !== 'Applied').length;
        const interviews = apps.filter(a => ['Interview Scheduled', 'Interview Completed', 'Offer Received'].includes(a.status)).length;
        const offers = apps.filter(a => a.status === 'Offer Received').length;

        const funnelApps = document.getElementById('funnelApps');
        const funnelResponses = document.getElementById('funnelResponses');
        const funnelInterviews = document.getElementById('funnelInterviews');
        const funnelOffers = document.getElementById('funnelOffers');

        if (funnelApps) funnelApps.innerText = totalApps;
        if (funnelResponses) funnelResponses.innerText = responses;
        if (funnelInterviews) funnelInterviews.innerText = interviews;
        if (funnelOffers) funnelOffers.innerText = offers;
    }

    loadProgressMetrics();
});
