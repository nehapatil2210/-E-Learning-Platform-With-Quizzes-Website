import sqlite3
import uuid
from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db_connection

# ----------------- User Management -----------------

def get_user_by_email(email):
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE LOWER(email) = LOWER(?)", (email.strip(),)).fetchone()
    conn.close()
    return user

def get_user_by_id(user_id):
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return user

def create_user(full_name, email, password, role='student'):
    conn = get_db_connection()
    hashed = generate_password_hash(password)
    try:
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO users (full_name, email, password_hash, role, streak_count, last_active_date)
        VALUES (?, ?, ?, ?, 1, date('now'))
        ''', (full_name.strip(), email.strip().lower(), hashed, role))
        user_id = cursor.lastrowid
        conn.commit()
        return user_id, None
    except sqlite3.IntegrityError:
        return None, "An account with this email address already exists."
    finally:
        conn.close()

def update_user_streak(user_id):
    conn = get_db_connection()
    user = conn.execute("SELECT last_active_date, streak_count FROM users WHERE id = ?", (user_id,)).fetchone()
    if user:
        today_str = date.today().isoformat()
        last_active = user['last_active_date']
        streak = user['streak_count'] or 1

        if last_active != today_str:
            if last_active:
                try:
                    last_date = datetime.strptime(last_active, '%Y-%m-%d').date()
                    diff = (date.today() - last_date).days
                    if diff == 1:
                        streak += 1
                    elif diff > 1:
                        streak = 1
                except Exception:
                    streak = 1
            conn.execute('''
            UPDATE users SET streak_count = ?, last_active_date = ? WHERE id = ?
            ''', (streak, today_str, user_id))
            conn.commit()
    conn.close()

# ----------------- Courses & Categories -----------------

def get_categories():
    conn = get_db_connection()
    categories = conn.execute("SELECT * FROM categories ORDER BY name ASC").fetchall()
    conn.close()
    return categories

def get_all_courses(category_id=None, difficulty=None, search=None):
    conn = get_db_connection()
    query = '''
    SELECT c.*, cat.name as category_name,
           (SELECT COUNT(*) FROM lessons WHERE course_id = c.id) as lesson_count,
           (SELECT COUNT(*) FROM enrollments WHERE course_id = c.id) as student_count,
           (SELECT id FROM quizzes WHERE course_id = c.id LIMIT 1) as quiz_id
    FROM courses c
    LEFT JOIN categories cat ON c.category_id = cat.id
    WHERE c.is_published = 1
    '''
    params = []

    if category_id:
        query += " AND c.category_id = ?"
        params.append(category_id)
    if difficulty:
        query += " AND LOWER(c.difficulty) = LOWER(?)"
        params.append(difficulty)
    if search:
        query += " AND (c.title LIKE ? OR c.description LIKE ? OR c.short_desc LIKE ?)"
        term = f"%{search.strip()}%"
        params.extend([term, term, term])

    query += " ORDER BY c.is_popular DESC, c.id ASC"
    courses = conn.execute(query, params).fetchall()
    conn.close()
    return courses

def get_popular_courses(limit=8):
    conn = get_db_connection()
    courses = conn.execute('''
    SELECT c.*, cat.name as category_name,
           (SELECT COUNT(*) FROM lessons WHERE course_id = c.id) as lesson_count,
           (SELECT COUNT(*) FROM enrollments WHERE course_id = c.id) as student_count,
           (SELECT id FROM quizzes WHERE course_id = c.id LIMIT 1) as quiz_id
    FROM courses c
    LEFT JOIN categories cat ON c.category_id = cat.id
    WHERE c.is_published = 1
    ORDER BY c.is_popular DESC, c.id ASC
    LIMIT ?
    ''', (limit,)).fetchall()
    conn.close()
    return courses

def get_course_by_slug(slug):
    conn = get_db_connection()
    course = conn.execute('''
    SELECT c.*, cat.name as category_name,
           (SELECT COUNT(*) FROM lessons WHERE course_id = c.id) as lesson_count,
           (SELECT COUNT(*) FROM enrollments WHERE course_id = c.id) as student_count,
           (SELECT id FROM quizzes WHERE course_id = c.id LIMIT 1) as quiz_id
    FROM courses c
    LEFT JOIN categories cat ON c.category_id = cat.id
    WHERE c.slug = ?
    ''', (slug,)).fetchone()
    conn.close()
    return course

def get_course_by_id(course_id):
    conn = get_db_connection()
    course = conn.execute('''
    SELECT c.*, cat.name as category_name
    FROM courses c
    LEFT JOIN categories cat ON c.category_id = cat.id
    WHERE c.id = ?
    ''', (course_id,)).fetchone()
    conn.close()
    return course

def get_course_structure(course_id, user_id=None):
    """Returns modules with lessons, and completion status for user if provided."""
    conn = get_db_connection()
    modules = conn.execute('''
    SELECT * FROM modules WHERE course_id = ? ORDER BY order_num ASC, id ASC
    ''', (course_id,)).fetchall()

    structure = []
    for mod in modules:
        lessons = conn.execute('''
        SELECT l.*,
               CASE WHEN lp.id IS NOT NULL THEN 1 ELSE 0 END as is_completed,
               CASE WHEN bm.id IS NOT NULL THEN 1 ELSE 0 END as is_bookmarked
        FROM lessons l
        LEFT JOIN lesson_progress lp ON lp.lesson_id = l.id AND lp.user_id = ?
        LEFT JOIN bookmarks bm ON bm.lesson_id = l.id AND bm.user_id = ?
        WHERE l.module_id = ?
        ORDER BY l.order_num ASC, l.id ASC
        ''', (user_id, user_id, mod['id'])).fetchall()

        structure.append({
            'module': mod,
            'lessons': lessons
        })

    conn.close()
    return structure

# ----------------- Lessons & Navigation -----------------

def get_quiz_by_course_id(course_id):
    conn = get_db_connection()
    quiz = conn.execute('''
    SELECT q.*, c.title as course_title, c.slug as course_slug, c.icon as course_icon
    FROM quizzes q
    JOIN courses c ON q.course_id = c.id
    WHERE q.course_id = ?
    LIMIT 1
    ''', (course_id,)).fetchone()
    conn.close()
    return quiz

def get_lesson_details(course_slug, lesson_id, user_id=None):
    conn = get_db_connection()
    course = conn.execute('''
    SELECT c.*, (SELECT id FROM quizzes WHERE course_id = c.id LIMIT 1) as quiz_id
    FROM courses c WHERE c.slug = ?
    ''', (course_slug,)).fetchone()
    if not course:
        conn.close()
        return None, None, None, None, None, None, None

    lesson = conn.execute('''
    SELECT l.*, m.title as module_title 
    FROM lessons l
    JOIN modules m ON l.module_id = m.id
    WHERE l.id = ? AND l.course_id = ?
    ''', (lesson_id, course['id'])).fetchone()

    if not lesson:
        conn.close()
        return None, course, None, None, None, None, None

    # Get ordered list of all lessons in course to find prev and next
    all_lessons = conn.execute('''
    SELECT l.id, l.title, l.slug
    FROM lessons l
    JOIN modules m ON l.module_id = m.id
    WHERE l.course_id = ?
    ORDER BY m.order_num ASC, l.order_num ASC, l.id ASC
    ''', (course['id'],)).fetchall()

    prev_lesson = None
    next_lesson = None
    for i, item in enumerate(all_lessons):
        if item['id'] == lesson_id:
            if i > 0:
                prev_lesson = all_lessons[i - 1]
            if i < len(all_lessons) - 1:
                next_lesson = all_lessons[i + 1]
            break

    # Check user completion, bookmark, and personal note
    is_completed = False
    is_bookmarked = False
    note_text = ""
    if user_id:
        comp = conn.execute('''
        SELECT id FROM lesson_progress WHERE user_id = ? AND lesson_id = ?
        ''', (user_id, lesson_id)).fetchone()
        is_completed = (comp is not None)

        bm = conn.execute('''
        SELECT id FROM bookmarks WHERE user_id = ? AND lesson_id = ?
        ''', (user_id, lesson_id)).fetchone()
        is_bookmarked = (bm is not None)

        nt = conn.execute('''
        SELECT note_text FROM student_notes WHERE user_id = ? AND lesson_id = ?
        ''', (user_id, lesson_id)).fetchone()
        if nt:
            note_text = nt['note_text']

        # Update last accessed lesson in enrollment
        conn.execute('''
        UPDATE enrollments 
        SET last_accessed_lesson_id = ? 
        WHERE user_id = ? AND course_id = ?
        ''', (lesson_id, user_id, course['id']))
        conn.commit()

    conn.close()
    return lesson, course, prev_lesson, next_lesson, is_completed, is_bookmarked, note_text

def toggle_lesson_completion(user_id, lesson_id, course_id):
    conn = get_db_connection()
    existing = conn.execute('''
    SELECT id FROM lesson_progress WHERE user_id = ? AND lesson_id = ?
    ''', (user_id, lesson_id)).fetchone()

    if existing:
        conn.execute("DELETE FROM lesson_progress WHERE user_id = ? AND lesson_id = ?", (user_id, lesson_id))
        is_now_completed = False
    else:
        conn.execute('''
        INSERT INTO lesson_progress (user_id, lesson_id, course_id, is_completed)
        VALUES (?, ?, ?, 1)
        ''', (user_id, lesson_id, course_id))
        is_now_completed = True

    # Recalculate course progress percentage
    total_lessons = conn.execute("SELECT COUNT(*) FROM lessons WHERE course_id = ?", (course_id,)).fetchone()[0]
    completed_lessons = conn.execute('''
    SELECT COUNT(*) FROM lesson_progress WHERE user_id = ? AND course_id = ?
    ''', (user_id, course_id)).fetchone()[0]

    pct = round((completed_lessons / total_lessons * 100), 1) if total_lessons > 0 else 0.0

    # Ensure enrolled
    enrolled = conn.execute("SELECT id FROM enrollments WHERE user_id = ? AND course_id = ?", (user_id, course_id)).fetchone()
    if enrolled:
        completed_at = "CURRENT_TIMESTAMP" if pct >= 100.0 else "NULL"
        conn.execute(f'''
        UPDATE enrollments 
        SET progress_percent = ?, 
            last_accessed_lesson_id = ?,
            completed_at = {completed_at}
        WHERE user_id = ? AND course_id = ?
        ''', (pct, lesson_id, user_id, course_id))
    else:
        conn.execute('''
        INSERT INTO enrollments (user_id, course_id, last_accessed_lesson_id, progress_percent)
        VALUES (?, ?, ?, ?)
        ''', (user_id, course_id, lesson_id, pct))

    conn.commit()
    conn.close()

    # Check for badge awards
    check_and_award_badges(user_id)
    return is_now_completed, pct

def toggle_bookmark(user_id, lesson_id):
    conn = get_db_connection()
    existing = conn.execute("SELECT id FROM bookmarks WHERE user_id = ? AND lesson_id = ?", (user_id, lesson_id)).fetchone()
    if existing:
        conn.execute("DELETE FROM bookmarks WHERE user_id = ? AND lesson_id = ?", (user_id, lesson_id))
        is_bookmarked = False
    else:
        conn.execute("INSERT INTO bookmarks (user_id, lesson_id) VALUES (?, ?)", (user_id, lesson_id))
        is_bookmarked = True
    conn.commit()
    conn.close()
    return is_bookmarked

def save_student_note(user_id, lesson_id, note_text):
    conn = get_db_connection()
    if not note_text.strip():
        conn.execute("DELETE FROM student_notes WHERE user_id = ? AND lesson_id = ?", (user_id, lesson_id))
    else:
        conn.execute('''
        INSERT INTO student_notes (user_id, lesson_id, note_text, updated_at)
        VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(user_id, lesson_id) DO UPDATE SET
            note_text = excluded.note_text,
            updated_at = CURRENT_TIMESTAMP
        ''', (user_id, lesson_id, note_text.strip()))
    conn.commit()
    conn.close()
    check_and_award_badges(user_id)
    return True

# ----------------- Enrollments & Dashboard -----------------

def enroll_user_in_course(user_id, course_id):
    conn = get_db_connection()
    try:
        # Get first lesson of course
        first_lesson = conn.execute('''
        SELECT l.id FROM lessons l
        JOIN modules m ON l.module_id = m.id
        WHERE l.course_id = ?
        ORDER BY m.order_num ASC, l.order_num ASC, l.id ASC
        LIMIT 1
        ''', (course_id,)).fetchone()
        first_id = first_lesson[0] if first_lesson else None

        conn.execute('''
        INSERT OR IGNORE INTO enrollments (user_id, course_id, last_accessed_lesson_id, progress_percent)
        VALUES (?, ?, ?, 0.0)
        ''', (user_id, course_id, first_id))
        conn.commit()
        return True
    finally:
        conn.close()

def get_user_enrollments(user_id):
    conn = get_db_connection()
    enrollments = conn.execute('''
    SELECT e.*, c.title as course_title, c.slug as course_slug, c.icon as course_icon,
           c.difficulty, c.badge_color,
           (SELECT COUNT(*) FROM lessons WHERE course_id = c.id) as total_lessons,
           (SELECT COUNT(*) FROM lesson_progress lp WHERE lp.course_id = c.id AND lp.user_id = e.user_id) as completed_lessons,
           l.title as last_lesson_title, l.id as last_lesson_id
    FROM enrollments e
    JOIN courses c ON e.course_id = c.id
    LEFT JOIN lessons l ON e.last_accessed_lesson_id = l.id
    WHERE e.user_id = ?
    ORDER BY e.enrolled_at DESC
    ''', (user_id,)).fetchall()
    conn.close()
    return enrollments

def get_student_dashboard_data(user_id):
    conn = get_db_connection()

    # Enrolled courses stats
    enrollments = conn.execute('''
    SELECT e.*, c.title as course_title, c.slug as course_slug, c.icon as course_icon,
           c.badge_color, c.difficulty,
           (SELECT COUNT(*) FROM lessons WHERE course_id = c.id) as total_lessons,
           (SELECT COUNT(*) FROM lesson_progress WHERE user_id = e.user_id AND course_id = c.id) as completed_lessons,
           l.title as last_lesson_title, l.id as last_lesson_id
    FROM enrollments e
    JOIN courses c ON e.course_id = c.id
    LEFT JOIN lessons l ON e.last_accessed_lesson_id = l.id
    WHERE e.user_id = ?
    ORDER BY e.enrolled_at DESC
    ''', (user_id,)).fetchall()

    total_enrolled = len(enrollments)
    completed_courses = sum(1 for e in enrollments if e['progress_percent'] >= 100.0)
    in_progress_courses = total_enrolled - completed_courses

    # Average progress across enrolled courses
    avg_progress = 0.0
    if total_enrolled > 0:
        avg_progress = round(sum(e['progress_percent'] for e in enrollments) / total_enrolled, 1)

    # Quiz statistics
    quiz_stats = conn.execute('''
    SELECT COUNT(*) as total_attempts,
           COALESCE(AVG(percentage), 0.0) as avg_score,
           SUM(CASE WHEN passed = 1 THEN 1 ELSE 0 END) as passed_quizzes
    FROM quiz_attempts
    WHERE user_id = ?
    ''', (user_id,)).fetchone()

    total_quizzes_attempted = quiz_stats['total_attempts']
    avg_quiz_score = round(quiz_stats['avg_score'], 1)

    # Recent Quiz Results
    recent_quiz_results = conn.execute('''
    SELECT qa.*, q.title as quiz_title, c.title as course_title, c.slug as course_slug
    FROM quiz_attempts qa
    JOIN quizzes q ON qa.quiz_id = q.id
    JOIN courses c ON q.course_id = c.id
    WHERE qa.user_id = ?
    ORDER BY qa.completed_at DESC
    LIMIT 5
    ''', (user_id,)).fetchall()

    # Continue Learning target (most recently touched in-progress course)
    continue_learning = None
    for e in enrollments:
        if e['progress_percent'] < 100.0 and e['last_lesson_id']:
            continue_learning = e
            break
    if not continue_learning and enrollments:
        continue_learning = enrollments[0]

    # Badges
    badges = conn.execute('''
    SELECT b.*, ub.awarded_at
    FROM user_badges ub
    JOIN badges b ON ub.badge_id = b.id
    WHERE ub.user_id = ?
    ORDER BY ub.awarded_at DESC
    ''', (user_id,)).fetchall()

    # Quiz Score History for Chart
    score_history = conn.execute('''
    SELECT q.title as quiz_title, qa.percentage, qa.completed_at
    FROM quiz_attempts qa
    JOIN quizzes q ON qa.quiz_id = q.id
    WHERE qa.user_id = ?
    ORDER BY qa.completed_at ASC
    LIMIT 10
    ''', (user_id,)).fetchall()

    # Category completion breakdown
    category_progress = conn.execute('''
    SELECT cat.name, COUNT(DISTINCT l.id) as total_cat_lessons,
           COUNT(DISTINCT lp.lesson_id) as completed_cat_lessons
    FROM categories cat
    JOIN courses c ON c.category_id = cat.id
    JOIN lessons l ON l.course_id = c.id
    LEFT JOIN lesson_progress lp ON lp.lesson_id = l.id AND lp.user_id = ?
    GROUP BY cat.id
    ''', (user_id,)).fetchall()

    # Certificates count
    cert_count = conn.execute("SELECT COUNT(*) FROM certificates WHERE user_id = ?", (user_id,)).fetchone()[0]

    # User info (streak)
    user = conn.execute("SELECT streak_count, full_name, email FROM users WHERE id = ?", (user_id,)).fetchone()

    conn.close()

    return {
        'user': user,
        'total_enrolled': total_enrolled,
        'completed_courses': completed_courses,
        'in_progress_courses': in_progress_courses,
        'avg_progress': avg_progress,
        'total_quizzes_attempted': total_quizzes_attempted,
        'avg_quiz_score': avg_quiz_score,
        'passed_quizzes': quiz_stats['passed_quizzes'] or 0,
        'enrollments': enrollments,
        'continue_learning': continue_learning,
        'recent_quiz_results': recent_quiz_results,
        'badges': badges,
        'score_history': score_history,
        'category_progress': category_progress,
        'cert_count': cert_count
    }

# ----------------- Quizzes System -----------------

def get_all_quizzes(subject_slug=None, difficulty=None):
    conn = get_db_connection()
    query = '''
    SELECT q.*, c.title as course_title, c.slug as course_slug, c.badge_color, c.icon as course_icon,
           (SELECT COUNT(*) FROM quiz_questions WHERE quiz_id = q.id) as question_count
    FROM quizzes q
    JOIN courses c ON q.course_id = c.id
    WHERE c.is_published = 1
    '''
    params = []
    if subject_slug:
        query += " AND c.slug = ?"
        params.append(subject_slug)
    if difficulty:
        query += " AND LOWER(q.difficulty) = LOWER(?)"
        params.append(difficulty)

    query += " ORDER BY c.id ASC"
    quizzes = conn.execute(query, params).fetchall()
    conn.close()
    return quizzes

def get_quiz_by_id(quiz_id):
    conn = get_db_connection()
    quiz = conn.execute('''
    SELECT q.*, c.title as course_title, c.slug as course_slug, c.icon as course_icon
    FROM quizzes q
    JOIN courses c ON q.course_id = c.id
    WHERE q.id = ?
    ''', (quiz_id,)).fetchone()
    conn.close()
    return quiz

def get_quiz_questions(quiz_id):
    conn = get_db_connection()
    questions = conn.execute('''
    SELECT * FROM quiz_questions WHERE quiz_id = ? ORDER BY order_num ASC, id ASC
    ''', (quiz_id,)).fetchall()
    conn.close()
    return questions

def submit_quiz_attempt(user_id, quiz_id, answers_dict, time_taken_seconds=0):
    conn = get_db_connection()
    questions = conn.execute('''
    SELECT * FROM quiz_questions WHERE quiz_id = ? ORDER BY order_num ASC, id ASC
    ''', (quiz_id,)).fetchall()

    total_questions = len(questions)
    correct_count = 0

    evaluated_answers = []
    for q in questions:
        q_id = q['id']
        selected = answers_dict.get(str(q_id), '').strip().upper()
        is_correct = 1 if (selected and selected == q['correct_option'].strip().upper()) else 0
        if is_correct:
            correct_count += 1
        evaluated_answers.append({
            'question_id': q_id,
            'selected_option': selected,
            'is_correct': is_correct
        })

    incorrect_count = total_questions - correct_count
    percentage = round((correct_count / total_questions * 100), 1) if total_questions > 0 else 0.0

    quiz = conn.execute("SELECT passing_score, course_id FROM quizzes WHERE id = ?", (quiz_id,)).fetchone()
    passing_score = quiz['passing_score'] if quiz else 70
    passed = 1 if percentage >= passing_score else 0

    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO quiz_attempts (user_id, quiz_id, score, total_questions, correct_count, incorrect_count, percentage, passed, time_taken_seconds)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, quiz_id, correct_count, total_questions, correct_count, incorrect_count, percentage, passed, time_taken_seconds))
    attempt_id = cursor.lastrowid

    # Store individual answers for detailed review
    for ans in evaluated_answers:
        cursor.execute('''
        INSERT INTO quiz_attempt_answers (attempt_id, question_id, selected_option, is_correct)
        VALUES (?, ?, ?, ?)
        ''', (attempt_id, ans['question_id'], ans['selected_option'], ans['is_correct']))

    conn.commit()
    conn.close()

    # Trigger badges check (e.g. 100% quiz score)
    check_and_award_badges(user_id)

    return attempt_id

def get_quiz_attempt_result(attempt_id, user_id=None):
    conn = get_db_connection()
    query = '''
    SELECT qa.*, q.title as quiz_title, q.passing_score, q.time_limit_minutes,
           c.title as course_title, c.slug as course_slug, c.id as course_id
    FROM quiz_attempts qa
    JOIN quizzes q ON qa.quiz_id = q.id
    JOIN courses c ON q.course_id = c.id
    WHERE qa.id = ?
    '''
    params = [attempt_id]
    if user_id:
        query += " AND qa.user_id = ?"
        params.append(user_id)

    attempt = conn.execute(query, params).fetchone()
    if not attempt:
        conn.close()
        return None, None

    # Retrieve answers with questions and explanations
    answers = conn.execute('''
    SELECT qaa.*, qq.question_text, qq.code_snippet, qq.option_a, qq.option_b, qq.option_c, qq.option_d,
           qq.correct_option, qq.explanation, qq.order_num
    FROM quiz_attempt_answers qaa
    JOIN quiz_questions qq ON qaa.question_id = qq.id
    WHERE qaa.attempt_id = ?
    ORDER BY qq.order_num ASC, qq.id ASC
    ''', (attempt_id,)).fetchall()

    conn.close()
    return attempt, answers

# ----------------- Smart Revision (Bookmarks, Notes, Mistakes) -----------------

def get_user_revision_data(user_id):
    conn = get_db_connection()

    bookmarks = conn.execute('''
    SELECT bm.*, l.title as lesson_title, l.id as lesson_id, c.title as course_title, c.slug as course_slug
    FROM bookmarks bm
    JOIN lessons l ON bm.lesson_id = l.id
    JOIN courses c ON l.course_id = c.id
    WHERE bm.user_id = ?
    ORDER BY bm.created_at DESC
    ''', (user_id,)).fetchall()

    notes = conn.execute('''
    SELECT sn.*, l.title as lesson_title, l.id as lesson_id, c.title as course_title, c.slug as course_slug
    FROM student_notes sn
    JOIN lessons l ON sn.lesson_id = l.id
    JOIN courses c ON l.course_id = c.id
    WHERE sn.user_id = ?
    ORDER BY sn.updated_at DESC
    ''', (user_id,)).fetchall()

    # Find unique questions the user got wrong in their most recent attempts
    incorrect_questions = conn.execute('''
    SELECT DISTINCT qq.id as question_id, qq.question_text, qq.code_snippet,
           qq.option_a, qq.option_b, qq.option_c, qq.option_d, qq.correct_option, qq.explanation,
           q.title as quiz_title, c.title as course_title, c.slug as course_slug
    FROM quiz_attempt_answers qaa
    JOIN quiz_attempts qa ON qaa.attempt_id = qa.id
    JOIN quiz_questions qq ON qaa.question_id = qq.id
    JOIN quizzes q ON qa.quiz_id = q.id
    JOIN courses c ON q.course_id = c.id
    WHERE qa.user_id = ? AND qaa.is_correct = 0
    ORDER BY qa.completed_at DESC
    LIMIT 15
    ''', (user_id,)).fetchall()

    conn.close()
    return {
        'bookmarks': bookmarks,
        'notes': notes,
        'incorrect_questions': incorrect_questions
    }

# ----------------- Badges & Rewards -----------------

def check_and_award_badges(user_id):
    conn = get_db_connection()

    # 1. First step: completed at least 1 lesson
    completed_count = conn.execute("SELECT COUNT(*) FROM lesson_progress WHERE user_id = ?", (user_id,)).fetchone()[0]
    if completed_count >= 1:
        award_badge_if_not_present(conn, user_id, 'FIRST_STEP')

    # 2. Quiz Ace: 100% on any quiz
    ace_count = conn.execute("SELECT COUNT(*) FROM quiz_attempts WHERE user_id = ? AND percentage >= 100.0", (user_id,)).fetchone()[0]
    if ace_count >= 1:
        award_badge_if_not_present(conn, user_id, 'QUIZ_ACE')

    # 3. Scholar Mind: saved 3+ notes
    notes_count = conn.execute("SELECT COUNT(*) FROM student_notes WHERE user_id = ?", (user_id,)).fetchone()[0]
    if notes_count >= 3:
        award_badge_if_not_present(conn, user_id, 'NOTE_TAKER')

    # 4. Consistency Master: streak >= 3
    user = conn.execute("SELECT streak_count FROM users WHERE id = ?", (user_id,)).fetchone()
    if user and user['streak_count'] >= 3:
        award_badge_if_not_present(conn, user_id, 'STREAK_3')

    # 5. Course-specific badges
    py_course = conn.execute("SELECT id FROM courses WHERE slug = 'python'").fetchone()
    if py_course:
        py_done = conn.execute('''
        SELECT COUNT(*) FROM lesson_progress WHERE user_id = ? AND course_id = ?
        ''', (user_id, py_course['id'])).fetchone()[0]
        if py_done >= 1:
            award_badge_if_not_present(conn, user_id, 'PYTHON_EXPLORER')

    conn.commit()
    conn.close()

def award_badge_if_not_present(conn, user_id, badge_code):
    badge = conn.execute("SELECT id FROM badges WHERE code = ?", (badge_code,)).fetchone()
    if badge:
        conn.execute('''
        INSERT OR IGNORE INTO user_badges (user_id, badge_id) VALUES (?, ?)
        ''', (user_id, badge['id']))

# ----------------- Certificates -----------------

def check_certificate_eligibility(user_id, course_id):
    conn = get_db_connection()
    # Check total vs completed lessons
    total_lessons = conn.execute("SELECT COUNT(*) FROM lessons WHERE course_id = ?", (course_id,)).fetchone()[0]
    completed_lessons = conn.execute('''
    SELECT COUNT(*) FROM lesson_progress WHERE user_id = ? AND course_id = ?
    ''', (user_id, course_id)).fetchone()[0]

    # Check if passed the course quiz
    quiz = conn.execute("SELECT id, passing_score FROM quizzes WHERE course_id = ?", (course_id,)).fetchone()
    quiz_passed = False
    if quiz:
        pass_attempt = conn.execute('''
        SELECT id FROM quiz_attempts 
        WHERE user_id = ? AND quiz_id = ? AND passed = 1
        ''', (user_id, quiz['id'])).fetchone()
        quiz_passed = (pass_attempt is not None)

    # Check existing certificate
    cert = conn.execute("SELECT * FROM certificates WHERE user_id = ? AND course_id = ?", (user_id, course_id)).fetchone()

    is_eligible = (total_lessons > 0 and completed_lessons >= total_lessons and quiz_passed)

    conn.close()
    return is_eligible, completed_lessons, total_lessons, quiz_passed, cert

def generate_course_certificate(user_id, course_id):
    conn = get_db_connection()
    # Check if already generated
    cert = conn.execute("SELECT * FROM certificates WHERE user_id = ? AND course_id = ?", (user_id, course_id)).fetchone()
    if cert:
        conn.close()
        return cert['certificate_code']

    course = conn.execute("SELECT slug FROM courses WHERE id = ?", (course_id,)).fetchone()
    slug_code = course['slug'][:3].upper() if course else "DEV"
    rand_suffix = uuid.uuid4().hex[:6].upper()
    cert_code = f"CERT-2026-{slug_code}-{rand_suffix}"

    conn.execute('''
    INSERT INTO certificates (user_id, course_id, certificate_code, grade)
    VALUES (?, ?, ?, 'Excellence')
    ''', (user_id, course_id, cert_code))

    award_badge_if_not_present(conn, user_id, 'CERTIFIED_GRAD')
    conn.commit()
    conn.close()
    return cert_code

def get_certificate_details(cert_code):
    conn = get_db_connection()
    cert = conn.execute('''
    SELECT cert.*, u.full_name as student_name, u.email as student_email,
           c.title as course_title, c.slug as course_slug, c.estimated_hours
    FROM certificates cert
    JOIN users u ON cert.user_id = u.id
    JOIN courses c ON cert.course_id = c.id
    WHERE cert.certificate_code = ?
    ''', (cert_code.strip().upper(),)).fetchone()
    conn.close()
    return cert

def get_user_certificates(user_id):
    conn = get_db_connection()
    certs = conn.execute('''
    SELECT cert.*, c.title as course_title, c.slug as course_slug, c.badge_color, c.icon as course_icon
    FROM certificates cert
    JOIN courses c ON cert.course_id = c.id
    WHERE cert.user_id = ?
    ORDER BY cert.issue_date DESC
    ''', (user_id,)).fetchall()
    conn.close()
    return certs

# ----------------- Personalized Recommendations -----------------

def get_personalized_recommendations(user_id):
    """
    Computes intelligent next-step recommendations based on:
    1. Unfinished active course lesson
    2. Unattempted quiz for an enrolled course
    3. Weak topics/quizzes where score was < passing
    4. Next recommended course in same or complementary category
    """
    conn = get_db_connection()

    # 1. Continue active lesson
    active_enrollment = conn.execute('''
    SELECT e.*, c.title as course_title, c.slug as course_slug,
           l.title as lesson_title, l.id as lesson_id
    FROM enrollments e
    JOIN courses c ON e.course_id = c.id
    LEFT JOIN lessons l ON e.last_accessed_lesson_id = l.id
    WHERE e.user_id = ? AND e.progress_percent < 100.0
    ORDER BY e.enrolled_at DESC
    LIMIT 1
    ''', (user_id,)).fetchone()

    # 2. Low-scoring quiz needing retake
    retake_quiz = conn.execute('''
    SELECT qa.*, q.title as quiz_title, q.id as quiz_id, c.title as course_title, c.slug as course_slug
    FROM quiz_attempts qa
    JOIN quizzes q ON qa.quiz_id = q.id
    JOIN courses c ON q.course_id = c.id
    WHERE qa.user_id = ? AND qa.passed = 0
    ORDER BY qa.completed_at DESC
    LIMIT 1
    ''', (user_id,)).fetchone()

    # 3. Next course suggestion (not yet enrolled)
    suggested_course = conn.execute('''
    SELECT c.*, cat.name as category_name
    FROM courses c
    LEFT JOIN categories cat ON c.category_id = cat.id
    WHERE c.id NOT IN (SELECT course_id FROM enrollments WHERE user_id = ?)
    ORDER BY c.is_popular DESC, c.id ASC
    LIMIT 1
    ''', (user_id,)).fetchone()

    conn.close()
    return {
        'active_enrollment': active_enrollment,
        'retake_quiz': retake_quiz,
        'suggested_course': suggested_course
    }

# ----------------- Admin Analytics & CRUD -----------------

def get_admin_dashboard_stats():
    conn = get_db_connection()
    total_users = conn.execute("SELECT COUNT(*) FROM users WHERE role = 'student'").fetchone()[0]
    total_courses = conn.execute("SELECT COUNT(*) FROM courses").fetchone()[0]
    total_lessons = conn.execute("SELECT COUNT(*) FROM lessons").fetchone()[0]
    total_quizzes = conn.execute("SELECT COUNT(*) FROM quizzes").fetchone()[0]
    total_attempts = conn.execute("SELECT COUNT(*) FROM quiz_attempts").fetchone()[0]
    total_certs = conn.execute("SELECT COUNT(*) FROM certificates").fetchone()[0]

    recent_users = conn.execute('''
    SELECT u.id, u.full_name, u.email, u.created_at, u.streak_count,
           (SELECT COUNT(*) FROM enrollments WHERE user_id = u.id) as enrolled_count,
           (SELECT COUNT(*) FROM quiz_attempts WHERE user_id = u.id) as quiz_count
    FROM users u
    WHERE u.role = 'student'
    ORDER BY u.created_at DESC
    LIMIT 8
    ''').fetchall()

    recent_attempts = conn.execute('''
    SELECT qa.*, u.full_name as student_name, q.title as quiz_title, c.title as course_title
    FROM quiz_attempts qa
    JOIN users u ON qa.user_id = u.id
    JOIN quizzes q ON qa.quiz_id = q.id
    JOIN courses c ON q.course_id = c.id
    ORDER BY qa.completed_at DESC
    LIMIT 8
    ''').fetchall()

    courses_summary = conn.execute('''
    SELECT c.id, c.title, c.difficulty, c.is_popular, c.is_published,
           (SELECT COUNT(*) FROM lessons WHERE course_id = c.id) as lesson_count,
           (SELECT COUNT(*) FROM enrollments WHERE course_id = c.id) as student_count,
           (SELECT COUNT(*) FROM certificates WHERE course_id = c.id) as cert_count
    FROM courses c
    ORDER BY c.id ASC
    ''').fetchall()

    conn.close()
    return {
        'total_users': total_users,
        'total_courses': total_courses,
        'total_lessons': total_lessons,
        'total_quizzes': total_quizzes,
        'total_attempts': total_attempts,
        'total_certs': total_certs,
        'recent_users': recent_users,
        'recent_attempts': recent_attempts,
        'courses_summary': courses_summary
    }

def add_contact_message(name, email, subject, message):
    conn = get_db_connection()
    conn.execute('''
    INSERT INTO contact_messages (name, email, subject, message)
    VALUES (?, ?, ?, ?)
    ''', (name.strip(), email.strip(), subject.strip(), message.strip()))
    conn.commit()
    conn.close()
