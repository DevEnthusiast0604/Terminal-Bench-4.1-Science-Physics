#!/usr/bin/env python3
"""The README `## Task Metadata` block exactly as terminal-bench v4.1.0 renders and checks it
(scripts/checks/check-task-fields.sh at tag v4.1.0, commit 4070d6cef56a7d20cb5dc98d5e10ada88a6b9440,
Apache-2.0). The values are the upstream code's; only the packaging into functions is ours.

4.1 compares every line of the block with task.toml as text, so the format matters, not only the
numbers: the author is `Name (email)`, organizations follow a ` | `, the category is the domain
alone in backticks (no subcategory), hours always read "hours", and a GPUs line appears only when
[environment].gpus is set. A label that task.toml does not produce fails too.

    expected(doc)              {label: value} for the block, in order; ValueError names a missing field
    render(doc)                the block's text
    findings(doc, readme_text) [(line, message)]: every difference 4.1 would fail on, empty when none
                               (and empty when task.toml lacks a field: the schema checks report that)

Stdlib only.
"""
from __future__ import annotations

import re

HEADING = "## Task Metadata"


def _as_list(value):
    return value if isinstance(value, list) else [value]


def _number(value, divisor=1) -> str:
    value = float(value) / divisor
    return str(int(value)) if value.is_integer() else str(value)


def expected(doc: dict) -> dict:
    md = doc.get("metadata") or {}
    agent = doc.get("agent") or {}
    env = doc.get("environment") or {}
    missing = [k for k in ("author_name", "author_email", "category", "tags", "expert_time_estimate_hours")
               if k not in md]
    missing += [shown for shown, section, key in (("[agent].timeout_sec", agent, "timeout_sec"),
                                                   ("[environment].cpus", env, "cpus"),
                                                   ("[environment].memory_mb", env, "memory_mb"))
                if key not in section]
    if missing:
        raise ValueError("task.toml is missing: %s" % ", ".join(missing))
    names, emails = _as_list(md["author_name"]), _as_list(md["author_email"])
    if len(names) != len(emails):
        raise ValueError("task.toml author_name and author_email must have the same length")
    author = ", ".join("%s (%s)" % (n, e) for n, e in zip(names, emails))
    if md.get("author_organization"):
        author += " | " + ", ".join(dict.fromkeys(_as_list(md["author_organization"])))
    out = {
        "Author": author,
        "Category": "`%s`" % md["category"],
        "Tags": " ".join("<code>%s</code>" % t for t in md["tags"]),
        "Expert time": "%s hours" % _number(md["expert_time_estimate_hours"]),
        "Agent timeout": "%s hours" % _number(agent["timeout_sec"], 3600),
        "CPUs": _number(env["cpus"]),
        "Memory": "%s GB" % _number(env["memory_mb"], 1024),
    }
    if env.get("gpus", 0):
        out["GPUs"] = _number(env["gpus"])
    return out


def render(doc: dict) -> str:
    return "\n".join([HEADING, ""] + ["- **%s:** %s" % kv for kv in expected(doc).items()]) + "\n"


def findings(doc: dict, readme_text: str) -> list[tuple[int | None, str]]:
    try:
        want = expected(doc)
    except ValueError:
        return []
    lines = readme_text.splitlines()
    try:
        start = lines.index(HEADING) + 1
    except ValueError:
        return [(None, "no %s section" % HEADING)]
    actual, where, out = {}, {}, []
    for n, line in enumerate(lines[start:], start + 1):
        if line.startswith("## "):
            break
        m = re.fullmatch(r"- \*\*(.+?):\*\* (.*)", line)
        if not m:
            continue
        label, value = m.groups()
        if label in actual:
            out.append((n, "duplicate %s line" % label))
            continue
        actual[label], where[label] = value, n
    for label, value in want.items():
        if actual.get(label) == value:
            continue
        if label == "Author":   # never echo addresses: lint output ships in evidence/, where the email rule fails them
            out.append((where.get(label, start), "Author is not `Name (email)` as task.toml declares it"
                        + ("" if label in actual else " (no Author line)")))
        else:
            out.append((where.get(label, start), "%s is %r; 4.1 expects %r" % (label, actual.get(label), value)))
    for label in actual.keys() - want.keys():
        out.append((where[label], "%s is not a 4.1 metadata line" % label))
    return out
