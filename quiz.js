/**
 * E-Learning Platform with Quizzes - Quiz Runner
 * Features:
 * - Timed Countdown with auto-submit
 * - Question palette navigation & progress indicator
 * - Confirmation modal before final submission
 * - Instant evaluation with zero answer leakage during test
 */

document.addEventListener('DOMContentLoaded', () => {
    initQuizRunner();
});

function initQuizRunner() {
    const quizForm = document.getElementById('quizForm');
    if (!quizForm) return;

    const cards = document.querySelectorAll('.question-card');
    const paletteBtns = document.querySelectorAll('.palette-btn');
    const prevBtn = document.getElementById('prevQuestionBtn');
    const nextBtn = document.getElementById('nextQuestionBtn');
    const submitBtn = document.getElementById('submitQuizBtn');
    const timerDisplay = document.getElementById('quizTimer');
    const timeTakenInput = document.getElementById('timeTakenInput');

    let currentIndex = 0;
    const totalQuestions = cards.length;
    let secondsSpent = 0;

    // Timer logic
    const timeLimitMinutes = parseInt(timerDisplay?.dataset.timeLimit || '15', 10);
    let remainingSeconds = timeLimitMinutes * 60;

    const timerInterval = setInterval(() => {
        remainingSeconds--;
        secondsSpent++;
        if (timeTakenInput) timeTakenInput.value = secondsSpent;

        if (timerDisplay) {
            const mins = Math.floor(remainingSeconds / 60);
            const secs = remainingSeconds % 60;
            timerDisplay.textContent = `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;

            if (remainingSeconds <= 120) {
                timerDisplay.parentElement.classList.add('timer-urgent');
            }

            if (remainingSeconds <= 0) {
                clearInterval(timerInterval);
                alert("Time has expired! Submitting your quiz now.");
                quizForm.submit();
            }
        }
    }, 1000);

    function showQuestion(index) {
        if (index < 0 || index >= totalQuestions) return;

        cards.forEach((card, idx) => {
            card.classList.toggle('active', idx === index);
        });

        paletteBtns.forEach((btn, idx) => {
            btn.classList.toggle('current', idx === index);
        });

        currentIndex = index;

        // Button states
        if (prevBtn) prevBtn.disabled = (currentIndex === 0);
        if (nextBtn) {
            if (currentIndex === totalQuestions - 1) {
                nextBtn.style.display = 'none';
                if (submitBtn) submitBtn.style.display = 'inline-flex';
            } else {
                nextBtn.style.display = 'inline-flex';
            }
        }
    }

    // Palette button clicks
    paletteBtns.forEach((btn, idx) => {
        btn.addEventListener('click', () => {
            showQuestion(idx);
        });
    });

    // Next / Prev button clicks
    if (prevBtn) {
        prevBtn.addEventListener('click', () => {
            if (currentIndex > 0) showQuestion(currentIndex - 1);
        });
    }

    if (nextBtn) {
        nextBtn.addEventListener('click', () => {
            if (currentIndex < totalQuestions - 1) showQuestion(currentIndex + 1);
        });
    }

    // Option selection handling & palette marking
    const optionLabels = document.querySelectorAll('.option-label');
    optionLabels.forEach(label => {
        label.addEventListener('click', () => {
            const radio = label.querySelector('input[type="radio"]');
            if (radio) {
                radio.checked = true;
                
                // Clear sibling selected states
                const parentList = label.closest('.options-list');
                parentList.querySelectorAll('.option-label').forEach(l => l.classList.remove('selected'));
                label.classList.add('selected');

                // Mark current question in palette
                if (paletteBtns[currentIndex]) {
                    paletteBtns[currentIndex].classList.add('answered');
                }
                updateAnsweredCounter();
            }
        });
    });

    function updateAnsweredCounter() {
        const checkedCount = document.querySelectorAll('input[type="radio"]:checked').length;
        const countDisplay = document.getElementById('answeredCountDisplay');
        if (countDisplay) {
            countDisplay.textContent = `${checkedCount} of ${totalQuestions} answered`;
        }
    }

    // Submit confirmation
    if (submitBtn) {
        submitBtn.addEventListener('click', (e) => {
            e.preventDefault();
            const answeredCount = document.querySelectorAll('input[type="radio"]:checked').length;
            const unanswered = totalQuestions - answeredCount;

            let confirmMsg = `Are you sure you want to finish and submit your quiz?\n\n- Answered: ${answeredCount}\n`;
            if (unanswered > 0) {
                confirmMsg += `- Unanswered: ${unanswered} question(s)\n\nUnanswered questions will be scored as incorrect.`;
            } else {
                confirmMsg += `All ${totalQuestions} questions completed!`;
            }

            if (confirm(confirmMsg)) {
                clearInterval(timerInterval);
                if (timeTakenInput) timeTakenInput.value = secondsSpent;
                quizForm.submit();
            }
        });
    }

    // Initialize first question
    showQuestion(0);
    updateAnsweredCounter();
}
