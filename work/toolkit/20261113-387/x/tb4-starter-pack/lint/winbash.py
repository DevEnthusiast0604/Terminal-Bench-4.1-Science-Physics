"""Resolve a real bash, never Windows' WSL launcher stub.

subprocess.run(["bash", ...]) passes a bare command name. On Windows, CreateProcess
searches the Windows system directory (System32) before PATH regardless of PATH order, so a
machine with WSL installed silently gets System32's bash.exe (a WSL launcher) instead of Git
Bash, and the command fails inside WSL with no useful error ("execvpe(/bin/bash) failed: No
such file or directory") even when a working bash is earlier on PATH.

bash() walks PATH itself and returns the first hit outside the system directory; TB4_BASH
overrides. Unaffected off Windows. Every caller in this package that runs a .sh script should
use bash() in place of the literal "bash".

This is a duplicate of tbench_assess.winbash on purpose: starter-pack ships as a standalone
zip with no Python dependency on tbench-assess, so it can't import across that package
boundary. Keep the two in sync (same PATH-only resolution, no guessing at common install
locations) if either changes.
"""
from __future__ import annotations

import os
import sys


def bash() -> str:
    override = os.environ.get("TB4_BASH")
    if override:
        return override
    if sys.platform != "win32":
        return "bash"
    sysroot = os.path.normcase(os.environ.get("SystemRoot", r"C:\Windows"))
    for d in os.environ.get("PATH", "").split(os.pathsep):
        if not d:
            continue
        if os.path.normcase(os.path.normpath(d)).startswith(sysroot):
            continue
        for name in ("bash.exe", "bash"):
            cand = os.path.join(d, name)
            if os.path.isfile(cand):
                return cand
    return "bash"
