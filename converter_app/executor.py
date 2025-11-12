# executor.py — executes code safely in temporary sandboxes
import subprocess
import tempfile
import os
import textwrap


def run_code(language: str, code: str) -> str:
    """
    Executes the given code snippet in a sandbox (temp file).
    Supports: python, go, js, java, c, cpp
    Returns the stdout or stderr output.
    """
    language = language.lower()
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            if language in ["py", "python"]:
                filepath = os.path.join(tmpdir, "temp.py")
                with open(filepath, "w") as f:
                    f.write(code)
                cmd = ["python3", filepath]

            elif language in ["go", "golang"]:
                filepath = os.path.join(tmpdir, "temp.go")
                with open(filepath, "w") as f:
                    f.write(code)
                cmd = ["go", "run", filepath]

            elif language in ["js", "javascript"]:
                filepath = os.path.join(tmpdir, "temp.js")
                with open(filepath, "w") as f:
                    f.write(code)
                cmd = ["node", filepath]

            elif language == "java":
                filepath = os.path.join(tmpdir, "Temp.java")
                with open(filepath, "w") as f:
                    f.write(code)
                compile_proc = subprocess.run(["javac", filepath], capture_output=True, text=True)
                if compile_proc.returncode != 0:
                    return compile_proc.stderr
                cmd = ["java", "-cp", tmpdir, "Temp"]

            elif language == "c":
                filepath = os.path.join(tmpdir, "temp.c")
                with open(filepath, "w") as f:
                    f.write(code)
                compile_proc = subprocess.run(["gcc", filepath, "-o", os.path.join(tmpdir, "a.out")],
                                              capture_output=True, text=True)
                if compile_proc.returncode != 0:
                    return compile_proc.stderr
                cmd = [os.path.join(tmpdir, "a.out")]

            elif language == "cpp":
                filepath = os.path.join(tmpdir, "temp.cpp")
                with open(filepath, "w") as f:
                    f.write(code)
                compile_proc = subprocess.run(["g++", filepath, "-o", os.path.join(tmpdir, "a.out")],
                                              capture_output=True, text=True)
                if compile_proc.returncode != 0:
                    return compile_proc.stderr
                cmd = [os.path.join(tmpdir, "a.out")]

            else:
                return f"Execution not supported for {language}"

            # Run the compiled/interpreted code
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            output = (proc.stdout or proc.stderr).strip()
            return output or "(no output)"
    except Exception as e:
        return f"Execution error: {e}"
