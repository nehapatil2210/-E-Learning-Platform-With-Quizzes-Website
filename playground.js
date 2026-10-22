/**
 * E-Learning Platform with Quizzes - Interactive Coding Playground
 * Multi-language support with code execution, syntax templates, and practice challenges.
 */

const SAMPLE_PROGRAMS = {
    python: `# Python 3 Practice Program
def fibonacci(n):
    """Generate first n Fibonacci numbers."""
    sequence = [0, 1]
    while len(sequence) < n:
        sequence.append(sequence[-1] + sequence[-2])
    return sequence[:n]

count = 8
print(f"First {count} Fibonacci numbers:")
print(fibonacci(count))

# Object-oriented demonstration
class Student:
    def __init__(self, name, score):
        self.name = name
        self.score = score
        
    def summary(self):
        status = "Passed" if self.score >= 70 else "Needs Work"
        return f"{self.name}: {self.score}% ({status})"

student = Student("Sophia", 92)
print(student.summary())`,

    javascript: `// Modern JavaScript Playground
const calculateStats = (numbers) => {
    const sum = numbers.reduce((acc, curr) => acc + curr, 0);
    const avg = sum / numbers.length;
    const max = Math.max(...numbers);
    const min = Math.min(...numbers);
    return { sum, avg, max, min };
};

const testScores = [85, 92, 78, 96, 88];
console.log("Scores Analyzed:", testScores);
console.log(calculateStats(testScores));`,

    html: `<!DOCTYPE html>
<html>
<head>
<style>
  body { font-family: sans-serif; display: flex; justify-content: center; align-items: center; min-height: 250px; background: #f0fdf4; margin: 0; }
  .card { background: white; padding: 24px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); border-top: 4px solid #10b981; text-align: center; max-width: 300px; }
  h2 { color: #065f46; margin-top: 0; }
  button { background: #10b981; color: white; border: none; padding: 8px 16px; border-radius: 6px; cursor: pointer; font-weight: bold; }
  button:hover { background: #059669; }
</style>
</head>
<body>
  <div class="card">
    <h2>Interactive HTML Preview</h2>
    <p>Live CSS styling rendered directly inside the browser iframe.</p>
    <button onclick="alert('Button clicked inside Playground!')">Click Me!</button>
  </div>
</body>
</html>`,

    sql: `-- Sample Relational SQL Queries
SELECT 
    c.title AS course_title,
    c.difficulty,
    COUNT(e.id) AS total_enrolled,
    ROUND(AVG(e.progress_percent), 1) AS avg_progress
FROM courses c
LEFT JOIN enrollments e ON c.id = e.course_id
GROUP BY c.id
ORDER BY total_enrolled DESC;`,

    c: `#include <stdio.h>

// Function to calculate factorial
long long factorial(int n) {
    if (n <= 1) return 1;
    return n * factorial(n - 1);
}

int main() {
    int number = 5;
    printf("Factorial of %d is %lld\\n", number, factorial(number));
    return 0;
}`,

    cpp: `#include <iostream>
#include <vector>
#include <numeric>

using namespace std;

int main() {
    vector<int> grades = {88, 92, 79, 95, 84};
    int total = accumulate(grades.begin(), grades.end(), 0);
    double average = (double)total / grades.size();

    cout << "C++ STL Vector Processing:" << endl;
    cout << "Total: " << total << ", Average: " << average << endl;
    return 0;
}`,

    java: `public class Main {
    public static void main(String[] args) {
        System.out.println("Java Playground Demonstration");
        int[] scores = {90, 85, 78, 92};
        int sum = 0;
        for (int s : scores) {
            sum += s;
        }
        System.out.println("Sum of scores: " + sum);
    }
}`
};

const CHALLENGES = {
    python: {
        title: "Challenge: Find Even Numbers",
        description: "Write a function get_evens(nums) that takes a list of integers and returns a new list containing only the even numbers.",
        starter: `def get_evens(numbers):
    # Your code here
    return [n for n in numbers if n % 2 == 0]

# Test cases
test_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
print("Result:", get_evens(test_list))`
    },
    javascript: {
        title: "Challenge: Palindrome Checker",
        description: "Write a function isPalindrome(str) that returns true if a given word is spelled the same backwards.",
        starter: `function isPalindrome(str) {
    const clean = str.toLowerCase().replace(/[^a-z0-9]/g, '');
    return clean === clean.split('').reverse().join('');
}

console.log("racecar:", isPalindrome("racecar"));
console.log("hello:", isPalindrome("hello"));`
    }
};

document.addEventListener('DOMContentLoaded', () => {
    initPlayground();
});

function initPlayground() {
    const langSelect = document.getElementById('playgroundLanguageSelect');
    const editor = document.getElementById('playgroundEditor');
    const consoleOutput = document.getElementById('playgroundConsole');
    const previewIframe = document.getElementById('playgroundPreviewIframe');
    const runBtn = document.getElementById('runCodeBtn');
    const clearBtn = document.getElementById('clearCodeBtn');
    const resetBtn = document.getElementById('resetCodeBtn');
    const loadChallengeBtn = document.getElementById('loadChallengeBtn');

    if (!editor || !langSelect) return;

    function updateLanguageMode() {
        const lang = langSelect.value;
        editor.value = SAMPLE_PROGRAMS[lang] || '# Write code here';

        if (lang === 'html') {
            consoleOutput.style.display = 'none';
            previewIframe.style.display = 'block';
            runHtmlPreview(editor.value);
        } else {
            consoleOutput.style.display = 'block';
            previewIframe.style.display = 'none';
            consoleOutput.textContent = `// Ready to run ${lang.toUpperCase()} code.\n// Click "Run Code" above.`;
        }
    }

    langSelect.addEventListener('change', updateLanguageMode);

    if (resetBtn) {
        resetBtn.addEventListener('click', () => {
            editor.value = SAMPLE_PROGRAMS[langSelect.value] || '';
            consoleOutput.textContent = '// Example reset.';
        });
    }

    if (clearBtn) {
        clearBtn.addEventListener('click', () => {
            editor.value = '';
            consoleOutput.textContent = '// Editor cleared.';
        });
    }

    if (loadChallengeBtn) {
        loadChallengeBtn.addEventListener('click', () => {
            const lang = langSelect.value;
            const challenge = CHALLENGES[lang];
            if (challenge) {
                editor.value = challenge.starter;
                consoleOutput.textContent = `// Challenge Loaded: ${challenge.title}\n// Goal: ${challenge.description}`;
            } else {
                alert(`No challenge currently configured for ${lang}. Try Python or JavaScript!`);
            }
        });
    }

    if (runBtn) {
        runBtn.addEventListener('click', () => {
            const lang = langSelect.value;
            const code = editor.value;

            if (lang === 'html') {
                runHtmlPreview(code);
                return;
            }

            if (lang === 'javascript') {
                runJsInSandbox(code);
                return;
            }

            // Run backend execution for Python and other languages
            runBtn.disabled = true;
            runBtn.innerHTML = 'Running...';
            consoleOutput.textContent = 'Executing in secure sandbox...';

            fetch('/api/execute-code', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ code: code, language: lang })
            })
            .then(res => res.json())
            .then(data => {
                runBtn.disabled = false;
                runBtn.innerHTML = '▶ Run Code';
                consoleOutput.textContent = data.output;
            })
            .catch(err => {
                runBtn.disabled = false;
                runBtn.innerHTML = '▶ Run Code';
                consoleOutput.textContent = `Error reaching sandbox runner: ${err.message}`;
            });
        });
    }

    function runHtmlPreview(html) {
        const doc = previewIframe.contentDocument || previewIframe.contentWindow.document;
        doc.open();
        doc.write(html);
        doc.close();
    }

    function runJsInSandbox(jsCode) {
        consoleOutput.textContent = '';
        let capturedLogs = [];
        const originalLog = console.log;

        try {
            console.log = (...args) => {
                capturedLogs.push(args.map(a => typeof a === 'object' ? JSON.stringify(a, null, 2) : a).join(' '));
                originalLog.apply(console, args);
            };

            // Evaluate in safe scope
            const evalFn = new Function(jsCode);
            evalFn();

            console.log = originalLog;
            consoleOutput.textContent = capturedLogs.length > 0 ? capturedLogs.join('\n') : '(Code executed successfully with no console output)';
        } catch (err) {
            console.log = originalLog;
            consoleOutput.textContent = `JavaScript Execution Error: ${err.message}`;
        }
    }

    // Initialize
    updateLanguageMode();
}
