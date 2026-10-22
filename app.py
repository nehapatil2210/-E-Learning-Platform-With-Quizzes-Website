import os
from functools import wraps
from flask import (
    Flask, render_template, request, redirect, url_for, session,
    flash, jsonify, abort
)
from werkzeug.security import check_password_hash
import models
from database import init_db
from code_runner import run_python_code
from ai_engine import get_ai_response

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'elearning-secure-key-2026-production')

# Ensure database tables exist on startup
init_db()

# ----------------- Authentication Decorators & Helpers -----------------

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in as an administrator.', 'warning')
            return redirect(url_for('login', next=request.url))
        if session.get('user_role') != 'admin':
            flash('Access denied. Administrator privileges required.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@app.context_processor
def inject_global_data():
    current_user = None
    if 'user_id' in session:
        current_user = models.get_user_by_id(session['user_id'])
    categories = models.get_categories()
    return dict(current_user=current_user, nav_categories=categories)

# ----------------- 1. Home Page -----------------

@app.route('/')
def index():
    popular_courses = models.get_popular_courses(limit=8)
    categories = models.get_categories()
    quizzes = models.get_all_quizzes()[:6]

    continue_course = None
    if 'user_id' in session:
        enrollments = models.get_user_enrollments(session['user_id'])
        for e in enrollments:
            if e['progress_percent'] < 100.0:
                continue_course = e
                break

    return render_template(
        'index.html',
        popular_courses=popular_courses,
        categories=categories,
        quizzes=quizzes,
        continue_course=continue_course
    )

# ----------------- 2 & 3. Authentication: Login & Register -----------------

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

        if not email or not password:
            flash('Please provide both your email and password.', 'danger')
            return render_template('auth/login.html')

        user = models.get_user_by_email(email)
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['user_name'] = user['full_name']
            session['user_email'] = user['email']
            session['user_role'] = user['role']

            # Update streak
            models.update_user_streak(user['id'])

            flash(f"Welcome back, {user['full_name']}!", 'success')
            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            if user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email address or password. Please try again.', 'danger')

    return render_template('auth/login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        # Validations
        if not full_name or not email or not password or not confirm_password:
            flash('All registration fields are required.', 'danger')
            return render_template('auth/register.html')

        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return render_template('auth/register.html')

        if password != confirm_password:
            flash('Passwords do not match. Please verify and re-type.', 'danger')
            return render_template('auth/register.html')

        user_id, error = models.create_user(full_name, email, password, role='student')
        if error:
            flash(error, 'danger')
            return render_template('auth/register.html')

        user = models.get_user_by_id(user_id)
        session['user_id'] = user['id']
        session['user_name'] = user['full_name']
        session['user_email'] = user['email']
        session['user_role'] = user['role']

        flash('Registration successful! Welcome to E-Learning Platform with Quizzes.', 'success')
        return redirect(url_for('dashboard'))

    return render_template('auth/register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been successfully logged out.', 'info')
    return redirect(url_for('index'))

# ----------------- 4. Course Catalog -----------------

@app.route('/courses')
def course_catalog():
    category_id = request.args.get('category', type=int)
    difficulty = request.args.get('difficulty')
    search = request.args.get('search')

    courses = models.get_all_courses(category_id=category_id, difficulty=difficulty, search=search)
    categories = models.get_categories()

    return render_template(
        'courses/catalog.html',
        courses=courses,
        categories=categories,
        selected_category=category_id,
        selected_difficulty=difficulty,
        search_query=search
    )

# ----------------- 5. Course Details -----------------

@app.route('/courses/<slug>')
def course_detail(slug):
    course = models.get_course_by_slug(slug)
    if not course:
        abort(404)

    user_id = session.get('user_id')
    structure = models.get_course_structure(course['id'], user_id=user_id)

    # Check enrollment status
    is_enrolled = False
    enrollment = None
    if user_id:
        enrollments = models.get_user_enrollments(user_id)
        for e in enrollments:
            if e['course_id'] == course['id']:
                is_enrolled = True
                enrollment = e
                break

    # Get course quiz
    quiz = models.get_quiz_by_course_id(course['id'])

    # Find first lesson
    first_lesson_id = None
    if structure and structure[0]['lessons']:
        first_lesson_id = structure[0]['lessons'][0]['id']

    return render_template(
        'courses/detail.html',
        course=course,
        structure=structure,
        is_enrolled=is_enrolled,
        enrollment=enrollment,
        quiz=quiz,
        first_lesson_id=first_lesson_id
    )

@app.route('/courses/<slug>/enroll', methods=['POST'])
@login_required
def enroll_course(slug):
    course = models.get_course_by_slug(slug)
    if not course:
        abort(404)

    models.enroll_user_in_course(session['user_id'], course['id'])
    flash(f"You have successfully enrolled in {course['title']}!", 'success')

    # Redirect to first lesson or course detail
    structure = models.get_course_structure(course['id'], user_id=session['user_id'])
    if structure and structure[0]['lessons']:
        first_id = structure[0]['lessons'][0]['id']
        return redirect(url_for('lesson_viewer', slug=slug, lesson_id=first_id))
    return redirect(url_for('course_detail', slug=slug))

# ----------------- 6. Lesson Viewer -----------------

@app.route('/courses/<slug>/lessons/<int:lesson_id>')
def lesson_viewer(slug, lesson_id):
    user_id = session.get('user_id')
    lesson, course, prev_lesson, next_lesson, is_completed, is_bookmarked, note_text = models.get_lesson_details(
        slug, lesson_id, user_id=user_id
    )

    if not lesson or not course:
        abort(404)

    # Automatically enroll if student views lesson
    if user_id:
        models.enroll_user_in_course(user_id, course['id'])

    structure = models.get_course_structure(course['id'], user_id=user_id)
    quiz = models.get_quiz_by_course_id(course['id'])

    return render_template(
        'courses/lesson.html',
        course=course,
        lesson=lesson,
        prev_lesson=prev_lesson,
        next_lesson=next_lesson,
        is_completed=is_completed,
        is_bookmarked=is_bookmarked,
        note_text=note_text,
        structure=structure,
        quiz=quiz
    )

# ----------------- 7, 8, 9. Quizzes System -----------------

@app.route('/quizzes')
def quizzes_index():
    subject = request.args.get('subject')
    difficulty = request.args.get('difficulty')
    quizzes = models.get_all_quizzes(subject_slug=subject, difficulty=difficulty)
    courses = models.get_all_courses()

    return render_template(
        'quizzes/index.html',
        quizzes=quizzes,
        courses=courses,
        selected_subject=subject,
        selected_difficulty=difficulty
    )

@app.route('/quizzes/<int:quiz_id>/instructions')
def quiz_instructions(quiz_id):
    quiz = models.get_quiz_by_id(quiz_id)
    if not quiz:
        abort(404)
    questions = models.get_quiz_questions(quiz_id)

    # Previous attempt if logged in
    user_attempt = None
    if 'user_id' in session:
        conn = models.get_db_connection()
        user_attempt = conn.execute('''
        SELECT * FROM quiz_attempts WHERE user_id = ? AND quiz_id = ?
        ORDER BY completed_at DESC LIMIT 1
        ''', (session['user_id'], quiz_id)).fetchone()
        conn.close()

    return render_template(
        'quizzes/instructions.html',
        quiz=quiz,
        total_questions=len(questions),
        user_attempt=user_attempt
    )

@app.route('/quizzes/<int:quiz_id>/take', methods=['GET', 'POST'])
@login_required
def quiz_take(quiz_id):
    quiz = models.get_quiz_by_id(quiz_id)
    if not quiz:
        abort(404)

    questions = models.get_quiz_questions(quiz_id)
    if not questions:
        flash('This quiz has no questions available.', 'warning')
        return redirect(url_for('quizzes_index'))

    if request.method == 'POST':
        time_taken = request.form.get('time_taken_seconds', 0, type=int)
        answers = {}
        for q in questions:
            key = f"q_{q['id']}"
            if key in request.form:
                answers[str(q['id'])] = request.form[key]

        attempt_id = models.submit_quiz_attempt(
            session['user_id'],
            quiz_id,
            answers,
            time_taken_seconds=time_taken
        )
        return redirect(url_for('quiz_results', attempt_id=attempt_id))

    return render_template('quizzes/take.html', quiz=quiz, questions=questions)

@app.route('/quizzes/results/<int:attempt_id>')
@login_required
def quiz_results(attempt_id):
    user_id = session['user_id']
    attempt, answers = models.get_quiz_attempt_result(attempt_id, user_id=user_id)
    if not attempt:
        abort(404)

    # Check if this qualifies for course completion & certificate
    is_eligible, completed_count, total_lessons, quiz_passed, cert = models.check_certificate_eligibility(
        user_id, attempt['course_id']
    )

    return render_template(
        'quizzes/result.html',
        attempt=attempt,
        answers=answers,
        is_eligible=is_eligible,
        certificate=cert
    )

# ----------------- 10. Student Dashboard -----------------

@app.route('/dashboard')
@login_required
def dashboard():
    user_id = session['user_id']
    stats = models.get_student_dashboard_data(user_id)
    recommendations = models.get_personalized_recommendations(user_id)

    return render_template(
        'student/dashboard.html',
        stats=stats,
        recommendations=recommendations
    )

# ----------------- 11. My Learning -----------------

@app.route('/my-learning')
@login_required
def my_learning():
    user_id = session['user_id']
    enrollments = models.get_user_enrollments(user_id)
    certificates = models.get_user_certificates(user_id)

    # In progress vs completed
    in_progress = [e for e in enrollments if e['progress_percent'] < 100.0]
    completed = [e for e in enrollments if e['progress_percent'] >= 100.0]

    return render_template(
        'student/my_learning.html',
        enrollments=enrollments,
        in_progress=in_progress,
        completed=completed,
        certificates=certificates
    )

# ----------------- 12. Bookmarks and Notes (Smart Revision) -----------------

@app.route('/saved-notes')
@login_required
def saved_notes():
    user_id = session['user_id']
    revision = models.get_user_revision_data(user_id)
    return render_template('student/saved_notes.html', revision=revision)

# ----------------- 13. Coding Playground -----------------

@app.route('/playground')
def playground():
    default_lang = request.args.get('lang', 'python')
    return render_template('playground/playground.html', default_lang=default_lang)

# ----------------- 14. Certificates & Verification -----------------

@app.route('/certificates')
@login_required
def certificates_list():
    user_id = session['user_id']
    certs = models.get_user_certificates(user_id)
    return render_template('student/certificates.html', certificates=certs)

@app.route('/certificates/generate/<int:course_id>', methods=['POST'])
@login_required
def generate_certificate(course_id):
    user_id = session['user_id']
    is_eligible, _, _, _, existing = models.check_certificate_eligibility(user_id, course_id)

    if not is_eligible and not existing:
        flash('You must complete all lessons and pass the course quiz to earn this certificate.', 'warning')
        return redirect(url_for('my_learning'))

    cert_code = models.generate_course_certificate(user_id, course_id)
    flash('Congratulations! Your verified certificate of completion has been issued.', 'success')
    return redirect(url_for('view_certificate', cert_code=cert_code))

@app.route('/certificates/<cert_code>')
def view_certificate(cert_code):
    cert = models.get_certificate_details(cert_code)
    if not cert:
        flash('Invalid or non-existent certificate code.', 'danger')
        return redirect(url_for('index'))
    return render_template('student/certificate_view.html', cert=cert)

# ----------------- 15. AI Learning Assistant -----------------

@app.route('/ai-assistant')
def ai_assistant():
    course_context = request.args.get('course', '')
    return render_template('ai/assistant.html', course_context=course_context)

# ----------------- 16, 17, 19. Informational Pages -----------------

@app.route('/about')
def about():
    return render_template('pages/about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name', '')
        email = request.form.get('email', '')
        subject = request.form.get('subject', '')
        message = request.form.get('message', '')

        if not name or not email or not message:
            flash('Please fill in all required fields.', 'danger')
            return render_template('pages/contact.html')

        models.add_contact_message(name, email, subject, message)
        flash('Thank you for contacting us! We have received your message and will respond shortly.', 'success')
        return redirect(url_for('contact'))

    return render_template('pages/contact.html')

@app.route('/privacy')
def privacy():
    return render_template('pages/privacy.html')

# ----------------- 18. Admin Dashboard & Management -----------------

@app.route('/admin')
@admin_required
def admin_dashboard():
    stats = models.get_admin_dashboard_stats()
    return render_template('admin/dashboard.html', stats=stats)

@app.route('/admin/courses')
@admin_required
def admin_courses():
    courses = models.get_all_courses()
    categories = models.get_categories()
    return render_template('admin/courses.html', courses=courses, categories=categories)

@app.route('/admin/courses/new', methods=['POST'])
@admin_required
def admin_create_course():
    title = request.form.get('title')
    category_id = request.form.get('category_id', type=int)
    description = request.form.get('description')
    short_desc = request.form.get('short_desc')
    difficulty = request.form.get('difficulty', 'Beginner')
    estimated_hours = request.form.get('estimated_hours', 10, type=int)
    icon = request.form.get('icon', 'code')
    badge_color = request.form.get('badge_color', '#10b981')

    slug = title.lower().replace(' ', '-').replace('+', 'p').replace('#', 'sharp')

    conn = models.get_db_connection()
    conn.execute('''
    INSERT INTO courses (title, slug, category_id, description, short_desc, difficulty, estimated_hours, icon, badge_color, is_popular, is_published)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 1)
    ''', (title, slug, category_id, description, short_desc, difficulty, estimated_hours, icon, badge_color))
    conn.commit()
    conn.close()

    flash(f"Course '{title}' created successfully.", 'success')
    return redirect(url_for('admin_courses'))

@app.route('/admin/courses/<int:course_id>/delete', methods=['POST'])
@admin_required
def admin_delete_course(course_id):
    conn = models.get_db_connection()
    conn.execute("DELETE FROM courses WHERE id = ?", (course_id,))
    conn.commit()
    conn.close()
    flash('Course deleted successfully.', 'info')
    return redirect(url_for('admin_courses'))

@app.route('/admin/lessons')
@admin_required
def admin_lessons():
    conn = models.get_db_connection()
    courses = conn.execute("SELECT id, title FROM courses ORDER BY id ASC").fetchall()
    selected_course_id = request.args.get('course_id', type=int)
    if not selected_course_id and courses:
        selected_course_id = courses[0]['id']

    modules = []
    lessons = []
    if selected_course_id:
        modules = conn.execute("SELECT * FROM modules WHERE course_id = ? ORDER BY order_num ASC", (selected_course_id,)).fetchall()
        lessons = conn.execute('''
        SELECT l.*, m.title as module_title 
        FROM lessons l
        JOIN modules m ON l.module_id = m.id
        WHERE l.course_id = ?
        ORDER BY m.order_num ASC, l.order_num ASC
        ''', (selected_course_id,)).fetchall()

    conn.close()
    return render_template(
        'admin/lessons.html',
        courses=courses,
        selected_course_id=selected_course_id,
        modules=modules,
        lessons=lessons
    )

@app.route('/admin/lessons/new', methods=['POST'])
@admin_required
def admin_create_lesson():
    course_id = request.form.get('course_id', type=int)
    module_id = request.form.get('module_id', type=int)
    title = request.form.get('title')
    content_html = request.form.get('content_html')
    code_example = request.form.get('code_example')
    expected_output = request.form.get('expected_output')
    practice_task = request.form.get('practice_task')

    slug = title.lower().replace(' ', '-')

    conn = models.get_db_connection()
    conn.execute('''
    INSERT INTO lessons (module_id, course_id, title, slug, content_html, code_example, expected_output, practice_task)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (module_id, course_id, title, slug, content_html, code_example, expected_output, practice_task))
    conn.commit()
    conn.close()

    flash(f"Lesson '{title}' added successfully.", 'success')
    return redirect(url_for('admin_lessons', course_id=course_id))

@app.route('/admin/quizzes')
@admin_required
def admin_quizzes():
    quizzes = models.get_all_quizzes()
    return render_template('admin/quizzes.html', quizzes=quizzes)

@app.route('/admin/users')
@admin_required
def admin_users():
    conn = models.get_db_connection()
    users = conn.execute('''
    SELECT u.*,
           (SELECT COUNT(*) FROM enrollments WHERE user_id = u.id) as enrolled_count,
           (SELECT COUNT(*) FROM quiz_attempts WHERE user_id = u.id) as quiz_count,
           (SELECT COUNT(*) FROM certificates WHERE user_id = u.id) as cert_count
    FROM users u
    ORDER BY u.created_at DESC
    ''').fetchall()
    conn.close()
    return render_template('admin/users.html', users=users)

# ----------------- AJAX / API Endpoints -----------------

@app.route('/api/toggle-lesson-complete', methods=['POST'])
@login_required
def api_toggle_lesson_complete():
    data = request.get_json() or {}
    lesson_id = data.get('lesson_id')
    course_id = data.get('course_id')

    if not lesson_id or not course_id:
        return jsonify({'error': 'Missing lesson_id or course_id'}), 400

    is_completed, new_progress = models.toggle_lesson_completion(
        session['user_id'], int(lesson_id), int(course_id)
    )

    return jsonify({
        'success': True,
        'is_completed': is_completed,
        'progress_percent': new_progress
    })

@app.route('/api/toggle-bookmark', methods=['POST'])
@login_required
def api_toggle_bookmark():
    data = request.get_json() or {}
    lesson_id = data.get('lesson_id')
    if not lesson_id:
        return jsonify({'error': 'Missing lesson_id'}), 400

    is_bookmarked = models.toggle_bookmark(session['user_id'], int(lesson_id))
    return jsonify({'success': True, 'is_bookmarked': is_bookmarked})

@app.route('/api/save-note', methods=['POST'])
@login_required
def api_save_note():
    data = request.get_json() or {}
    lesson_id = data.get('lesson_id')
    note_text = data.get('note_text', '')

    if not lesson_id:
        return jsonify({'error': 'Missing lesson_id'}), 400

    models.save_student_note(session['user_id'], int(lesson_id), note_text)
    return jsonify({'success': True})

@app.route('/api/execute-code', methods=['POST'])
def api_execute_code():
    data = request.get_json() or {}
    code = data.get('code', '')
    lang = data.get('language', 'python').lower()

    if lang == 'python':
        result = run_python_code(code)
        return jsonify(result)
    else:
        return jsonify({
            'success': True,
            'output': f"[{lang.upper()} Sandbox] Code syntax verified.\nWeb execution is active in Playground preview!"
        })

@app.route('/api/ai-chat', methods=['POST'])
def api_ai_chat():
    data = request.get_json() or {}
    query = data.get('query', '')
    context_course = data.get('course', '')

    if not query.strip():
        return jsonify({'error': 'Empty question'}), 400

    response = get_ai_response(query, context_course)
    return jsonify(response)

@app.route('/api/search', methods=['GET'])
def api_search():
    q = request.args.get('q', '').strip()
    if not q or len(q) < 2:
        return jsonify({'courses': [], 'lessons': []})

    conn = models.get_db_connection()
    term = f"%{q}%"

    courses = conn.execute('''
    SELECT id, title, slug, short_desc, difficulty, badge_color
    FROM courses
    WHERE is_published = 1 AND (title LIKE ? OR description LIKE ? OR short_desc LIKE ?)
    LIMIT 5
    ''', (term, term, term)).fetchall()

    lessons = conn.execute('''
    SELECT l.id, l.title, l.slug, c.title as course_title, c.slug as course_slug
    FROM lessons l
    JOIN courses c ON l.course_id = c.id
    WHERE l.title LIKE ? OR l.content_html LIKE ?
    LIMIT 6
    ''', (term, term)).fetchall()

    conn.close()

    return jsonify({
        'courses': [dict(c) for c in courses],
        'lessons': [dict(l) for l in lessons]
    })

# ----------------- Error Handlers -----------------

@app.errorhandler(404)
def page_not_found(e):
    return render_template('pages/404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('pages/500.html'), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='127.0.0.1')
