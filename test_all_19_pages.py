import unittest
from app import app
import models

class Comprehensive19PagesTest(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_all_19_pages_rendered(self):
        """Verify each of the exact 19 pages from the requirement specification."""
        
        # 1. Home
        res = self.client.get('/')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Learn to Code', res.data)

        # 2. Login
        res = self.client.get('/login')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Welcome Back', res.data)

        # 3. Registration
        res = self.client.get('/register')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Create Student Account', res.data)

        # 4. Course Catalog
        res = self.client.get('/courses')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Explore All Courses', res.data)

        # 5. Course Details (Python)
        res = self.client.get('/courses/python')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Python Programming', res.data)

        # 6. Lesson Viewer
        conn = models.get_db_connection()
        lesson = conn.execute("SELECT id, course_id FROM lessons WHERE course_id = (SELECT id FROM courses WHERE slug = 'python') LIMIT 1").fetchone()
        conn.close()
        res = self.client.get(f'/courses/python/lessons/{lesson["id"]}')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Example Code', res.data)

        # Log in as demo student
        self.client.post('/login', data={'email': 'student@elearning.com', 'password': 'Student@123'})

        # 7. Quiz Instructions
        conn = models.get_db_connection()
        quiz = conn.execute("SELECT id FROM quizzes LIMIT 1").fetchone()
        conn.close()
        res = self.client.get(f'/quizzes/{quiz["id"]}/instructions')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Instructions', res.data)

        # 8. Quiz Interface
        res = self.client.get(f'/quizzes/{quiz["id"]}/take')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Question 1', res.data)

        # 9. Quiz Results (from previous attempt)
        conn = models.get_db_connection()
        attempt = conn.execute("SELECT id FROM quiz_attempts WHERE user_id = 2 LIMIT 1").fetchone()
        conn.close()
        res = self.client.get(f'/quizzes/results/{attempt["id"]}')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Results', res.data)

        # 10. Student Dashboard
        res = self.client.get('/dashboard')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Welcome back', res.data)

        # 11. My Learning
        res = self.client.get('/my-learning')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'My Learning', res.data)

        # 12. Bookmarks and Notes
        res = self.client.get('/saved-notes')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Smart Revision', res.data)

        # 13. Coding Playground
        res = self.client.get('/playground')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Code Playground', res.data)

        # 14. Certificates & Verification
        # Generate a certificate for testing view
        cert_code = models.generate_course_certificate(2, 1)
        res = self.client.get('/certificates')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'My Course Certificates', res.data)

        res_view = self.client.get(f'/certificates/{cert_code}')
        self.assertEqual(res_view.status_code, 200)
        self.assertIn(b'Certificate of Completion', res_view.data)

        # 15. AI Learning Assistant
        res = self.client.get('/ai-assistant')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'EduBot', res.data)

        # 16. About Us
        res = self.client.get('/about')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'About E-Learning Platform', res.data)

        # 17. Contact Us
        res = self.client.get('/contact')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Contact Support', res.data)

        # 18. Admin Dashboard (login as admin)
        self.client.get('/logout')
        self.client.post('/login', data={'email': 'admin@elearning.com', 'password': 'Admin@123'})
        res = self.client.get('/admin')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Administrator Portal', res.data)

        # 19. Privacy
        res = self.client.get('/privacy')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Privacy Policy', res.data)

    def test_all_8_courses_exist(self):
        """Verify that all 8 required courses are present with lessons and quizzes."""
        required_slugs = [
            'python',
            'c-programming',
            'cpp-programming',
            'java-programming',
            'html-css',
            'javascript',
            'sql',
            'dsa'
        ]
        conn = models.get_db_connection()
        for slug in required_slugs:
            course = conn.execute("SELECT id, title FROM courses WHERE slug = ?", (slug,)).fetchone()
            self.assertIsNotNone(course, f"Course with slug '{slug}' is missing!")
            
            # Check modules
            mods = conn.execute("SELECT COUNT(*) FROM modules WHERE course_id = ?", (course['id'],)).fetchone()[0]
            self.assertGreater(mods, 0, f"Course '{slug}' has no modules!")

            # Check lessons
            lessons = conn.execute("SELECT COUNT(*) FROM lessons WHERE course_id = ?", (course['id'],)).fetchone()[0]
            self.assertGreater(lessons, 0, f"Course '{slug}' has no lessons!")

            # Check quiz and at least 10 questions
            quiz = conn.execute("SELECT id FROM quizzes WHERE course_id = ?", (course['id'],)).fetchone()
            self.assertIsNotNone(quiz, f"Course '{slug}' has no quiz!")

            q_count = conn.execute("SELECT COUNT(*) FROM quiz_questions WHERE quiz_id = ?", (quiz['id'],)).fetchone()[0]
            self.assertGreaterEqual(q_count, 10, f"Course '{slug}' quiz has fewer than 10 questions! Found: {q_count}")
        conn.close()

if __name__ == '__main__':
    unittest.main()
