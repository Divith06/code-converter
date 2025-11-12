# backend/converter_app/utils.py
import subprocess
import tempfile
import os
import sys
from typing import Tuple

def run_code(lang: str, code: str, stdin: str = "", timeout: int = 10) -> str:
    """
    Run code for the given language and return stdout or stderr text.
    Supports: python, go, java, js/node, c, cpp.
    stdin is a string that will be provided to the process input (used for batch run).
    timeout is in seconds.
    """
    lang = (lang or "").lower().strip()
    ext_map = {
        "python": "py", "py": "py",
        "go": "go",
        "java": "java",
        "js": "js", "javascript": "js",
        "c": "c",
        "cpp": "cpp", "c++": "cpp"
    }
    ext = ext_map.get(lang, "txt")

    with tempfile.TemporaryDirectory() as tmpdir:
        filename = os.path.join(tmpdir, f"Main.{ext}")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(code)

        try:
            # Compose execution command depending on language
            if lang in ("python", "py"):
                cmd = [sys.executable, filename]

            elif lang == "go":
                cmd = ["go", "run", filename]

            elif lang in ("js", "javascript"):
                cmd = ["node", filename]

            elif lang == "java":
                # ensure filename is Main.java for public class Main
                main_path = os.path.join(tmpdir, "Main.java")
                if filename != main_path:
                    os.rename(filename, main_path)
                    filename = main_path
                compile_proc = subprocess.run(["javac", "Main.java"], cwd=tmpdir,
                                              capture_output=True, text=True, timeout=timeout)
                if compile_proc.returncode != 0:
                    return compile_proc.stderr.strip() or "[javac failed]"
                cmd = ["java", "-cp", tmpdir, "Main"]

            elif lang == "c":
                exe = os.path.join(tmpdir, "a.out")
                compile_proc = subprocess.run(["gcc", filename, "-o", exe], cwd=tmpdir,
                                              capture_output=True, text=True, timeout=timeout)
                if compile_proc.returncode != 0:
                    return compile_proc.stderr.strip() or "[gcc failed]"
                cmd = [exe]

            elif lang in ("cpp", "c++"):
                exe = os.path.join(tmpdir, "a.out")
                compile_proc = subprocess.run(["g++", filename, "-o", exe], cwd=tmpdir,
                                              capture_output=True, text=True, timeout=timeout)
                if compile_proc.returncode != 0:
                    return compile_proc.stderr.strip() or "[g++ failed]"
                cmd = [exe]

            else:
                return f"[Unsupported language: {lang}]"

            # Execute with provided stdin (batch)
            proc = subprocess.run(cmd, input=stdin, capture_output=True, text=True, timeout=timeout, cwd=tmpdir)

            if proc.returncode == 0:
                return proc.stdout.strip() or "[No output]"
            else:
                # Prefer stderr if present
                return (proc.stderr.strip() or proc.stdout.strip() or f"[Non-zero exit code: {proc.returncode}]")

        except subprocess.TimeoutExpired:
            return "[Execution timed out]"
        except Exception as e:
            return f"[Execution error: {e}]"
