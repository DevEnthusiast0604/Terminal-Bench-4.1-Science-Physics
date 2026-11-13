"""Exercise the task's tests/emit.py on Windows (author self-check, not shipped): its deliverable check, the
refusal path of main(), and main() running a stand-in transport.py on all ten cases through run_case.

select() takes only sockets on Windows, so a PeekNamedPipe-based stand-in replaces selectors, and killpg (absent
here) becomes a no-op; everything else is emit.py's own code (as in work/kater-pendulum-gravity/v12/explore).

    python -X utf8 -I -B test_emit_win.py <task_dir> <scratch_dir>
"""
import contextlib
import ctypes
import ctypes.wintypes as W
import importlib.util
import io
import json
import msvcrt
import os
import sys
import tempfile
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


task, scratch = sys.argv[1], sys.argv[2]
spec = importlib.util.spec_from_file_location("emit_under_test", os.path.join(task, "tests", "emit.py"))
emit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(emit)
emit.selectors = types.SimpleNamespace(DefaultSelector=PeekSelector, EVENT_READ=1)
os.killpg = lambda pid, sig: None
base_env = emit.program_env
emit.program_env = lambda: {**base_env(), "SYSTEMROOT": os.environ["SYSTEMROOT"]}
emit.PROGRAM = sys.executable          # absolute: os.path.join keeps it, as it keeps /usr/local/bin/python3
fails = 0


def check(label, ok, detail=""):
    global fails
    fails += not ok
    print("%s  %-52s %s" % ("PASS" if ok else "FAIL", label, detail))


def run_main(out):
    """emit.main() with TB4_OUTPUT = OUT and OUT as the working directory (test.sh cds there); its lines parsed."""
    os.environ["TB4_OUTPUT"], os.environ["TB4_CASE"], os.environ["TB4_CASE_DIR"] = out, "", ""
    buf, here = io.StringIO(), os.getcwd()
    os.chdir(out)
    try:
        with contextlib.redirect_stdout(buf):
            emit.main()
    finally:
        os.chdir(here)
    return [json.loads(l[len(emit.PREFIX):]) for l in buf.getvalue().splitlines() if l.startswith(emit.PREFIX)]


def fresh():
    return tempfile.mkdtemp(dir=scratch)


# 1. the deliverable check
out = fresh()
os.environ["TB4_OUTPUT"] = out
check("missing transport.py refused", emit.deliverable_problem() == "no transport.py was submitted",
      emit.deliverable_problem())
os.mkdir(os.path.join(out, "transport.py"))
with open(os.path.join(out, "transport.py", "__main__.py"), "w", newline="\n") as fh:
    fh.write("print('ran the folder')\n")
check("folder named transport.py refused", emit.deliverable_problem() == "transport.py is not a regular file",
      emit.deliverable_problem())
recs = run_main(out)
check("folder: every case emitted ok=False, nothing run",
      len(recs) == 10 and all(r["ok"] is False and r["error"].startswith("not run: ") for r in recs),
      "%d records, first: %s" % (len(recs), recs[0] if recs else None))
out = fresh()
with open(os.path.join(out, "transport.py"), "wb") as fh:
    fh.truncate(20971521)
os.environ["TB4_OUTPUT"] = out
check("20971521-byte transport.py refused", "more than 20971520" in (emit.deliverable_problem() or ""),
      emit.deliverable_problem())
with open(os.path.join(out, "transport.py"), "wb") as fh:
    fh.truncate(20971520)
check("20971520-byte transport.py accepted", emit.deliverable_problem() is None, emit.deliverable_problem())

# 2. main() on all ten cases with a stand-in program that echoes its arguments as the three quantities
out = fresh()
with open(os.path.join(out, "transport.py"), "w", newline="\n") as fh:
    fh.write("import json, sys\n"
             "a, t = float(sys.argv[1]), float(sys.argv[2])\n"
             "sys.stderr.write('progress\\n' * 1000)\n"
             "print(json.dumps({'viscosity': a, 'thermal_conductivity': t, 'self_diffusion': a + t}))\n")
t0 = time.monotonic()
recs = run_main(out)
by = {r["case"]: r for r in recs}
good = (sorted(by) == sorted(emit.CASES) and len(recs) == 10
        and all(by[c]["ok"] and by[c]["value"]["rc"] == 0
                and json.loads(by[c]["value"]["stdout"]) == {
                    "viscosity": float(emit.CASES[c][1]), "thermal_conductivity": float(emit.CASES[c][2]),
                    "self_diffusion": float(emit.CASES[c][1]) + float(emit.CASES[c][2])} for c in by))
check("stand-in program: ten observations, arguments passed", good,
      "%.1f s; k05 stdout %r" % (time.monotonic() - t0, by.get("k05", {}).get("value", {}).get("stdout")))
print("failures:", fails)
sys.exit(1 if fails else 0)
