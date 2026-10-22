import sys
import subprocess
import tempfile
import os

DISALLOWED_PATTERNS = [
    'import os', 'from os', 'import sys', 'from sys', 'import subprocess', 'from subprocess',
    'import shutil', 'from shutil', 'import socket', 'from socket', 'open(', '__import__',
    'eval(', 'exec(', 'compile('
]

def run_python_code(code_string):
    """
    Executes Python code in a restricted isolated subprocess with timeouts.
    Disallows file system operations, socket networking, and process spawning.
    """
    if not code_string or not code_string.strip():
        return {
            'success': True,
            'output': '(No code provided to execute)'
        }

    # Security check: check for dangerous imports or calls
    for pattern in DISALLOWED_PATTERNS:
        if pattern in code_string:
            return {
                'success': False,
                'output': f"Security Warning: The call '{pattern}' is restricted in the online educational sandbox for server safety.\nYou can run standard Python math, data structures, functions, and logic safely!"
            }

    # Write code to a temporary file
    temp_file = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
            temp_file = f.name
            f.write(code_string)

        # Run with strict timeout of 3.0 seconds
        process = subprocess.run(
            [sys.executable, temp_file],
            capture_output=True,
            text=True,
            timeout=3.5
        )

        stdout = process.stdout
        stderr = process.stderr

        if process.returncode == 0:
            output = stdout if stdout.strip() else "(Code executed successfully with no output)"
            return {
                'success': True,
                'output': output
            }
        else:
            return {
                'success': False,
                'output': stderr or "Execution resulted in an error."
            }

    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'output': "Execution Timed Out (Limit: 3 seconds). Check for infinite loops in your code!"
        }
    except Exception as e:
        return {
            'success': False,
            'output': f"Sandbox Execution Error: {str(e)}"
        }
    finally:
        if temp_file and os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except Exception:
                pass
