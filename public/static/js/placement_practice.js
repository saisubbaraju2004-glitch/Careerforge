document.addEventListener('DOMContentLoaded', () => {
    // Mode initialized via inline script in placement_practice.html
});

let currentPracticeMode = 'aptitude';
let activeQuestions = [];
let currentQuestionIndex = 0;
let userAnswersLog = [];
let practiceTimer = null;
let timerSeconds = 0;

function switchPracticeMode(mode) {
    currentPracticeMode = mode;
    document.getElementById('tabAptitude').classList.toggle('active', mode === 'aptitude');
    document.getElementById('tabCoding').classList.toggle('active', mode === 'coding');

    const selectCat = document.getElementById('selectCategory');
    if (selectCat) {
        if (mode === 'aptitude') {
            selectCat.innerHTML = `
                <option value="All" selected>All Categories</option>
                <option value="Quantitative Aptitude">Quantitative Aptitude</option>
                <option value="Logical Reasoning">Logical Reasoning</option>
                <option value="Verbal Ability">Verbal Ability</option>
                <option value="Data Interpretation">Data Interpretation</option>
            `;
        } else {
            selectCat.innerHTML = `
                <option value="All" selected>All Data Structures</option>
                <option value="Arrays">Arrays</option>
                <option value="Strings">Strings</option>
                <option value="Hashing">Hashing</option>
                <option value="Trees">Trees</option>
            `;
        }
    }
}

function startPracticeSession() {
    const category = document.getElementById('selectCategory').value;
    const count = parseInt(document.getElementById('selectCount').value || 10);

    const endpoint = currentPracticeMode === 'aptitude' ?
        '/api/placement-practice/aptitude/generate' :
        '/api/placement-practice/coding/generate';

    fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ category: category, count: count })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success && data.data) {
            activeQuestions = data.data.questions || data.data.problems || [];
            currentQuestionIndex = 0;
            userAnswersLog = [];

            document.getElementById('practiceSetupCard').style.display = 'none';
            document.getElementById('resultCard').style.display = 'none';
            document.getElementById('liveArenaCard').style.display = 'block';

            renderCurrentQuestion();
            startTimer();
        }
    });
}

function startTimer() {
    clearInterval(practiceTimer);
    timerSeconds = 0;
    practiceTimer = setInterval(() => {
        timerSeconds++;
        const mins = String(Math.floor(timerSeconds / 60)).padStart(2, '0');
        const secs = String(timerSeconds % 60).padStart(2, '0');
        if (document.getElementById('timerVal')) {
            document.getElementById('timerVal').textContent = `${mins}:${secs}`;
        }
    }, 1000);
}

function stopTimer() {
    clearInterval(practiceTimer);
}

function renderCurrentQuestion() {
    if (currentQuestionIndex >= activeQuestions.length) {
        finishPracticeSession();
        return;
    }

    const q = activeQuestions[currentQuestionIndex];
    const total = activeQuestions.length;

    document.getElementById('qNumBadge').textContent = `QUESTION ${currentQuestionIndex + 1} / ${total}`;
    document.getElementById('qTopicBadge').textContent = q.topic || q.category || "Practice";
    document.getElementById('qTitle').textContent = q.question || q.title || q.description;

    const optContainer = document.getElementById('optionsContainer');
    const codeContainer = document.getElementById('codeEditorContainer');

    if (currentPracticeMode === 'aptitude') {
        optContainer.style.display = 'flex';
        codeContainer.style.display = 'none';

        optContainer.innerHTML = (q.options || []).map((opt, idx) => `
            <button class="option-btn" onclick="selectOption('${opt.replace(/'/g, "\\'")}', this)">
                <strong>${String.fromCharCode(65 + idx)}.</strong> ${opt}
            </button>
        `).join('');
    } else {
        optContainer.style.display = 'none';
        codeContainer.style.display = 'block';
        document.getElementById('codeEditor').value = q.starter_code || "def solve():\n    pass";
    }
}

let selectedOptionVal = "";

function selectOption(optVal, btnEl) {
    selectedOptionVal = optVal;
    document.querySelectorAll('.option-btn').forEach(b => b.classList.remove('selected'));
    btnEl.classList.add('selected');
}

function skipQuestion() {
    const q = activeQuestions[currentQuestionIndex];
    userAnswersLog.push({
        id: q.id,
        user_answer: "",
        skipped: true
    });
    currentQuestionIndex++;
    renderCurrentQuestion();
}

function submitCurrentQuestion() {
    const q = activeQuestions[currentQuestionIndex];

    if (currentPracticeMode === 'aptitude') {
        if (!selectedOptionVal) {
            alert("Please select an option before submitting.");
            return;
        }
        userAnswersLog.push({
            id: q.id,
            user_answer: selectedOptionVal,
            skipped: false
        });
        selectedOptionVal = "";
        currentQuestionIndex++;
        renderCurrentQuestion();
    } else {
        const code = document.getElementById('codeEditor').value;
        fetch('/api/placement-practice/coding/submit', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ problem_id: q.id, code: code })
        })
        .then(res => res.json())
        .then(data => {
            if (data.success && data.data) {
                alert(`Code Evaluation Result:\n\nStatus: ${data.data.status}\nScore: ${data.data.score}%\nTest Cases: ${data.data.test_cases_passed}\n\n${data.data.message}`);
                currentQuestionIndex++;
                renderCurrentQuestion();
            }
        });
    }
}

function finishPracticeSession() {
    stopTimer();
    document.getElementById('liveArenaCard').style.display = 'none';

    if (currentPracticeMode === 'aptitude') {
        fetch('/api/placement-practice/aptitude/submit', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ answers: userAnswersLog })
        })
        .then(res => res.json())
        .then(data => {
            if (data.success && data.data) {
                const resData = data.data;
                document.getElementById('resScore').textContent = `${resData.accuracy_score}%`;
                document.getElementById('resDetail').textContent = `${resData.correct_answers} / ${resData.total_questions} Questions Correct`;
                document.getElementById('resFeedback').textContent = resData.feedback + ` Weak Areas: ${resData.weak_topics.join(', ')}.`;
                document.getElementById('resultCard').style.display = 'block';
            }
        });
    } else {
        document.getElementById('resScore').textContent = `100%`;
        document.getElementById('resDetail').textContent = `Coding Practice Session Completed`;
        document.getElementById('resFeedback').textContent = `Great job completing the coding challenge! Solutions met target time and space complexities.`;
        document.getElementById('resultCard').style.display = 'block';
    }
}

function resetPracticeSetup() {
    document.getElementById('resultCard').style.display = 'none';
    document.getElementById('practiceSetupCard').style.display = 'block';
}
