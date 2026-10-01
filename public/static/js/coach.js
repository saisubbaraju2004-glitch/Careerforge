window.CoachHandler = {
    sendPrompt: async function(promptText) {
        const chatWindow = document.getElementById('coachChatWindow');
        const inputEl = document.getElementById('coachQueryInput');

        if (!promptText && inputEl) {
            promptText = inputEl.value.trim();
        }

        if (!promptText) return;

        if (inputEl) inputEl.value = '';

        // Render User Bubble
        if (chatWindow) {
            const uBubble = document.createElement('div');
            uBubble.className = 'chat-bubble user';
            uBubble.innerText = promptText;
            chatWindow.appendChild(uBubble);

            // Render Thinking Indicator
            const aiBubble = document.createElement('div');
            aiBubble.className = 'chat-bubble ai';
            aiBubble.innerHTML = `<i class="fa-solid fa-circle-notch fa-spin"></i> AI Coach is formulating advice...`;
            chatWindow.appendChild(aiBubble);
            chatWindow.scrollTop = chatWindow.scrollHeight;

            try {
                const profile = JSON.parse(localStorage.getItem('careerforge_profile') || '{}');
                const targetRole = profile.targetRole || 'Python Backend Developer';
                const currentSkills = profile.skills || ['Python', 'Flask', 'SQL'];

                const res = await fetch('/api/career-coach', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        prompt: promptText,
                        target_role: targetRole,
                        current_skills: currentSkills,
                        missing_skills: ['REST APIs', 'Docker', 'Testing'],
                        readiness_score: 72,
                        ats_score: 83,
                        interview_score: 78
                    })
                });

                const data = await res.json();
                if (data.success && data.data && data.data.reply) {
                    aiBubble.textContent = data.data.reply;
                } else {
                    aiBubble.textContent = "Focus on closing your primary missing skills and completing your daily capstone tasks.";
                }
            } catch (e) {
                aiBubble.textContent = "Focus on your immediate 30-Day Plan targets and practice in the AI Interview Simulator.";
            }

            chatWindow.scrollTop = chatWindow.scrollHeight;
        }
    }
};

document.addEventListener('DOMContentLoaded', () => {
    const coachForm = document.getElementById('coachInputForm');
    if (coachForm) {
        coachForm.addEventListener('submit', (e) => {
            e.preventDefault();
            window.CoachHandler.sendPrompt();
        });
    }
});
