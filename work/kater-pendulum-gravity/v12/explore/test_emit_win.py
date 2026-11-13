"""Exercise the task's tests/emit.py run_case on Windows (author self-check, not shipped).

select() takes only sockets on Windows, so a PeekNamedPipe-based stand-in replaces selectors, and killpg (absent
here) becomes a no-op; everything else is emit.py's own code.

    python -X utf8 -I -B test_emit_win.py <task_dir>
"""
import ctypes
import ctypes.wintypes as W
import importlib.util
import json
import msvcrt
import os
import sys
import time
import types

kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
PeekNamedPipe = kernel32.PeekNamedPipe
PeekNamedPipe.argtypes = [W.HANDLE, ctypes.c_void_p, W.DWORD, ctypes.c_void_p, ctypes.POINTER(W.DWORD),
                          ctypes.c_void_p]
PeekNamedPipe.restype = W.BOOL


class Key:
    def __init__(self, fd):
        self.fd = fd


class PeekSelector:
    """Ready when the pipe holds data or is broken (EOF, where os.read returns b'')."""

    def __init__(self):
        self.map = {}

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def register(self, fd, events):
        self.map[fd] = Key(fd)

    def unregister(self, fd):
        del self.map[fd]

    def get_map(self):
        return self.map

    def select(self, timeout):
        end = time.monotonic() + (timeout or 0)
        while True:
            ready = []
            for fd, key in self.map.items():
                avail = W.DWORD(0)
                ok = PeekNamedPipe(msvcrt.get_osfhandle(fd), None, 0, None, ctypes.byref(avail), None)
                if not ok or avail.value > 0:
                    ready.append((key, 1))
            if ready or time.monotonic() >= end:
                return ready
            time.sleep(0.005)


task = sys.argv[1]
spec = importlib.util.spec_from_file_location("emit_under_test", os.path.join(task, "tests", "emit.py"))
emit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(emit)
emit.selectors = types.SimpleNamespace(DefaultSelector=PeekSelector, EVENT_READ=1)
os.killpg = lambda pid, sig: None
base_env = emit.program_env
emit.program_env = lambda: {**base_env(), "SYSTEMROOT": os.environ["SYSTEMROOT"]}
py = sys.executable


def case(label, code, expect):
    t0 = time.monotonic()
    try:
        got = emit.run_case(py, ["-c", code])
        outcome = "ok rc=%d stdout=%d bytes" % (got["rc"], len(got["stdout"]))
        kind = "ok"
    except Exception as exc:  # noqa: BLE001
        outcome, kind, got = "%s: %s" % (type(exc).__name__, exc), type(exc).__name__, None
    verdict = "PASS" if kind == expect else "FAIL"
    print("%s  %-34s %-6.1fs %s" % (verdict, label, time.monotonic() - t0, outcome))
    return got


JSON_OUT = "import sys,json; sys.stdout.write(json.dumps({'x': 1}) + chr(10))"
got = case("3 MiB of stderr, small JSON stdout",
           JSON_OUT + "; [sys.stderr.write('e' * 65536) for _ in range(48)]", "ok")
assert got and json.loads(got["stdout"]) == {"x": 1}
case("exactly 1048576 bytes of stdout", "import sys; sys.stdout.write('a' * 1048576)", "ok")
case("1048577 bytes of stdout", "import sys; sys.stdout.write('a' * 1048577)", "ValueError")
case("1.5 MiB of stdout", "import sys; [sys.stdout.write('a' * 65536) for _ in range(24)]", "ValueError")
emit.CASE_TIMEOUT_SEC = 3
case("sleeps past a 3 s deadline", "import time; time.sleep(30)", "TimeoutError")
emit.CASE_TIMEOUT_SEC = 630
session = os.path.join(task, "environment", "data", "sessions", "e2")
t0 = time.monotonic()
got = emit.run_case(py, ["-B", os.path.join(task, "solution", "reduce.py"), session])
res = json.loads(got["stdout"])
print("PASS  oracle on e2 through run_case        %-6.1fs rc=%d, members %s" % (
    time.monotonic() - t0, got["rc"], sorted(res)) if got["rc"] == 0 else "FAIL  oracle rc %d" % got["rc"])
