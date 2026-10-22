"""
AI Learning Assistant - Educational Knowledge Base and Assistant Engine.
Provides instant answers for programming topics, syntax questions, debugging advice,
and course recommendations across Python, C, C++, Java, HTML/CSS, JavaScript, SQL, and DSA.
"""

KNOWLEDGE_TOPICS = {
    'python': {
        'keywords': ['python', 'indentation', 'def', 'list', 'dict', 'tuple', 'lambda', 'pip', 'virtualenv', 'self'],
        'summary': 'Python is a high-level interpreted programming language renowned for its readable syntax, extensive standard libraries, and versatility across web, AI, and scripting.',
        'common_answers': {
            'loop': 'In Python, you can use `for item in sequence:` to iterate through lists, strings, or ranges. Use `range(start, stop, step)` to generate number sequences.',
            'function': 'Define functions using the `def` keyword: `def my_func(arg1, arg2): return arg1 + arg2`. Use docstrings `"""Doc"""` for documentation.',
            'list': 'Python lists are mutable arrays declared with square brackets: `fruits = ["apple", "banana"]`. Useful methods include `.append()`, `.pop()`, `.sort()`, and slicing `[start:stop:step]`.',
            'dict': 'Dictionaries store key-value mappings: `student = {"name": "Alice", "score": 98}`. Access values using `dict["key"]` or `dict.get("key", default)`.',
            'error': 'Common Python errors include `IndentationError` (inconsistent tabs/spaces), `TypeError` (mixing incompatible types), and `IndexError` (accessing an out-of-range index).'
        }
    },
    'javascript': {
        'keywords': ['javascript', 'js', 'dom', 'const', 'let', 'async', 'await', 'promise', 'arrow function', 'callback'],
        'summary': 'JavaScript is the dynamic scripting language powering interactive web browsers and modern backend development with Node.js.',
        'common_answers': {
            'variable': 'Use `const` for variables that should not be reassigned, and `let` for variables that will change. Avoid `var` in modern ES6+ code.',
            'async': 'Asynchronous operations return Promises. You can handle them with `.then()` or using `async` and `await` inside functions.',
            'dom': 'Manipulate the DOM using `document.querySelector(".my-class")`, `element.textContent`, and `element.addEventListener("click", handler)`.',
            'arrow': 'Arrow functions provide concise syntax: `const add = (a, b) => a + b;`. They inherit `this` lexically from their enclosing scope.'
        }
    },
    'c': {
        'keywords': ['c programming', 'pointer', 'malloc', 'printf', 'scanf', 'memory', 'struct', 'header'],
        'summary': 'C is a foundational procedural compiled language that provides low-level memory access and serves as the baseline for modern computing systems.',
        'common_answers': {
            'pointer': 'A pointer stores the memory address of another variable. Use `&` to obtain the address, and `*` to dereference and access the stored value.',
            'memory': 'Dynamic memory in C is managed using `malloc(bytes)` to allocate on the heap, and `free(ptr)` to release memory to prevent memory leaks.',
            'string': 'In C, strings are null-terminated character arrays ending with the byte `\\0`.'
        }
    },
    'cpp': {
        'keywords': ['c++', 'cpp', 'class', 'object', 'oop', 'template', 'stl', 'vector', 'inheritance', 'virtual'],
        'summary': 'C++ extends C with powerful Object-Oriented and generic programming features, templates, and the Standard Template Library (STL).',
        'common_answers': {
            'class': 'A C++ class groups attributes and methods. Members are `private` by default. Define constructors with the same name as the class.',
            'stl': 'The STL provides containers like `std::vector`, `std::map`, `std::set`, and algorithms like `std::sort`. Include `<vector>` or `<algorithm>`.'
        }
    },
    'java': {
        'keywords': ['java', 'jvm', 'bytecode', 'public static void main', 'polymorphism', 'interface', 'abstract'],
        'summary': 'Java is an enterprise-grade, class-based, object-oriented language known for platform independence via the Java Virtual Machine (JVM).',
        'common_answers': {
            'oop': 'The four core pillars of Java OOP are: Encapsulation (data hiding), Inheritance (extends), Polymorphism (method overriding), and Abstraction (interfaces and abstract classes).',
            'collection': 'Use `ArrayList<Type>` for resizable arrays and `HashMap<Key, Value>` for key-value pairs from `java.util`.'
        }
    },
    'sql': {
        'keywords': ['sql', 'select', 'join', 'database', 'where', 'group by', 'primary key', 'foreign key'],
        'summary': 'SQL is the standard language for querying, updating, and managing relational database management systems.',
        'common_answers': {
            'select': 'Retrieve records using `SELECT col1, col2 FROM table WHERE condition ORDER BY col1 DESC;`.',
            'join': '`INNER JOIN` retrieves only matching rows between tables. `LEFT JOIN` returns all rows from the left table plus any matched rows from the right table.',
            'aggregate': 'Compute group statistics using `COUNT()`, `SUM()`, `AVG()` combined with `GROUP BY` and filter with `HAVING`.'
        }
    },
    'dsa': {
        'keywords': ['dsa', 'algorithm', 'data structure', 'big o', 'complexity', 'binary search', 'stack', 'queue', 'tree', 'graph'],
        'summary': 'Data Structures and Algorithms form the core foundation of efficient computing, problem-solving, and software engineering.',
        'common_answers': {
            'big o': 'Big O measures runtime scalability. Common notations: O(1) constant, O(log n) binary search, O(n) linear scan, O(n log n) merge sort, O(n^2) nested loops.',
            'stack': 'Stacks operate on Last-In, First-Out (LIFO). Elements are added with push() and removed with pop(). Used in call stacks and undo operations.',
            'queue': 'Queues operate on First-In, First-Out (FIFO). Elements enter at the rear and exit from the front.'
        }
    },
    'html': {
        'keywords': ['html', 'css', 'flexbox', 'grid', 'div', 'span', 'responsive', 'margin', 'padding'],
        'summary': 'HTML supplies semantic document structure and CSS governs visual presentation, styling, and responsive layout across devices.',
        'common_answers': {
            'flexbox': 'Set `display: flex;` on a container. Use `justify-content` for main-axis alignment and `align-items` for cross-axis alignment.',
            'box model': 'Every HTML element is a box with Content -> Padding -> Border -> Margin.'
        }
    }
}

def get_ai_response(user_query, context_course=None):
    """
    Analyzes the user's question and provides an informative, structured educational response.
    Includes concept explanation, syntax or code snippet, and suggested learning steps.
    """
    q_lower = user_query.lower().strip()

    # Check for greetings
    if q_lower in ['hello', 'hi', 'hey', 'greetings', 'help']:
        return {
            'message': "Hello! I'm **EduBot**, your programming learning assistant. You can ask me to:\n\n"
                       "- Explain programming concepts (e.g. *What is a pointer in C?*, *Explain Big O notation*)\n"
                       "- Help debug error messages\n"
                       "- Show code examples in Python, JavaScript, C, C++, Java, HTML/CSS, SQL, or DSA\n"
                       "- Suggest what topic or course you should study next.\n\n"
                       "What would you like to learn today?",
            'subject': 'General',
            'related_course': 'python'
        }

    # Match subject
    matched_subject = None
    if context_course:
        for k in KNOWLEDGE_TOPICS:
            if k in context_course.lower():
                matched_subject = k
                break

    if not matched_subject:
        for subject, data in KNOWLEDGE_TOPICS.items():
            if any(kw in q_lower for kw in data['keywords']):
                matched_subject = subject
                break

    if not matched_subject:
        matched_subject = 'python'  # default fallback subject

    data = KNOWLEDGE_TOPICS[matched_subject]

    # Check for specific answer subcategories
    specific_answer = None
    for subkey, ans in data.get('common_answers', {}).items():
        if subkey in q_lower:
            specific_answer = ans
            break

    # Construct thoughtful structured response
    response_lines = []
    response_lines.append(f"### 💡 **{matched_subject.upper()} Insight**")

    if specific_answer:
        response_lines.append(f"\n{specific_answer}\n")
    else:
        response_lines.append(f"\n{data['summary']}\n")

    # Add contextual code example
    if matched_subject == 'python':
        response_lines.append("""```python
# Practical Python Example
def calculate_summary(scores):
    average = sum(scores) / len(scores)
    status = "Passed" if average >= 70 else "Needs Practice"
    return average, status

scores = [88, 92, 75, 96]
avg, result = calculate_summary(scores)
print(f"Average: {avg:.1f}% -> Status: {result}")
```""")
    elif matched_subject == 'javascript':
        response_lines.append("""```javascript
// Interactive JavaScript Example
const calculateSummary = (scores) => {
    const total = scores.reduce((sum, s) => sum + s, 0);
    const avg = total / scores.length;
    return { avg, status: avg >= 70 ? 'Passed' : 'Needs Practice' };
};

console.log(calculateSummary([88, 92, 75, 96]));
```""")
    elif matched_subject == 'sql':
        response_lines.append("""```sql
-- Practical SQL Example
SELECT student_id, AVG(percentage) AS avg_score, COUNT(id) AS total_quizzes
FROM quiz_attempts
GROUP BY student_id
HAVING avg_score >= 70
ORDER BY avg_score DESC;
```""")
    elif matched_subject == 'dsa':
        response_lines.append("""```python
# O(log n) Binary Search Example
def binary_search(arr, target):
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1
```""")
    elif matched_subject in ['c', 'cpp']:
        response_lines.append("""```c
// Memory and pointer example
#include <stdio.h>

void doubleValue(int *val) {
    *val = (*val) * 2;
}

int main() {
    int x = 21;
    doubleValue(&x);
    printf("Doubled value: %d\\n", x); // 42
    return 0;
}
```""")

    response_lines.append(f"\n> **Recommended Next Step:** Visit the **{matched_subject.upper()} Course** in our Course Catalog to test your skills with topic quizzes and hands-on playground practice!")

    return {
        'message': "\n".join(response_lines),
        'subject': matched_subject.capitalize(),
        'related_course': matched_subject
    }
