import json
import tempfile
import os
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer


class CodeRunnerConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        self.process = None
        self.tmpdir = None

    async def disconnect(self, close_code):
        if self.process and self.process.returncode is None:
            self.process.kill()
        if self.tmpdir and os.path.exists(self.tmpdir):
            try:
                for f in os.listdir(self.tmpdir):
                    os.remove(os.path.join(self.tmpdir, f))
                os.rmdir(self.tmpdir)
            except Exception:
                pass

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get("action")

        if action == "run":
            await self.handle_run(data)
        elif action == "stdin":
            await self.handle_stdin(data)

    async def handle_stdin(self, data):
        """Handles user input for stdin during interactive execution."""
        if not self.process or self.process.returncode is not None:
            await self.send(json.dumps({"output": "[⚠ Process not running]\n"}))
            return

        user_input = data.get("input", "") + "\n"
        try:
            self.process.stdin.write(user_input.encode())
            await self.process.stdin.drain()
        except Exception as e:
            await self.send(json.dumps({"output": f"[❌ Failed to send input: {e}]\n"}))

    async def handle_run(self, data):
        """Compiles and runs code interactively with stdout/stderr streaming."""
        code = data.get("code", "")
        lang = (data.get("lang") or "").lower().strip()

        ext_map = {
            "python": "py", "py": "py",
            "go": "go",
            "java": "java",
            "js": "js", "javascript": "js",
            "c": "c",
            "cpp": "cpp", "c++": "cpp"
        }
        ext = ext_map.get(lang, "txt")

        self.tmpdir = tempfile.mkdtemp(prefix="code_run_")
        filename = os.path.join(self.tmpdir, f"Main.{ext}")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(code)

        # Prepare language commands
        cmd = None
        try:
            if lang in ("python", "py"):
                cmd = ["python3", filename]

            elif lang == "go":
                cmd = ["go", "run", filename]

            elif lang in ("js", "javascript"):
                cmd = ["node", filename]

            elif lang == "java":
                compile_proc = await asyncio.create_subprocess_exec(
                    "javac", filename,
                    cwd=self.tmpdir,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                _, err = await compile_proc.communicate()
                if compile_proc.returncode != 0:
                    await self.send(json.dumps({"output": err.decode()}))
                    return
                cmd = ["java", "-cp", self.tmpdir, "Main"]

            elif lang == "c":
                exe = os.path.join(self.tmpdir, "a.out")
                compile_proc = await asyncio.create_subprocess_exec(
                    "gcc", filename, "-o", exe,
                    cwd=self.tmpdir,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                _, err = await compile_proc.communicate()
                if compile_proc.returncode != 0:
                    await self.send(json.dumps({"output": err.decode()}))
                    return
                cmd = [exe]

            elif lang in ("cpp", "c++"):
                exe = os.path.join(self.tmpdir, "a.out")
                compile_proc = await asyncio.create_subprocess_exec(
                    "g++", filename, "-o", exe,
                    cwd=self.tmpdir,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                _, err = await compile_proc.communicate()
                if compile_proc.returncode != 0:
                    await self.send(json.dumps({"output": err.decode()}))
                    return
                cmd = [exe]

            else:
                await self.send(json.dumps({"output": f"[❌ Unsupported language: {lang}]\n"}))
                return

            await self.send(json.dumps({"output": f"▶ Running {lang} code...\n"}))

            # Start async process
            self.process = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
                cwd=self.tmpdir
            )

            # Start reading output asynchronously
            asyncio.create_task(self.stream_output())

        except Exception as e:
            await self.send(json.dumps({"output": f"[❌ Runtime error: {e}]\n"}))

    async def stream_output(self):
        """Continuously stream output to the frontend while process runs."""
        try:
            while True:
                if not self.process:
                    break

                line = await self.process.stdout.readline()
                if not line:
                    break
                await self.send(json.dumps({"output": line.decode()}))

            await self.send(json.dumps({"output": "\n💡 Execution finished.\n"}))
        except asyncio.CancelledError:
            pass
        except Exception as e:
            await self.send(json.dumps({"output": f"[Stream error: {e}]\n"}))
