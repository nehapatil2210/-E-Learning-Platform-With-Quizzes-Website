# E-Learning Platform with Quizzes

A complete, modern, interactive, and responsive educational web application designed for academic computer science learning, hands-on programming practice, and automated assessment.

---

## 🌟 Key Highlights & Architectural Features

### 1. Educational Structure (Inspired by W3Schools)
- **8 Core Subjects Fully Implemented:**
  1. Python Programming
  2. C Programming
  3. C++ Programming
  4. Java Programming
  5. HTML & CSS
  6. JavaScript (ES6+)
  7. SQL (Structured Query Language)
  8. Data Structures & Algorithms (DSA)
- **Modular Curriculum:** Structured into modules, bite-sized lessons, syntax reference blocks, practical code examples with expected outputs, and practice challenges.
- **Collapsible Course Navigation Sidebar:** Interactive drawer with active lesson tracking, completion checkmarks, and breadcrumbs.

### 2. Interactive Quiz System
- **80+ High-Quality Assessment Questions:** At least 10 multiple-choice questions for each course with 4 choices and 1 single correct answer.
- **Timed Countdown Mode:** Real-time countdown timer with urgent visual warning.
- **Interactive Question Palette:** Direct jump to questions, marked answered state, and unanswered warnings.
- **Confirmation Modal:** Prevents premature submissions and displays remaining unanswered questions.
- **Instant Result Evaluation & Review:** Automatic score calculation, percentage, pass/fail status (passing grade: 70%), time taken, and comprehensive explanations for every question.
- **No Answer Leakage:** Answer options and explanations are strictly withheld until submission.

### 3. Student Dashboard & Learning Analytics
- **Personalized Welcome & Streak Counter:** Real-time tracking of consecutive active learning days.
- **Real-Time Dynamic Statistics:** Total enrolled courses, completed courses, in-progress courses, total quizzes attempted, average quiz score, and overall learning progress % (all computed from SQLite database records).
- **Interactive Data Visualizations:** Chart.js integration showing quiz score performance trends and curriculum progress by category.
- **Continue Learning Feature:** One-click resume to jump directly to the student's last active lesson.
- **Earned Badges & Gamification:** Milestones awarded for first lessons, 100% quiz scores, note-taking, and course completions.

### 4. Interactive Coding Playground
- **Multi-Language Support:** Python, JavaScript, HTML/CSS, SQL, C, C++, and Java.
- **Sandboxed Execution:** Python runs in a restricted subprocess with strict 3.5s timeout, memory bounds, and filtered dangerous system calls (`os`, `subprocess`, `socket`, `open`).
- **Live HTML/CSS Preview:** Real-time sandboxed iframe preview with immediate DOM rendering.
- **Practice Challenges:** Pre-built coding challenges with automatic starter code and test cases.
- **Sample Programs:** One-click sample programs and quick reset functionality.

### 5. Unique Advanced Features
- **Personalized Learning Recommendations:** Dynamically suggests next lessons, quiz retakes for failed assessments, and complementary course enrollments.
- **EduBot AI Learning Assistant:** Educational conversational engine explaining syntax, algorithms, debugging errors, and suggesting next steps.
- **Smart Revision Center:** Collects all bookmarked lessons, personal study notes, and questions previously answered incorrectly on quizzes for targeted revision.
- **Official Verifiable Certificates:** Automatically unlocked when all lessons in a course are marked complete and the final quiz is passed. Generates a unique verification code (`CERT-2026-PY-XXXXXX`), grade, and print-ready stylesheet for saving as PDF.

### 6. Role-Based Admin Management Console
- Protected by `@admin_required` authorization check.
- High-level platform metrics: registered students, courses, lessons, quizzes, attempts, and certificates.
- Full Course CRUD & Lesson organization.
- Student accounts overview with streaks and activity history.

---

## 🗄️ Database Architecture (SQLite3)

The application stores all data persistently in `elearning.db`:
- `users`: Credentials, PBKDF2 password hashes, roles (`student`, `admin`), streak counts, last active date.
- `categories`: Course subject domains.
- `courses`: Metadata, difficulty levels, estimated hours, icons.
- `modules` & `lessons`: Hierarchical curriculum, syntax examples, expected outputs, practice challenges.
- `enrollments`: Student course enrollment, progress percent, last accessed lesson.
- `lesson_progress`: Completed lesson tracking.
- `quizzes` & `quiz_questions`: Topic assessments, multiple choice options, correct keys, explanations.
- `quiz_attempts` & `quiz_attempt_answers`: Historical submission logs, scores, review records.
- `bookmarks`: Saved lessons for quick access.
- `student_notes`: Personal study summaries saved per lesson.
- `badges` & `user_badges`: Gamified achievement awards.
- `certificates`: Official completion records with unique verification IDs.
- `contact_messages`: Inquiries and student feedback.

---

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.10+ (tested with Python 3.14)
- Flask 3.x, Werkzeug, Jinja2

### Installation & Launch

1. **Clone or Navigate to the Project Directory:**
   ```bash
   cd "E learning platform with quizzes new"
   ```

2. **Initialize and Seed the Database:**
   ```bash
   python seed_data.py
   ```
   *(This initializes all tables and seeds 8 full courses, topic lessons, 80+ quiz questions, badges, and demo accounts).*

3. **Run the Automated Test Suite:**
   ```bash
   python test_all_19_pages.py
   ```

4. **Start the Web Server:**
   ```bash
   python app.py
   ```
   Open your browser and navigate to: **`http://127.0.0.1:5000`**

---

## 🔑 Demo Login Accounts

| Role | Email | Password | Access Capabilities |
| :--- | :--- | :--- | :--- |
| **Student** | `student@elearning.com` | `Student@123` | Enrolled in Python, quizzes, dashboard, notes, certificates |
| **Admin** | `admin@elearning.com` | `Admin@123` | Full access to Admin Portal, Course & Lesson CRUD, User review |

*(You can also register a brand new student account on the `/register` page with any email).*

---

## 📑 Complete Page Directory (All 19 Specified Pages)

1. **Home:** `/`
2. **Login:** `/login`
3. **Registration:** `/register`
4. **Course Catalog:** `/courses`
5. **Course Details:** `/courses/<course_slug>`
6. **Lesson Viewer:** `/courses/<course_slug>/lessons/<int:lesson_id>`
7. **Quiz Instructions:** `/quizzes/<int:quiz_id>/instructions`
8. **Quiz Interface:** `/quizzes/<int:quiz_id>/take`
9. **Quiz Results:** `/quizzes/results/<int:attempt_id>`
10. **Student Dashboard:** `/dashboard`
11. **My Learning:** `/my-learning`
12. **Bookmarks and Notes:** `/saved-notes`
13. **Coding Playground:** `/playground`
14. **Certificates & Verification:** `/certificates` and `/certificates/<cert_code>`
15. **AI Learning Assistant:** `/ai-assistant`
16. **About Us:** `/about`
17. **Contact Us:** `/contact`
18. **Admin Dashboard:** `/admin` (plus `/admin/courses`, `/admin/lessons`, `/admin/quizzes`, `/admin/users`)
19. **Privacy Policy:** `/privacy`
