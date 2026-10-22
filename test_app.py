import unittest
from app import app
import models
from database import get_db_connection

class ELearningPlatformTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_01_public_routes(self):
        """Test all public informative and catalog pages."""
        public_urls = [
            '/',
            '/courses',
            '/courses/python',
            '/quizzes',
            '/playground',
            '/ai-assistant',
            '/about',
            '/contact',
            '/privacy',
            '/login',
            '/register'
        ]
        for url in public_urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200, f"URL {url} failed with status {response.status_code}")

    def test_02_authentication_and_dashboard(self):
        """Test student login and dashboard access."""
        # Test login with demo student
        resp = self.client.post('/login', data={
            'email': 'student@elearning.com',
            'password': 'Student@123'
        }, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'Alex Morgan', resp.data)

        # Test authenticated student dashboard
        dash_resp = self.client.get('/dashboard')
        self.assertEqual(dash_resp.status_code, 200)
        self.assertIn(b'Enrolled Courses', dash_resp.data)

        # Test My Learning
        my_learn_resp = self.client.get('/my-learning')
        self.assertEqual(my_learn_resp.status_code, 200)

        # Test Saved Notes (Smart Revision)
        notes_resp = self.client.get('/saved-notes')
        self.assertEqual(notes_resp.status_code, 200)

        # Test Certificates
        certs_resp = self.client.get('/certificates')
        self.assertEqual(certs_resp.status_code, 200)

    def test_03_lesson_viewer_and_ajax(self):
        """Test viewing a lesson, toggling completion, bookmarks, and notes."""
        # Log in first
        self.client.post('/login', data={'email': 'student@elearning.com', 'password': 'Student@123'})

        # Find python course first lesson
        conn = models.get_db_connection()
        lesson = conn.execute("SELECT l.id, c.slug, c.id as course_id FROM lessons l JOIN courses c ON l.course_id = c.id WHERE c.slug = 'python' LIMIT 1").fetchone()
        conn.close()

        lesson_id = lesson['id']
        course_id = lesson['course_id']
        slug = lesson['slug']

        # View lesson page
        view_resp = self.client.get(f'/courses/{slug}/lessons/{lesson_id}')
        self.assertEqual(view_resp.status_code, 200)
        self.assertIn(b'Example Code', view_resp.data)

        # Test AJAX lesson completion toggle
        comp_resp = self.client.post('/api/toggle-lesson-complete', json={
            'lesson_id': lesson_id,
            'course_id': course_id
        })
        self.assertEqual(comp_resp.status_code, 200)
        data = comp_resp.get_json()
        self.assertTrue(data['success'])

        # Test AJAX bookmark toggle
        bm_resp = self.client.post('/api/toggle-bookmark', json={'lesson_id': lesson_id})
        self.assertEqual(bm_resp.status_code, 200)
        self.assertTrue(bm_resp.get_json()['success'])

        # Test AJAX note save
        note_resp = self.client.post('/api/save-note', json={
            'lesson_id': lesson_id,
            'note_text': 'Variables and indentation are foundational in Python.'
        })
        self.assertEqual(note_resp.status_code, 200)
        self.assertTrue(note_resp.get_json()['success'])

    def test_04_quiz_system(self):
        """Test quiz instructions, taking, submission, and result display."""
        self.client.post('/login', data={'email': 'student@elearning.com', 'password': 'Student@123'})

        # Get Python quiz
        conn = models.get_db_connection()
        quiz = conn.execute("SELECT id FROM quizzes WHERE course_id = (SELECT id FROM courses WHERE slug = 'python')").fetchone()
        quiz_id = quiz['id']
        questions = conn.execute("SELECT id, correct_option FROM quiz_questions WHERE quiz_id = ?", (quiz_id,)).fetchall()
        conn.close()

        # Check Instructions
        inst_resp = self.client.get(f'/quizzes/{quiz_id}/instructions')
        self.assertEqual(inst_resp.status_code, 200)

        # Check Take page
        take_resp = self.client.get(f'/quizzes/{quiz_id}/take')
        self.assertEqual(take_resp.status_code, 200)

        # Submit quiz answers (all correct)
        form_data = {'time_taken_seconds': 120}
        for q in questions:
            form_data[f"q_{q['id']}"] = q['correct_option']

        sub_resp = self.client.post(f'/quizzes/{quiz_id}/take', data=form_data, follow_redirects=True)
        self.assertEqual(sub_resp.status_code, 200)
        self.assertIn(b'100%', sub_resp.data)
        self.assertIn(b'PASSED', sub_resp.data)

    def test_05_code_execution_api(self):
        """Test sandbox code execution endpoint."""
        # 1. Safe Python code execution
        code = "total = sum([10, 20, 30])\nprint(f'Sum: {total}')"
        resp = self.client.post('/api/execute-code', json={'code': code, 'language': 'python'})
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data['success'])
        self.assertIn("Sum: 60", data['output'])

        # 2. Blocked unsafe operation check
        unsafe_code = "import os\nprint(os.listdir('.'))"
        resp2 = self.client.post('/api/execute-code', json={'code': unsafe_code, 'language': 'python'})
        self.assertEqual(resp2.status_code, 200)
        data2 = resp2.get_json()
        self.assertFalse(data2['success'])
        self.assertIn("Security Warning", data2['output'])

    def test_06_ai_chat_api(self):
        """Test AI assistant chat query."""
        resp = self.client.post('/api/ai-chat', json={'query': 'Explain Big O complexity'})
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertIn('message', data)
        self.assertIn('Big O', data['message'])

    def test_07_admin_role_security(self):
        """Verify student cannot access admin routes and admin can."""
        # Unauthenticated access
        unauth_resp = self.client.get('/admin', follow_redirects=False)
        self.assertEqual(unauth_resp.status_code, 302)

        # Student access
        self.client.post('/login', data={'email': 'student@elearning.com', 'password': 'Student@123'})
        student_resp = self.client.get('/admin', follow_redirects=False)
        self.assertEqual(student_resp.status_code, 302) # Redirected away with access denied

        # Admin access
        self.client.get('/logout')
        admin_login = self.client.post('/login', data={'email': 'admin@elearning.com', 'password': 'Admin@123'}, follow_redirects=True)
        self.assertEqual(admin_login.status_code, 200)

        admin_dash = self.client.get('/admin')
        self.assertEqual(admin_dash.status_code, 200)
        self.assertIn(b'Administrator Portal', admin_dash.data)

        admin_courses = self.client.get('/admin/courses')
        self.assertEqual(admin_courses.status_code, 200)

        admin_lessons = self.client.get('/admin/lessons')
        self.assertEqual(admin_lessons.status_code, 200)

        admin_users = self.client.get('/admin/users')
        self.assertEqual(admin_users.status_code, 200)

if __name__ == '__main__':
    unittest.main()
