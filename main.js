/**
 * E-Learning Platform with Quizzes - Main JavaScript
 * Handles Theme Toggling, Mobile Menu, Live Search, Bookmarks, and Notes.
 */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Theme Management (Dark / Light)
    initTheme();

    // 2. Live Search
    initLiveSearch();

    // 3. Mobile Navigation Toggle
    initMobileNav();

    // 4. Lesson Interactivity (Completion, Bookmarking, Notes)
    initLessonInteractions();
});

function initTheme() {
    const themeToggleBtn = document.getElementById('themeToggleBtn');
    const savedTheme = localStorage.getItem('elearning_theme') || 'light';
    
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);

    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', () => {
            const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
            const newTheme = currentTheme === 'light' ? 'dark' : 'light';
            
            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('elearning_theme', newTheme);
            updateThemeIcon(newTheme);
        });
    }
}

function updateThemeIcon(theme) {
    const icon = document.getElementById('themeIcon');
    if (icon) {
        if (theme === 'dark') {
            icon.innerHTML = '☀️';
            icon.setAttribute('title', 'Switch to Light Mode');
        } else {
            icon.innerHTML = '🌙';
            icon.setAttribute('title', 'Switch to Dark Mode');
        }
    }
}

function initLiveSearch() {
    const searchInput = document.getElementById('navSearchInput');
    const searchDropdown = document.getElementById('searchResultsDropdown');

    if (!searchInput || !searchDropdown) return;

    let debounceTimer;

    searchInput.addEventListener('input', (e) => {
        clearTimeout(debounceTimer);
        const query = e.target.value.trim();

        if (query.length < 2) {
            searchDropdown.classList.remove('show');
            searchDropdown.innerHTML = '';
            return;
        }

        debounceTimer = setTimeout(() => {
            fetch(`/api/search?q=${encodeURIComponent(query)}`)
                .then(res => res.json())
                .then(data => {
                    renderSearchResults(data, searchDropdown);
                })
                .catch(err => console.error("Search fetch error:", err));
        }, 250);
    });

    // Close dropdown on click outside
    document.addEventListener('click', (e) => {
        if (!searchInput.contains(e.target) && !searchDropdown.contains(e.target)) {
            searchDropdown.classList.remove('show');
        }
    });
}

function renderSearchResults(data, container) {
    const { courses, lessons } = data;

    if ((!courses || courses.length === 0) && (!lessons || lessons.length === 0)) {
        container.innerHTML = `
            <div style="padding: 16px; text-align: center; color: var(--text-muted); font-size: 0.9rem;">
                No matches found. Try searching for Python, Java, SQL, or Loops.
            </div>
        `;
        container.classList.add('show');
        return;
    }

    let html = '';

    if (courses && courses.length > 0) {
        html += `<div class="search-result-group-title">Courses</div>`;
        courses.forEach(c => {
            html += `
                <a href="/courses/${c.slug}" class="search-result-item">
                    <strong>${escapeHtml(c.title)}</strong>
                    <div style="font-size: 0.8rem; color: var(--text-muted);">${escapeHtml(c.short_desc || '')}</div>
                </a>
            `;
        });
    }

    if (lessons && lessons.length > 0) {
        html += `<div class="search-result-group-title">Lessons & Topics</div>`;
        lessons.forEach(l => {
            html += `
                <a href="/courses/${l.course_slug}/lessons/${l.id}" class="search-result-item">
                    <span>${escapeHtml(l.title)}</span>
                    <span style="font-size: 0.75rem; color: var(--primary-green-dark); margin-left: 8px;">(${escapeHtml(l.course_title)})</span>
                </a>
            `;
        });
    }

    container.innerHTML = html;
    container.classList.add('show');
}

function initMobileNav() {
    const toggleBtn = document.getElementById('mobileNavToggle');
    const navLinks = document.getElementById('navLinks');
    const sidebarToggle = document.getElementById('sidebarToggleBtn');
    const lessonSidebar = document.getElementById('lessonSidebar');

    if (toggleBtn && navLinks) {
        toggleBtn.addEventListener('click', () => {
            navLinks.classList.toggle('show-mobile');
        });
    }

    if (sidebarToggle && lessonSidebar) {
        sidebarToggle.addEventListener('click', () => {
            lessonSidebar.classList.toggle('open');
        });
    }
}

function initLessonInteractions() {
    // 1. Mark as completed button
    const completeBtn = document.getElementById('toggleCompleteBtn');
    if (completeBtn) {
        completeBtn.addEventListener('click', () => {
            const lessonId = completeBtn.dataset.lessonId;
            const courseId = completeBtn.dataset.courseId;

            completeBtn.disabled = true;
            fetch('/api/toggle-lesson-complete', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ lesson_id: lessonId, course_id: courseId })
            })
            .then(res => res.json())
            .then(data => {
                completeBtn.disabled = false;
                if (data.success) {
                    if (data.is_completed) {
                        completeBtn.innerHTML = '✓ Completed';
                        completeBtn.classList.remove('btn-secondary');
                        completeBtn.classList.add('btn-primary');
                        showToast('Lesson marked as completed! Keep going!');
                    } else {
                        completeBtn.innerHTML = 'Mark as Completed';
                        completeBtn.classList.remove('btn-primary');
                        completeBtn.classList.add('btn-secondary');
                        showToast('Lesson unmarked.');
                    }
                    // Update progress bar if visible
                    const progFill = document.getElementById('courseProgressFill');
                    const progText = document.getElementById('courseProgressPercent');
                    if (progFill) progFill.style.width = `${data.progress_percent}%`;
                    if (progText) progText.textContent = `${data.progress_percent}%`;
                }
            })
            .catch(err => {
                completeBtn.disabled = false;
                console.error("Completion toggle error:", err);
            });
        });
    }

    // 2. Bookmark toggle button
    const bookmarkBtn = document.getElementById('bookmarkBtn');
    if (bookmarkBtn) {
        bookmarkBtn.addEventListener('click', () => {
            const lessonId = bookmarkBtn.dataset.lessonId;
            fetch('/api/toggle-bookmark', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ lesson_id: lessonId })
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    if (data.is_bookmarked) {
                        bookmarkBtn.innerHTML = '★ Saved';
                        bookmarkBtn.classList.add('btn-outline');
                        showToast('Lesson bookmarked for Smart Revision!');
                    } else {
                        bookmarkBtn.innerHTML = '☆ Bookmark';
                        bookmarkBtn.classList.remove('btn-outline');
                        showToast('Bookmark removed.');
                    }
                }
            });
        });
    }

    // 3. Save note button
    const saveNoteBtn = document.getElementById('saveNoteBtn');
    const noteTextarea = document.getElementById('lessonNoteText');
    if (saveNoteBtn && noteTextarea) {
        saveNoteBtn.addEventListener('click', () => {
            const lessonId = saveNoteBtn.dataset.lessonId;
            const noteText = noteTextarea.value;

            saveNoteBtn.textContent = 'Saving...';
            fetch('/api/save-note', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ lesson_id: lessonId, note_text: noteText })
            })
            .then(res => res.json())
            .then(data => {
                saveNoteBtn.textContent = 'Save Note';
                if (data.success) {
                    showToast('Personal notes saved successfully!');
                }
            })
            .catch(() => {
                saveNoteBtn.textContent = 'Save Note';
            });
        });
    }
}

function showToast(message) {
    let toast = document.getElementById('appToast');
    if (!toast) {
        toast = document.createElement('div');
        toast.id = 'appToast';
        toast.style.position = 'fixed';
        toast.style.bottom = '24px';
        toast.style.right = '24px';
        toast.style.backgroundColor = 'var(--text-primary)';
        toast.style.color = 'var(--bg-primary)';
        toast.style.padding = '12px 20px';
        toast.style.borderRadius = '8px';
        toast.style.boxShadow = 'var(--shadow-xl)';
        toast.style.zIndex = '99999';
        toast.style.fontSize = '0.9rem';
        toast.style.fontWeight = '600';
        toast.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
        document.body.appendChild(toast);
    }
    toast.textContent = message;
    toast.style.opacity = '1';
    toast.style.transform = 'translateY(0)';

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(10px)';
    }, 3000);
}

function escapeHtml(str) {
    if (!str) return '';
    return str.replace(/[&<>"']/g, m => ({
        '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
    })[m]);
}
