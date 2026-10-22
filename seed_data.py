import sqlite3
from werkzeug.security import generate_password_hash
from database import get_db_connection, init_db

def seed_database():
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if database already has courses
    cursor.execute("SELECT COUNT(*) FROM courses")
    if cursor.fetchone()[0] > 0:
        print("Database already contains data. Skipping re-seed.")
        conn.close()
        return

    print("Seeding database with courses, lessons, quizzes, questions, and badges...")

    # 1. Users
    admin_pw = generate_password_hash("Admin@123")
    student_pw = generate_password_hash("Student@123")

    cursor.execute('''
    INSERT INTO users (full_name, email, password_hash, role, streak_count, last_active_date)
    VALUES (?, ?, ?, ?, ?, date('now'))
    ''', ('System Administrator', 'admin@elearning.com', admin_pw, 'admin', 5))

    cursor.execute('''
    INSERT INTO users (full_name, email, password_hash, role, streak_count, last_active_date)
    VALUES (?, ?, ?, ?, ?, date('now'))
    ''', ('Alex Morgan', 'student@elearning.com', student_pw, 'student', 3))

    # 2. Categories
    categories = [
        ('Programming Languages', 'programming-languages', 'Core compiled and interpreted programming languages for software development.', 'code'),
        ('Web Development', 'web-development', 'Modern technologies for building responsive and dynamic web applications.', 'globe'),
        ('Databases', 'databases', 'Relational database management, querying, and data modeling.', 'database'),
        ('Computer Science', 'computer-science', 'Fundamental computer science concepts, algorithms, and data structures.', 'cpu')
    ]

    cursor.executemany('''
    INSERT INTO categories (name, slug, description, icon) VALUES (?, ?, ?, ?)
    ''', categories)

    # 3. Badges
    badges = [
        ('FIRST_STEP', 'First Step', 'Completed your very first lesson.', 'compass', 'general'),
        ('QUIZ_ACE', 'Quiz Champion', 'Scored 100% on any course quiz.', 'award', 'quiz'),
        ('STREAK_3', 'Consistency Master', 'Maintained a 3-day active learning streak.', 'flame', 'streak'),
        ('PYTHON_EXPLORER', 'Python Explorer', 'Enrolled and completed the first module of Python.', 'terminal', 'course'),
        ('WEB_CRAFTER', 'Web Crafter', 'Successfully completed HTML & CSS basics.', 'layout', 'course'),
        ('ALGO_WARRIOR', 'Algorithm Warrior', 'Finished Data Structures & Algorithms essentials.', 'git-merge', 'course'),
        ('CERTIFIED_GRAD', 'Certified Achiever', 'Earned your first official course certificate.', 'shield-check', 'certificate'),
        ('NOTE_TAKER', 'Scholar Mind', 'Saved 3 or more personal revision notes.', 'bookmark', 'learning')
    ]

    cursor.executemany('''
    INSERT INTO badges (code, title, description, icon, category) VALUES (?, ?, ?, ?, ?)
    ''', badges)

    # 4. Courses definition
    courses_data = [
        {
            'title': 'Python Programming',
            'slug': 'python',
            'category_id': 1,
            'description': 'Master Python from syntax basics to object-oriented programming, data structures, and practical application building. Python is the world’s most versatile and popular language.',
            'short_desc': 'Learn Python programming from scratch with interactive syntax, hands-on examples, and quizzes.',
            'difficulty': 'Beginner',
            'estimated_hours': 14,
            'icon': 'python',
            'badge_color': '#10b981',
            'is_popular': 1,
            'modules': [
                {
                    'title': 'Python Fundamentals',
                    'lessons': [
                        {
                            'title': 'Introduction to Python & Syntax',
                            'slug': 'python-intro',
                            'content': '''<p><strong>Python</strong> is a high-level, interpreted, general-purpose programming language known for its clear, clean, and highly readable syntax.</p>
<h4>Why Learn Python?</h4>
<ul>
<li>Simple, readable syntax resembling natural English.</li>
<li>Widely used in Web Development, Artificial Intelligence, Data Science, and Automation.</li>
<li>Massive community and extensive collection of standard libraries.</li>
</ul>
<h4>Python Syntax Rules</h4>
<p>Unlike languages like C++ or Java that use curly braces <code>{}</code> to delimit code blocks, Python uses <strong>indentation</strong> (typically 4 spaces) to define scope.</p>''',
                            'code': '''# Welcome to Python!
print("Hello, World!")

# Variables and simple math
name = "Student"
score = 95
print(f"Welcome {name}! Your score is {score}.")''',
                            'output': '''Hello, World!
Welcome Student! Your score is 95.''',
                            'task': 'Write a Python program that prints your name and your favorite programming language using formatted strings.'
                        },
                        {
                            'title': 'Variables, Data Types & Operators',
                            'slug': 'python-variables',
                            'content': '''<p>In Python, variables are created when you assign a value to them. Python is <em>dynamically typed</em>, meaning you do not need to declare variable types explicitly.</p>
<h4>Built-in Core Data Types:</h4>
<ul>
<li><code>int</code>: Integer numbers (e.g. <code>42</code>, <code>-7</code>)</li>
<li><code>float</code>: Floating-point decimals (e.g. <code>3.1415</code>)</li>
<li><code>str</code>: String text (e.g. <code>"Python"</code>)</li>
<li><code>bool</code>: Boolean values (<code>True</code> or <code>False</code>)</li>
</ul>''',
                            'code': '''# Data types demonstration
item_price = 19.99
quantity = 3
item_name = "Notebook"
is_in_stock = True

total = item_price * quantity
print(f"Total for {quantity} {item_name}s: ${total:.2f}")
print("Type of total:", type(total))''',
                            'output': '''Total for 3 Notebooks: $59.97
Type of total: <class 'float'>''',
                            'task': 'Declare three variables: base, height, and calculate the area of a triangle (0.5 * base * height).'
                        },
                        {
                            'title': 'Control Flow: Conditionals & Loops',
                            'slug': 'python-control-flow',
                            'content': '''<p>Control flow structures allow your programs to make decisions and repeat execution blocks based on conditions.</p>
<h4>Conditional Statements</h4>
<p>Python uses <code>if</code>, <code>elif</code>, and <code>else</code> keywords.</p>
<h4>Loops</h4>
<p>Use <code>for</code> loops to iterate over collections or sequences, and <code>while</code> loops to repeat as long as a condition evaluates to <code>True</code>.</p>''',
                            'code': '''# Conditional Check
marks = 85
if marks >= 90:
    grade = 'A'
elif marks >= 75:
    grade = 'B'
else:
    grade = 'C'

print(f"Grade: {grade}")

# Iteration
print("Counting down:")
for i in range(3, 0, -1):
    print(f"T-minus {i}")
print("Blast off!")''',
                            'output': '''Grade: B
Counting down:
T-minus 3
T-minus 2
T-minus 1
Blast off!''',
                            'task': 'Create a loop that prints the even numbers from 2 to 20 inclusive.'
                        }
                    ]
                },
                {
                    'title': 'Data Structures & Functions',
                    'lessons': [
                        {
                            'title': 'Functions & Scope',
                            'slug': 'python-functions',
                            'content': '''<p>A <strong>function</strong> is a reusable block of code that executes only when called. Functions help organize code into logical, modular components.</p>
<h4>Syntax</h4>
<pre><code>def function_name(parameters):
    # function body
    return result</code></pre>''',
                            'code': '''def calculate_grade(score):
    """Calculates student letter grade based on numerical score."""
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    return "F"

scores = [92, 78, 85, 64]
for s in scores:
    print(f"Score {s} -> Grade {calculate_grade(s)}")''',
                            'output': '''Score 92 -> Grade A
Score 78 -> Grade C
Score 85 -> Grade B
Score 64 -> Grade F''',
                            'task': 'Write a function named is_prime(n) that returns True if a number is prime, and False otherwise.'
                        },
                        {
                            'title': 'Lists, Tuples, Dictionaries & Sets',
                            'slug': 'python-data-structures',
                            'content': '''<p>Python provides four fundamental collection data types:</p>
<ul>
<li><strong>List</strong>: Ordered, mutable, allows duplicate members (<code>[1, 2, 3]</code>).</li>
<li><strong>Tuple</strong>: Ordered, immutable, allows duplicate members (<code>(1, 2, 3)</code>).</li>
<li><strong>Dictionary</strong>: Key-value pairs, unordered/ordered, mutable, no duplicate keys (<code>{"a": 1}</code>).</li>
<li><strong>Set</strong>: Unordered, mutable, unique elements only (<code>{1, 2, 3}</code>).</li>
</ul>''',
                            'code': '''# List and Dictionary in action
fruits = ["apple", "banana", "cherry"]
fruits.append("orange")

student = {
    "name": "Sarah",
    "course": "Python",
    "completed_lessons": 5
}

print(f"Fruit count: {len(fruits)}")
print(f"Student {student['name']} is learning {student['course']}.")''',
                            'output': '''Fruit count: 4
Student Sarah is learning Python.''',
                            'task': 'Create a dictionary with 3 course names as keys and their credit hours as values. Iterate and print each key-value pair.'
                        }
                    ]
                }
            ],
            'quiz': {
                'title': 'Python Fundamentals & Syntax Quiz',
                'description': 'Assess your knowledge of Python syntax, data types, control flow, collections, and functions.',
                'time_limit': 15,
                'difficulty': 'Beginner',
                'questions': [
                    ('Which symbol is used for single-line comments in Python?', None, '//', '#', '/*', '--', 'B', 'In Python, the # symbol is used to start a single-line comment.'),
                    ('What is the correct file extension for Python files?', None, '.pyt', '.pt', '.py', '.python', 'C', 'Python script files use the .py file extension.'),
                    ('How do you output text to the console in Python 3?', None, 'echo "Hello"', 'console.log("Hello")', 'System.out.println("Hello")', 'print("Hello")', 'D', 'Python uses the built-in print() function to display text on the screen.'),
                    ('What is the output of type(3.14)?', 'print(type(3.14))', '<class "int">', '<class "float">', '<class "double">', '<class "decimal">', 'B', 'Decimal numbers in Python belong to the float data type.'),
                    ('Which of the following is an IMMUTABLE collection in Python?', None, 'List', 'Dictionary', 'Tuple', 'Set', 'C', 'Tuples are immutable; once created, their elements cannot be modified, added, or removed.'),
                    ('What keyword is used to define a function in Python?', None, 'func', 'function', 'define', 'def', 'D', 'The def keyword is used to declare and define functions in Python.'),
                    ('What will len(["a", "b", "c", "d"]) return?', 'items = ["a", "b", "c", "d"]\nprint(len(items))', '3', '4', '5', 'Error', 'B', 'The len() function returns the total number of items in a sequence. Here there are 4 items.'),
                    ('What does the range(1, 5) function produce when converted to a list?', None, '[1, 2, 3, 4, 5]', '[1, 2, 3, 4]', '[0, 1, 2, 3, 4]', '[2, 3, 4, 5]', 'B', 'range(start, stop) generates numbers from start up to, but not including, stop. Thus range(1, 5) produces 1, 2, 3, 4.'),
                    ('How do you insert an item at the end of a list in Python?', None, 'list.add(item)', 'list.insert(item)', 'list.append(item)', 'list.push(item)', 'C', 'The append() method adds an item to the end of a Python list.'),
                    ('Which operator is used for exponentiation (power) in Python?', None, '^', '**', '^^', 'pow() only', 'B', 'The ** operator raises a number to the power of an exponent (e.g., 2 ** 3 = 8).')
                ]
            }
        },
        {
            'title': 'C Programming',
            'slug': 'c-programming',
            'category_id': 1,
            'description': 'Master C, the mother of modern programming languages. Understand low-level memory management, pointers, structures, and efficient systems programming.',
            'short_desc': 'Foundational programming language covering syntax, memory management, pointers, and compilation.',
            'difficulty': 'Beginner',
            'estimated_hours': 16,
            'icon': 'cpu',
            'badge_color': '#3b82f6',
            'is_popular': 1,
            'modules': [
                {
                    'title': 'C Basics & Compilation',
                    'lessons': [
                        {
                            'title': 'Introduction to C & Program Structure',
                            'slug': 'c-intro',
                            'content': '''<p><strong>C</strong> was developed by Dennis Ritchie at Bell Labs in 1972. It is a procedural, compiled, low-level language that powers operating systems, embedded hardware, and database kernels.</p>
<h4>Structure of a C Program</h4>
<pre><code>#include &lt;stdio.h&gt;

int main() {
    // Statements
    return 0;
}</code></pre>
<p>Every C program execution begins at the <code>main()</code> function.</p>''',
                            'code': '''#include <stdio.h>

int main() {
    printf("Welcome to C Programming!\\n");
    printf("Fast, Efficient, and Close to the Hardware.\\n");
    return 0;
}''',
                            'output': '''Welcome to C Programming!
Fast, Efficient, and Close to the Hardware.''',
                            'task': 'Write a C program that prints your name and age on separate lines using \\n.'
                        },
                        {
                            'title': 'Variables, Format Specifiers & Math',
                            'slug': 'c-variables',
                            'content': '''<p>C is a statically typed language. Every variable must have an explicit data type before use.</p>
<h4>Common Format Specifiers in <code>printf</code></h4>
<ul>
<li><code>%d</code> or <code>%i</code>: Integer</li>
<li><code>%f</code>: Floating-point decimal</li>
<li><code>%c</code>: Single character</li>
<li><code>%s</code>: String (array of characters)</li>
</ul>''',
                            'code': '''#include <stdio.h>

int main() {
    int age = 20;
    float gpa = 3.85;
    char grade = 'A';

    printf("Age: %d years\\n", age);
    printf("GPA: %.2f\\n", gpa);
    printf("Letter Grade: %c\\n", grade);
    return 0;
}''',
                            'output': '''Age: 20 years
GPA: 3.85
Letter Grade: A''',
                            'task': 'Declare two integer variables a = 15 and b = 4. Print their quotient and remainder.'
                        }
                    ]
                },
                {
                    'title': 'Pointers & Memory',
                    'lessons': [
                        {
                            'title': 'Understanding Pointers and Addresses',
                            'slug': 'c-pointers',
                            'content': '''<p>A <strong>pointer</strong> is a variable that stores the memory address of another variable.</p>
<h4>Key Pointer Operators:</h4>
<ul>
<li><code>&</code> (Address-of operator): Retrieves the memory address of a variable.</li>
<li><code>*</code> (Dereference operator): Accesses the value stored at the address pointed to.</li>
</ul>''',
                            'code': '''#include <stdio.h>

int main() {
    int number = 42;
    int *ptr = &number;

    printf("Value of number: %d\\n", number);
    printf("Address of number: %p\\n", (void*)&number);
    printf("Value via pointer: %d\\n", *ptr);
    return 0;
}''',
                            'output': '''Value of number: 42
Address of number: 0x7ffd582a
Value via pointer: 42''',
                            'task': 'Write a C function swap(int *a, int *b) that exchanges the values of two integers using pointers.'
                        }
                    ]
                }
            ],
            'quiz': {
                'title': 'C Programming Core Quiz',
                'description': 'Test your understanding of C syntax, pointers, data types, compilation, and standard I/O.',
                'time_limit': 15,
                'difficulty': 'Beginner',
                'questions': [
                    ('Who developed the C programming language?', None, 'Bjarne Stroustrup', 'Dennis Ritchie', 'James Gosling', 'Guido van Rossum', 'B', 'Dennis Ritchie created the C programming language at Bell Labs in 1972.'),
                    ('Which header file is required to use printf() and scanf() in C?', None, '<math.h>', '<stdlib.h>', '<stdio.h>', '<string.h>', 'C', '<stdio.h> contains declarations for standard input and output functions like printf and scanf.'),
                    ('What does the & operator represent in C when applied to a variable?', None, 'Bitwise AND only', 'Logical AND', 'Address of the variable', 'Dereference value', 'C', 'The & operator returns the memory address of the specified variable.'),
                    ('What is the return type of the main() function in standard C?', None, 'void', 'int', 'float', 'char', 'B', 'The main() function returns an integer (int) status code to the operating system, with 0 indicating success.'),
                    ('Which format specifier is used to print a floating-point number with printf?', None, '%d', '%c', '%s', '%f', 'D', '%f is the standard printf format specifier for float and double numbers.'),
                    ('What is the size of an int data type typically on modern 32-bit/64-bit systems in C?', None, '1 byte', '2 bytes', '4 bytes', '8 bytes', 'C', 'On standard 32-bit and 64-bit architectures, int is typically 4 bytes (32 bits).'),
                    ('What terminates a string in C?', None, 'Whitespace', 'Newline \\n', 'Null character \\0', 'Semicolon ;', 'C', 'In C, strings are null-terminated character arrays ending with the null byte \\0.'),
                    ('Which function dynamically allocates memory in C without initializing it to zero?', None, 'calloc()', 'malloc()', 'realloc()', 'free()', 'B', 'malloc() allocates the requested number of uninitialized bytes on the heap.'),
                    ('What keyword is used to prevent modification of a variable in C?', None, 'static', 'volatile', 'immutable', 'const', 'D', 'The const keyword makes a variable read-only after initialization.'),
                    ('What will happen if you access an array index out of bounds in C?', None, 'Compile-time error', 'IndexOutOfBoundsException', 'Undefined Behavior / segmentation fault', 'Array automatically expands', 'C', 'C does not perform bounds checking; accessing out-of-bounds indices leads to undefined behavior.')
                ]
            }
        },
        {
            'title': 'C++ Programming',
            'slug': 'cpp-programming',
            'category_id': 1,
            'description': 'Learn modern C++ including Object-Oriented Programming (OOP), templates, the Standard Template Library (STL), and high-performance system design.',
            'short_desc': 'High-performance Object-Oriented language powering game engines, browsers, and embedded systems.',
            'difficulty': 'Intermediate',
            'estimated_hours': 18,
            'icon': 'layers',
            'badge_color': '#6366f1',
            'is_popular': 1,
            'modules': [
                {
                    'title': 'C++ Basics & I/O Streams',
                    'lessons': [
                        {
                            'title': 'Introduction to Modern C++',
                            'slug': 'cpp-intro',
                            'content': '''<p><strong>C++</strong> was created by Bjarne Stroustrup as an extension of C, introducing Classes and Object-Oriented Programming while retaining direct hardware access and unmatched speed.</p>
<h4>Standard Streams</h4>
<p>C++ uses <code>std::cout</code> for output and <code>std::cin</code> for input, declared in <code>&lt;iostream&gt;</code>.</p>''',
                            'code': '''#include <iostream>
using namespace std;

int main() {
    cout << "Welcome to C++!" << endl;
    cout << "Combines low-level power with high-level abstractions." << endl;
    return 0;
}''',
                            'output': '''Welcome to C++!
Combines low-level power with high-level abstractions.''',
                            'task': 'Write a C++ program that reads two numbers using cin and displays their sum using cout.'
                        }
                    ]
                },
                {
                    'title': 'Object-Oriented Programming (OOP)',
                    'lessons': [
                        {
                            'title': 'Classes, Objects, and Constructors',
                            'slug': 'cpp-classes',
                            'content': '''<p>An <strong>Object</strong> is an instance of a <strong>Class</strong>. A class encapsulates data (attributes) and functions (methods).</p>
<h4>Access Specifiers:</h4>
<ul>
<li><code>public</code>: Accessible from anywhere.</li>
<li><code>private</code>: Accessible only within the class.</li>
<li><code>protected</code>: Accessible within the class and derived classes.</li>
</ul>''',
                            'code': '''#include <iostream>
#include <string>
using namespace std;

class Student {
private:
    string name;
    int score;

public:
    Student(string n, int s) : name(n), score(s) {}

    void display() {
        cout << "Student: " << name << " | Score: " << score << endl;
    }
};

int main() {
    Student s1("Elena", 98);
    s1.display();
    return 0;
}''',
                            'output': '''Student: Elena | Score: 98''',
                            'task': 'Create a Rectangle class with width and height attributes and an area() method.'
                        }
                    ]
                }
            ],
            'quiz': {
                'title': 'C++ Object-Oriented Programming Quiz',
                'description': 'Test your comprehension of C++ classes, inheritance, STL containers, pointers, and memory management.',
                'time_limit': 15,
                'difficulty': 'Intermediate',
                'questions': [
                    ('Who created the C++ programming language?', None, 'James Gosling', 'Bjarne Stroustrup', 'Ken Thompson', 'Linus Torvalds', 'B', 'Bjarne Stroustrup created C++ at Bell Labs in 1979 as "C with Classes".'),
                    ('Which header file is required for std::cout and std::cin?', None, '<stdio.h>', '<stream.h>', '<iostream>', '<conio.h>', 'C', '<iostream> defines standard input and output stream objects.'),
                    ('What is the default access specifier for members of a class in C++?', None, 'public', 'protected', 'private', 'internal', 'C', 'In C++, class members are private by default, unlike structs where members are public.'),
                    ('What special member function is called automatically when an object is destroyed?', None, 'Constructor', 'Finalizer', 'Destructor', 'Deleter', 'C', 'A Destructor (~ClassName) is invoked automatically when an object goes out of scope or is deleted.'),
                    ('Which feature of C++ allows functions with the same name but different parameters?', None, 'Function Overriding', 'Function Overloading', 'Encapsulation', 'Dynamic Dispatch', 'B', 'Function Overloading allows multiple functions in the same scope to share a name with differing signatures.'),
                    ('Which STL container stores elements in contiguous memory and supports dynamic resizing?', None, 'std::list', 'std::map', 'std::vector', 'std::set', 'C', 'std::vector provides dynamic array behavior with contiguous memory storage.'),
                    ('Which operator is used to allocate dynamic memory on the free store in C++?', None, 'malloc', 'alloc', 'new', 'create', 'C', 'The new operator allocates memory on the heap and calls the appropriate constructor.'),
                    ('What concept allows a derived class to provide a specific implementation of a base method?', None, 'Polymorphism / Method Overriding', 'Abstraction', 'Encapsulation', 'Composition', 'A', 'Virtual functions and method overriding enable runtime polymorphism.'),
                    ('What keyword is used to define a virtual function that MUST be implemented by derived classes?', None, 'abstract', 'virtual void func() = 0;', 'interface', 'pure virtual', 'B', 'A pure virtual function is defined with = 0 and makes the containing class abstract.'),
                    ('What does RAII stand for in modern C++ idiomatic design?', None, 'Random Access Interface Index', 'Resource Allocation Is Initialization', 'Reusable Algorithm Integration Instance', 'Realtime Asynchronous Input Iterator', 'B', 'RAII stands for Resource Allocation Is Initialization, tying resource lifetime to object lifetime.')
                ]
            }
        },
        {
            'title': 'Java Programming',
            'slug': 'java-programming',
            'category_id': 1,
            'description': 'Master Java: platform-independent, object-oriented language running billions of devices. Learn JVM concepts, collections framework, exception handling, and enterprise design.',
            'short_desc': 'Robust, platform-independent enterprise programming language with automatic memory management.',
            'difficulty': 'Intermediate',
            'estimated_hours': 18,
            'icon': 'coffee',
            'badge_color': '#f59e0b',
            'is_popular': 1,
            'modules': [
                {
                    'title': 'Java Core Architecture',
                    'lessons': [
                        {
                            'title': 'Java Fundamentals & The JVM',
                            'slug': 'java-intro',
                            'content': '''<p><strong>Java</strong> is a high-level, class-based, object-oriented programming language designed to have as few implementation dependencies as possible ("Write Once, Run Anywhere").</p>
<h4>How Java Works:</h4>
<ol>
<li>Source code is written in <code>.java</code> files.</li>
<li>Java Compiler (<code>javac</code>) compiles it to bytecode (<code>.class</code> files).</li>
<li>Java Virtual Machine (<code>JVM</code>) executes the bytecode on any operating system.</li>
</ol>''',
                            'code': '''public class HelloWorld {
    public static void main(String[] args) {
        System.out.println("Hello from Java!");
        System.out.println("Platform Independence via JVM bytecode.");
    }
}''',
                            'output': '''Hello from Java!
Platform Independence via JVM bytecode.''',
                            'task': 'Write a Java main method that prints three of your favorite tech topics.'
                        }
                    ]
                },
                {
                    'title': 'Java OOP & Collections',
                    'lessons': [
                        {
                            'title': 'Inheritance, Polymorphism & ArrayList',
                            'slug': 'java-oop',
                            'content': '''<p>Java is built around the four pillars of OOP: <strong>Encapsulation</strong>, <strong>Inheritance</strong>, <strong>Polymorphism</strong>, and <strong>Abstraction</strong>.</p>
<h4>Java Collections Framework</h4>
<p>The <code>java.util</code> package provides data structures like <code>ArrayList</code>, <code>HashMap</code>, and <code>HashSet</code>.</p>''',
                            'code': '''import java.util.ArrayList;

class Animal {
    void makeSound() {
        System.out.println("Some generic sound");
    }
}

class Dog extends Animal {
    @Override
    void makeSound() {
        System.out.println("Woof! Woof!");
    }
}

public class Main {
    public static void main(String[] args) {
        Animal myDog = new Dog();
        myDog.makeSound();

        ArrayList<String> languages = new ArrayList<>();
        languages.add("Java");
        languages.add("Kotlin");
        System.out.println("Languages count: " + languages.size());
    }
}''',
                            'output': '''Woof! Woof!
Languages count: 2''',
                            'task': 'Create a Car class with brand and speed variables, and a drive() method.'
                        }
                    ]
                }
            ],
            'quiz': {
                'title': 'Java Core & Object-Oriented Quiz',
                'description': 'Assess your understanding of Java fundamentals, JVM architecture, OOP, exceptions, and collections.',
                'time_limit': 15,
                'difficulty': 'Intermediate',
                'questions': [
                    ('What does JVM stand for in Java technology?', None, 'Java Variable Machine', 'Java Virtual Machine', 'Java Verified Module', 'Joint Virtual Memory', 'B', 'JVM stands for Java Virtual Machine, the execution engine that runs compiled Java bytecode.'),
                    ('What is the entry point method signature for every standalone Java program?', None, 'void main(String args[])', 'public static void main(String[] args)', 'public int main()', 'static void run()', 'B', 'The required entry point is public static void main(String[] args).'),
                    ('Which keyword is used by a class to inherit another class in Java?', None, 'implements', 'inherits', 'extends', 'super', 'C', 'The extends keyword is used by a class to inherit from a superclass.'),
                    ('Which of these data types is NOT a primitive type in Java?', None, 'int', 'boolean', 'char', 'String', 'D', 'String is a reference class type in java.lang, not a primitive type.'),
                    ('What mechanism automatically frees unused heap memory in Java?', None, 'Manual free()', 'Destructors', 'Garbage Collector', 'Memory Allocator', 'C', 'Java features an automatic Garbage Collector that reclaims memory allocated to unreachable objects.'),
                    ('Which keyword prevents a class from being subclassed (inherited)?', None, 'static', 'sealed', 'final', 'const', 'C', 'The final keyword on a class declaration prevents any subclass from extending it.'),
                    ('Which collection interface stores key-value pairs in Java?', None, 'List', 'Set', 'Map', 'Queue', 'C', 'Map (such as HashMap and TreeMap) maps unique keys to values.'),
                    ('What block in a try-catch structure ALWAYS executes regardless of exceptions?', None, 'catch', 'throw', 'finally', 'then', 'C', 'The finally block executes whether an exception was thrown and caught or not.'),
                    ('What is the default value of an uninitialized boolean instance variable in Java?', None, 'true', 'false', '0', 'null', 'B', 'In Java, boolean instance fields default to false upon object allocation.'),
                    ('Which package is automatically imported into every Java program without an import statement?', None, 'java.util', 'java.io', 'java.lang', 'java.net', 'C', 'The java.lang package contains core foundational classes and is imported implicitly.')
                ]
            }
        },
        {
            'title': 'HTML and CSS',
            'slug': 'html-css',
            'category_id': 2,
            'description': 'Build modern, beautiful, and responsive websites using HTML5 semantics and modern CSS3, including Flexbox, Grid, animations, and accessible styling.',
            'short_desc': 'The foundational building blocks of the web: semantic structure and modern responsive styling.',
            'difficulty': 'Beginner',
            'estimated_hours': 12,
            'icon': 'layout',
            'badge_color': '#ea580c',
            'is_popular': 1,
            'modules': [
                {
                    'title': 'HTML5 Semantic Structure',
                    'lessons': [
                        {
                            'title': 'HTML Basics & Semantic Tags',
                            'slug': 'html-basics',
                            'content': '''<p><strong>HTML (HyperText Markup Language)</strong> defines the structure and content of web pages using elements represented by tags.</p>
<h4>Semantic HTML Elements:</h4>
<ul>
<li><code>&lt;header&gt;</code>: Navigational and introductory content.</li>
<li><code>&lt;nav&gt;</code>: Group of navigational links.</li>
<li><code>&lt;main&gt;</code>: Central dominant content of the page.</li>
<li><code>&lt;article&gt;</code> and <code>&lt;section&gt;</code>: Modular thematic groups.</li>
<li><code>&lt;footer&gt;</code>: Metadata, copyright, and bottom links.</li>
</ul>''',
                            'code': '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>My First Web Page</title>
</head>
<body>
    <header>
        <h1>Welcome to Web Dev</h1>
    </header>
    <main>
        <p>HTML creates the skeleton of every website.</p>
    </main>
</body>
</html>''',
                            'output': '''Welcome to Web Dev
HTML creates the skeleton of every website.''',
                            'task': 'Create an HTML snippet containing an unordered list with 3 hyperlinks.'
                        }
                    ]
                },
                {
                    'title': 'Modern CSS3, Flexbox & Grid',
                    'lessons': [
                        {
                            'title': 'CSS Box Model, Flexbox & Grid',
                            'slug': 'css-layout',
                            'content': '''<p><strong>CSS (Cascading Style Sheets)</strong> describes how HTML elements are formatted, styled, and laid out across screen resolutions.</p>
<h4>The CSS Box Model</h4>
<p>Every element is treated as a rectangular box comprising <strong>Content</strong>, <strong>Padding</strong>, <strong>Border</strong>, and <strong>Margin</strong>.</p>
<h4>Flexbox</h4>
<p>Use <code>display: flex;</code> for one-dimensional layouts with alignments such as <code>justify-content: center;</code> and <code>align-items: center;</code>.</p>''',
                            'code': '''/* Modern Flexbox Card */
.card-container {
    display: flex;
    justify-content: space-between;
    gap: 16px;
    padding: 20px;
}

.card {
    background-color: #ffffff;
    border-radius: 8px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    padding: 24px;
    flex: 1;
}''',
                            'output': '''Renders a responsive multi-column card layout with even spacing.''',
                            'task': 'Write CSS for a button with rounded corners, a green background, and a hover effect that darkens the background.'
                        }
                    ]
                }
            ],
            'quiz': {
                'title': 'HTML5 & Modern CSS3 Quiz',
                'description': 'Test your skills in HTML semantics, attributes, the CSS box model, selectors, and responsive layout systems.',
                'time_limit': 15,
                'difficulty': 'Beginner',
                'questions': [
                    ('What does HTML stand for?', None, 'Hyperlinks and Text Markup Language', 'HyperText Markup Language', 'Home Tool Markup Language', 'High Tech Modern Language', 'B', 'HTML stands for HyperText Markup Language.'),
                    ('Which HTML element is used to define the largest heading?', None, '<heading>', '<h6>', '<head>', '<h1>', 'D', '<h1> represents the top-level heading on an HTML document.'),
                    ('Which attribute is used to provide an alternative text for an image if it cannot display?', None, 'title', 'src', 'alt', 'desc', 'C', 'The alt attribute provides alternative text for accessibility and search engines.'),
                    ('What does CSS stand for?', None, 'Creative Style Sheets', 'Computer Style System', 'Cascading Style Sheets', 'Colorful Style Sheets', 'C', 'CSS stands for Cascading Style Sheets.'),
                    ('Which CSS property controls the spacing INSIDE an element border?', None, 'margin', 'padding', 'border-spacing', 'gap', 'B', 'Padding is the space between the content and the border of an element.'),
                    ('Which value of display turns a container into a flexible one-dimensional layout?', None, 'block', 'inline', 'grid', 'flex', 'D', 'display: flex creates a flex container for laying out items in a row or column.'),
                    ('How do you select an element with id="main-header" in CSS?', None, '.main-header', '#main-header', '*main-header', 'header#all', 'B', 'The hash (#) symbol is used to select elements by their id attribute in CSS.'),
                    ('Which HTML5 semantic element should contain the primary navigational links?', None, '<links>', '<menu>', '<nav>', '<section>', 'C', 'The <nav> element designates major navigational blocks on a webpage.'),
                    ('Which CSS property is used to change the text color of an element?', None, 'text-color', 'font-color', 'color', 'background-color', 'C', 'The color property defines the foreground text color in CSS.'),
                    ('What is the default positioning scheme of HTML elements in normal flow?', None, 'relative', 'absolute', 'static', 'fixed', 'C', 'HTML elements are positioned static by default, following the normal document flow.')
                ]
            }
        },
        {
            'title': 'JavaScript',
            'slug': 'javascript',
            'category_id': 2,
            'description': 'Master modern JavaScript (ES6+) for interactive web frontends and full-stack development. Learn variables, functions, DOM manipulation, asynchronous promises, and APIs.',
            'short_desc': 'The interactive language of the web: ES6+ syntax, DOM manipulation, async/await, and APIs.',
            'difficulty': 'Intermediate',
            'estimated_hours': 16,
            'icon': 'zap',
            'badge_color': '#eab308',
            'is_popular': 1,
            'modules': [
                {
                    'title': 'JavaScript Fundamentals & ES6',
                    'lessons': [
                        {
                            'title': 'Variables, Functions & Arrow Functions',
                            'slug': 'js-basics',
                            'content': '''<p><strong>JavaScript</strong> is the dynamic scripting language that brings interactivity to websites. Modern JavaScript uses <strong>ES6+</strong> standards.</p>
<h4>Variable Declarations:</h4>
<ul>
<li><code>const</code>: Block-scoped, immutable identifier binding.</li>
<li><code>let</code>: Block-scoped, mutable variable.</li>
<li><code>var</code>: Function-scoped (legacy, avoid in modern code).</li>
</ul>''',
                            'code': '''// Modern ES6 JavaScript
const user = { name: "Jordan", role: "Developer" };

// Arrow function
const greet = (person) => `Hello, ${person.name}! Role: ${person.role}`;

console.log(greet(user));

// Array methods: map and filter
const numbers = [1, 2, 3, 4, 5];
const squares = numbers.map(n => n * n);
console.log("Squares:", squares);''',
                            'output': '''Hello, Jordan! Role: Developer
Squares: [1, 4, 9, 16, 25]''',
                            'task': 'Write an arrow function that takes an array of numbers and returns only numbers greater than 10 using .filter().'
                        }
                    ]
                },
                {
                    'title': 'Async JavaScript & DOM',
                    'lessons': [
                        {
                            'title': 'DOM Manipulation & Async/Await',
                            'slug': 'js-async-dom',
                            'content': '''<p>The <strong>Document Object Model (DOM)</strong> represents the webpage structure that JavaScript can inspect, modify, and listen for user events on.</p>
<h4>Asynchronous JavaScript</h4>
<p>Modern applications fetch data asynchronously without blocking the UI thread using <code>async / await</code> and the <code>fetch()</code> API.</p>''',
                            'code': '''// Simulating an asynchronous data fetch
async function fetchCourseInfo() {
    console.log("Fetching course data...");
    const data = await new Promise(resolve => {
        setTimeout(() => resolve({ course: "JavaScript", lessons: 12 }), 500);
    });
    console.log(`Loaded: ${data.course} with ${data.lessons} lessons.`);
}

fetchCourseInfo();''',
                            'output': '''Fetching course data...
Loaded: JavaScript with 12 lessons.''',
                            'task': 'Write an async function that simulates fetching user data and handles potential errors with a try...catch block.'
                        }
                    ]
                }
            ],
            'quiz': {
                'title': 'Modern JavaScript (ES6+) Quiz',
                'description': 'Evaluate your knowledge of JavaScript syntax, types, closures, promises, arrow functions, and the DOM.',
                'time_limit': 15,
                'difficulty': 'Intermediate',
                'questions': [
                    ('Which keyword creates a block-scoped variable whose value cannot be reassigned?', None, 'var', 'let', 'const', 'immutable', 'C', 'const declares block-scoped read-only named constants.'),
                    ('What is the output of typeof null in JavaScript?', 'console.log(typeof null);', '"null"', '"undefined"', '"object"', '"boolean"', 'C', 'Due to a historical bug in JavaScript design, typeof null evaluates to "object".'),
                    ('Which method attaches an event listener to a DOM element?', None, 'element.attach()', 'element.addEventListener()', 'element.onEvent()', 'element.listen()', 'B', 'addEventListener() is the standard method for registering event handlers on DOM elements.'),
                    ('What does the strict equality operator (===) compare?', None, 'Values only, with type coercion', 'Both values and types without coercion', 'Object memory pointers only', 'Length of items', 'B', 'The strict equality operator (===) checks both value and type without converting types.'),
                    ('Which array method creates a new array populated with the results of calling a provided function on every element?', None, 'forEach()', 'map()', 'filter()', 'reduce()', 'B', 'Array.prototype.map() applies a transformation function to each element and returns a new array.'),
                    ('What does the Promise object represent in JavaScript?', None, 'A synchronous function thread', 'An eventual completion or failure of an asynchronous operation', 'A fixed variable definition', 'A memory pointer', 'B', 'A Promise represents the eventual result of an asynchronous operation and its resulting value.'),
                    ('How do you parse a JSON string into a JavaScript object?', None, 'JSON.stringify()', 'JSON.parse()', 'JSON.toObject()', 'Object.fromJSON()', 'B', 'JSON.parse() deserializes a JSON-formatted string into a JavaScript object or primitive.'),
                    ('What keyword pauses execution inside an async function until a Promise settles?', None, 'wait', 'pause', 'await', 'defer', 'C', 'The await keyword can only be used inside async functions to pause execution until a promise resolves.'),
                    ('What will [1, 2, 3] + [4, 5, 6] evaluate to in JavaScript?', None, '[1, 2, 3, 4, 5, 6]', '"1,2,34,5,6"', 'NaN', 'Error', 'B', 'The + operator converts both arrays to comma-separated strings and concatenates them into "1,2,34,5,6".'),
                    ('Which built-in object allows scheduling code execution after a specified delay in milliseconds?', None, 'setInterval()', 'setTimeout()', 'setDelay()', 'wait()', 'B', 'setTimeout(callback, milliseconds) executes code after a specified delay.')
                ]
            }
        },
        {
            'title': 'SQL (Structured Query Language)',
            'slug': 'sql',
            'category_id': 3,
            'description': 'Master relational database management, querying, joins, aggregations, schema design, and indexing using standard SQL.',
            'short_desc': 'The universal language for relational databases: querying, filtering, joins, and aggregates.',
            'difficulty': 'Beginner',
            'estimated_hours': 14,
            'icon': 'database',
            'badge_color': '#0284c7',
            'is_popular': 1,
            'modules': [
                {
                    'title': 'SQL Querying Basics',
                    'lessons': [
                        {
                            'title': 'Introduction to Relational Databases & SELECT',
                            'slug': 'sql-select',
                            'content': '''<p><strong>SQL (Structured Query Language)</strong> is the standard language for storing, manipulating, and retrieving data stored in relational databases like PostgreSQL, MySQL, and SQLite.</p>
<h4>The Fundamental Query</h4>
<pre><code>SELECT column1, column2 
FROM table_name 
WHERE condition 
ORDER BY column1 ASC;</code></pre>''',
                            'code': '''-- Create and query students table
CREATE TABLE students (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    gpa REAL,
    major TEXT
);

INSERT INTO students (name, gpa, major) VALUES 
('David', 3.8, 'Computer Science'),
('Sophia', 3.9, 'Data Science'),
('Marcus', 3.4, 'Computer Science');

SELECT name, gpa FROM students 
WHERE gpa >= 3.5 
ORDER BY gpa DESC;''',
                            'output': '''name    | gpa
Sophia  | 3.9
David   | 3.8''',
                            'task': 'Write an SQL query to retrieve all students majoring in "Data Science" ordered alphabetically by name.'
                        }
                    ]
                },
                {
                    'title': 'Joins, Grouping & Aggregates',
                    'lessons': [
                        {
                            'title': 'INNER JOIN, LEFT JOIN & GROUP BY',
                            'slug': 'sql-joins-grouping',
                            'content': '''<p>Relational databases connect normalized tables using keys.</p>
<h4>Common Join Types:</h4>
<ul>
<li><strong>INNER JOIN</strong>: Returns records that have matching values in both tables.</li>
<li><strong>LEFT JOIN</strong>: Returns all records from the left table and matched records from the right table.</li>
</ul>
<h4>Aggregate Functions</h4>
<p><code>COUNT()</code>, <code>AVG()</code>, <code>SUM()</code>, <code>MIN()</code>, <code>MAX()</code> combined with <code>GROUP BY</code>.</p>''',
                            'code': '''-- Query orders joined with customers
SELECT 
    c.customer_name, 
    COUNT(o.id) AS total_orders, 
    SUM(o.amount) AS total_spent
FROM customers c
LEFT JOIN orders o ON c.id = o.customer_id
GROUP BY c.id
HAVING total_spent > 100
ORDER BY total_spent DESC;''',
                            'output': '''customer_name | total_orders | total_spent
Acme Corp     | 5            | $1,450.00
Global Tech   | 2            | $320.00''',
                            'task': 'Write an SQL query to find the average score for each course from an enrollments table using GROUP BY.'
                        }
                    ]
                }
            ],
            'quiz': {
                'title': 'Relational Databases & SQL Quiz',
                'description': 'Assess your command of SQL clauses, filtering with WHERE, aggregate functions, and table JOINs.',
                'time_limit': 15,
                'difficulty': 'Beginner',
                'questions': [
                    ('What does SQL stand for?', None, 'Structured Question Language', 'Structured Query Language', 'Strong Query Logic', 'Simple Query Layout', 'B', 'SQL stands for Structured Query Language.'),
                    ('Which SQL clause is used to filter records based on a condition?', None, 'SELECT', 'ORDER BY', 'WHERE', 'GROUP BY', 'C', 'The WHERE clause specifies conditions that rows must satisfy to be selected or updated.'),
                    ('Which SQL statement is used to extract data from a database?', None, 'EXTRACT', 'GET', 'SELECT', 'FETCH', 'C', 'The SELECT statement retrieves rows and columns from one or more database tables.'),
                    ('Which keyword is used to return only unique (non-duplicate) values in a query?', None, 'UNIQUE', 'DISTINCT', 'DIFFERENT', 'ISOLATE', 'B', 'SELECT DISTINCT eliminates duplicate rows from the query result set.'),
                    ('Which clause is used to filter groups created by the GROUP BY clause?', None, 'WHERE', 'HAVING', 'FILTER', 'LIMIT', 'B', 'HAVING filters aggregated groups, whereas WHERE filters individual rows before grouping.'),
                    ('Which JOIN returns ALL rows from the left table and matched rows from the right table?', None, 'INNER JOIN', 'RIGHT JOIN', 'LEFT JOIN', 'FULL OUTER JOIN', 'C', 'LEFT JOIN (or LEFT OUTER JOIN) preserves all rows from the left table regardless of a match.'),
                    ('Which command is used to remove all records from a table without deleting the table structure?', None, 'DROP TABLE', 'TRUNCATE TABLE', 'REMOVE ALL', 'COLLAPSE', 'B', 'TRUNCATE TABLE quickly removes all rows from a table while preserving the table schema.'),
                    ('What is a PRIMARY KEY in a relational database table?', None, 'A key that encrypts data', 'A unique identifier for each row with no NULLs', 'A foreign connection to another database', 'The first column created', 'B', 'A PRIMARY KEY uniquely identifies each record in a table and cannot contain NULL values.'),
                    ('Which SQL aggregate function computes the arithmetic average of numeric values?', None, 'MEAN()', 'MEDIAN()', 'AVG()', 'COUNT()', 'C', 'The AVG() function computes the mean average value of a numeric column.'),
                    ('Which clause sorts the returned result set in ascending or descending order?', None, 'SORT BY', 'ARRANGE BY', 'ORDER BY', 'ALIGN BY', 'C', 'The ORDER BY clause sorts query results in ASC (ascending) or DESC (descending) sequence.')
                ]
            }
        },
        {
            'title': 'Data Structures and Algorithms',
            'slug': 'dsa',
            'category_id': 4,
            'description': 'Master fundamental computer science concepts: Big O notation, linked lists, stacks, queues, trees, graphs, sorting, and dynamic programming.',
            'short_desc': 'Essential algorithms, data structures, Big O notation, and technical interview problem solving.',
            'difficulty': 'Intermediate',
            'estimated_hours': 20,
            'icon': 'git-merge',
            'badge_color': '#8b5cf6',
            'is_popular': 1,
            'modules': [
                {
                    'title': 'Complexity & Linear Structures',
                    'lessons': [
                        {
                            'title': 'Big O Notation & Time Complexity',
                            'slug': 'dsa-big-o',
                            'content': '''<p><strong>Big O notation</strong> describes the asymptotic upper bound of an algorithm\'s runtime or space requirements as the input size <code>n</code> scales to infinity.</p>
<h4>Common Time Complexities:</h4>
<ul>
<li><code>O(1)</code> - Constant time: Index lookup, hash map get.</li>
<li><code>O(log n)</code> - Logarithmic: Binary search.</li>
<li><code>O(n)</code> - Linear: Scanning an array.</li>
<li><code>O(n log n)</code> - Linearithmic: Merge sort, quicksort.</li>
<li><code>O(n^2)</code> - Quadratic: Nested loops, bubble sort.</li>
</ul>''',
                            'code': '''# Binary Search in Python: O(log n)
def binary_search(arr, target):
    low = 0
    high = len(arr) - 1
    
    while low <= high:
        mid = (low + high) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    return -1

sorted_nums = [2, 5, 8, 12, 16, 23, 38, 56, 72, 91]
idx = binary_search(sorted_nums, 23)
print(f"Target found at index: {idx}")''',
                            'output': '''Target found at index: 5''',
                            'task': 'Implement a stack with push, pop, and peek operations using a Python list.'
                        }
                    ]
                },
                {
                    'title': 'Trees, Sorting & Recursion',
                    'lessons': [
                        {
                            'title': 'Binary Search Trees & QuickSort',
                            'slug': 'dsa-trees-sorting',
                            'content': '''<p>A <strong>Binary Search Tree (BST)</strong> is a node-based binary tree data structure where each node has at most two children, the left subtree contains keys smaller than the node, and the right subtree contains keys greater.</p>
<h4>Divide & Conquer: QuickSort</h4>
<p>QuickSort picks an element as a pivot and partitions the given array around the chosen pivot, running in <code>O(n log n)</code> average time.</p>''',
                            'code': '''def quicksort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quicksort(left) + middle + quicksort(right)

numbers = [34, 7, 23, 32, 5, 62]
print("Sorted:", quicksort(numbers))''',
                            'output': '''Sorted: [5, 7, 23, 32, 34, 62]''',
                            'task': 'Write an in-order traversal algorithm for a binary tree that visits nodes in ascending order.'
                        }
                    ]
                }
            ],
            'quiz': {
                'title': 'Data Structures & Algorithms Mastery Quiz',
                'description': 'Challenge yourself on asymptotic complexity, searching, sorting, trees, and linked structures.',
                'time_limit': 15,
                'difficulty': 'Intermediate',
                'questions': [
                    ('What is the time complexity of Binary Search on a sorted array of size n?', None, 'O(1)', 'O(n)', 'O(log n)', 'O(n^2)', 'C', 'Binary Search divides the search space in half at each step, yielding O(log n) time complexity.'),
                    ('Which data structure operates on a Last-In, First-Out (LIFO) principle?', None, 'Queue', 'Stack', 'Linked List', 'Priority Queue', 'B', 'A Stack follows the Last-In, First-Out (LIFO) protocol.'),
                    ('What is the worst-case time complexity of QuickSort?', None, 'O(n log n)', 'O(n)', 'O(n^2)', 'O(log n)', 'C', 'When the pivot repeatedly chooses the minimum or maximum element, QuickSort degrades to O(n^2).'),
                    ('Which sorting algorithm has a guaranteed worst-case time complexity of O(n log n)?', None, 'Bubble Sort', 'Insertion Sort', 'Merge Sort', 'Quick Sort', 'C', 'Merge Sort guarantees O(n log n) in all cases (worst, average, and best) by consistently halving arrays.'),
                    ('What is the average time complexity for lookup in a well-distributed Hash Table?', None, 'O(1)', 'O(log n)', 'O(n)', 'O(n log n)', 'A', 'Hash tables achieve average O(1) constant time complexity for insertions and lookups.'),
                    ('In a Binary Search Tree (BST), where are keys smaller than the root node located?', None, 'Right subtree', 'Left subtree', 'At the leaves only', 'At the deepest level', 'B', 'By definition of a BST, all keys in the left subtree are less than the node key.'),
                    ('Which traversal of a Binary Search Tree yields values in strictly ascending sorted order?', None, 'Pre-order traversal', 'Post-order traversal', 'In-order traversal', 'Level-order traversal', 'C', 'An in-order traversal (Left, Root, Right) of a BST visits nodes in strictly ascending sorted order.'),
                    ('What data structure operates on a First-In, First-Out (FIFO) principle?', None, 'Stack', 'Queue', 'Array', 'Heap', 'B', 'A Queue follows First-In, First-Out (FIFO) ordering.'),
                    ('What problem occurs when a recursive function exceeds its allocated call stack limit?', None, 'Memory Leak', 'NullPointerException', 'Stack Overflow', 'Segmentation Fault', 'C', 'Deep or infinite recursion exhausts call stack frames, resulting in a Stack Overflow.'),
                    ('What is the time complexity to access an element by index in a standard array?', None, 'O(n)', 'O(1)', 'O(log n)', 'O(n^2)', 'B', 'Arrays provide contiguous memory locations, allowing O(1) direct constant time index access.')
                ]
            }
        }
    ]

    for c_data in courses_data:
        cursor.execute('''
        INSERT INTO courses (title, slug, category_id, description, short_desc, difficulty, estimated_hours, icon, badge_color, is_popular, is_published)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            c_data['title'],
            c_data['slug'],
            c_data['category_id'],
            c_data['description'],
            c_data['short_desc'],
            c_data['difficulty'],
            c_data['estimated_hours'],
            c_data['icon'],
            c_data['badge_color'],
            c_data['is_popular'],
            1
        ))
        course_id = cursor.lastrowid

        # Insert modules and lessons
        for mod_idx, m_data in enumerate(c_data['modules'], 1):
            cursor.execute('''
            INSERT INTO modules (course_id, title, order_num) VALUES (?, ?, ?)
            ''', (course_id, m_data['title'], mod_idx))
            module_id = cursor.lastrowid

            for les_idx, l_data in enumerate(m_data['lessons'], 1):
                cursor.execute('''
                INSERT INTO lessons (module_id, course_id, title, slug, content_html, code_example, expected_output, practice_task, order_num)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    module_id,
                    course_id,
                    l_data['title'],
                    l_data['slug'],
                    l_data['content'],
                    l_data['code'],
                    l_data['output'],
                    l_data['task'],
                    les_idx
                ))

        # Insert quiz
        q_data = c_data['quiz']
        cursor.execute('''
        INSERT INTO quizzes (course_id, title, description, time_limit_minutes, passing_score, difficulty)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            course_id,
            q_data['title'],
            q_data['description'],
            q_data['time_limit'],
            70,
            q_data['difficulty']
        ))
        quiz_id = cursor.lastrowid

        for q_idx, q in enumerate(q_data['questions'], 1):
            q_text, snippet, op_a, op_b, op_c, op_d, correct, explanation = q
            cursor.execute('''
            INSERT INTO quiz_questions (quiz_id, question_text, code_snippet, option_a, option_b, option_c, option_d, correct_option, explanation, order_num)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                quiz_id,
                q_text,
                snippet,
                op_a,
                op_b,
                op_c,
                op_d,
                correct,
                explanation,
                q_idx
            ))

    # Add sample enrollment & progress for the demo student
    cursor.execute("SELECT id FROM courses WHERE slug = 'python'")
    py_course = cursor.fetchone()
    if py_course:
        py_id = py_course[0]
        cursor.execute("SELECT id FROM lessons WHERE course_id = ? ORDER BY id ASC LIMIT 2", (py_id,))
        py_lessons = cursor.fetchall()
        
        # Enroll Alex Morgan in Python
        cursor.execute('''
        INSERT INTO enrollments (user_id, course_id, enrolled_at, last_accessed_lesson_id, progress_percent)
        VALUES (?, ?, datetime('now', '-2 days'), ?, 40.0)
        ''', (2, py_id, py_lessons[0][0] if py_lessons else None))

        # Mark first lesson completed
        if py_lessons:
            cursor.execute('''
            INSERT INTO lesson_progress (user_id, lesson_id, course_id, is_completed)
            VALUES (?, ?, ?, 1)
            ''', (2, py_lessons[0][0], py_id))

        # Award first badge to demo student
        cursor.execute("SELECT id FROM badges WHERE code = 'FIRST_STEP'")
        badge = cursor.fetchone()
        if badge:
            cursor.execute('''
            INSERT INTO user_badges (user_id, badge_id) VALUES (?, ?)
            ''', (2, badge[0]))

        # Award Python Rookie badge
        cursor.execute("SELECT id FROM badges WHERE code = 'PYTHON_EXPLORER'")
        badge2 = cursor.fetchone()
        if badge2:
            cursor.execute('''
            INSERT INTO user_badges (user_id, badge_id) VALUES (?, ?)
            ''', (2, badge2[0]))

        # Add a sample completed quiz attempt for Alex Morgan
        cursor.execute("SELECT id FROM quizzes WHERE course_id = ?", (py_id,))
        py_quiz = cursor.fetchone()
        if py_quiz:
            cursor.execute('''
            INSERT INTO quiz_attempts (user_id, quiz_id, score, total_questions, correct_count, incorrect_count, percentage, passed, time_taken_seconds, completed_at)
            VALUES (?, ?, 9, 10, 9, 1, 90.0, 1, 480, datetime('now', '-1 day'))
            ''', (2, py_quiz[0]))

    conn.commit()
    conn.close()
    print("Database seeding completed successfully with 8 full courses and 80+ quiz questions!")

if __name__ == '__main__':
    seed_database()
