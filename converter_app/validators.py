# validators.py
import subprocess
import tempfile
import os
import shlex
import sys
from typing import Tuple, Dict

# WARNING: Running user code is dangerous. Use only in sandboxed environment or set ENABLE_LOCAL_EXEC=0.
ENABLE_LOCAL_EXEC = os.getenv("ENABLE_LOCAL_EXEC", "0") == "1"
EXEC_TIMEOUT = 5  # seconds


def run_python_code(source: str) -> Tuple[bool, str]:
    """Run python source in a temporary file. Returns (success, stdout+stderr)"""
    if not ENABLE_LOCAL_EXEC:
        return False, "Local execution disabled."
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
        f.write(source)
        fname = f.name
    try:
        proc = subprocess.run([sys.executable, fname], capture_output=True, text=True, timeout=EXEC_TIMEOUT)
        out = (proc.stdout or "") + (proc.stderr or "")
        return proc.returncode == 0, out
    except Exception as e:
        return False, f"Execution error: {e}"
    finally:
        try:
            os.remove(fname)
        except:
            pass


def run_go_code(source: str) -> Tuple[bool, str]:
    """Run Go code by writing to a temp file and running `go run` if go is installed."""
    if not ENABLE_LOCAL_EXEC:
        return False, "Local execution disabled."
    with tempfile.TemporaryDirectory() as d:
        fname = os.path.join(d, "temp.go")
        with open(fname, "w") as f:
            f.write(source)
        try:
            proc = subprocess.run(["go", "run", fname], capture_output=True, text=True, timeout=EXEC_TIMEOUT)
            out = (proc.stdout or "") + (proc.stderr or "")
            return proc.returncode == 0, out
        except Exception as e:
            return False, f"Execution error: {e}"


def execute_by_lang(code: str, lang: str) -> Dict:
    """Execute code depending on language and return dict with success and output."""
    lang = lang.lower()
    if lang in ("py", "python"):
        ok, out = run_python_code(code)
        return {"success": ok, "output": out}
    if lang == "go":
        ok, out = run_go_code(code)
        return {"success": ok, "output": out}
    # other languages not executed locally
    return {"success": False, "output": f"Execution not supported for {lang}"}
