"""v2: the selection rule the quick check asked for, stated in the instruction and kept consistent everywhere."""
from pathlib import Path

S = Path("tasks/active/gamma-decay-scheme")
RULE = "If more than one scheme agrees with the data, we want the one with the fewest levels."


def sub(path, old, new):
    t = path.read_text(encoding="utf-8")
    assert t.count(old) == 1, (path, old)
    path.write_text(t.replace(old, new), encoding="utf-8", newline="\n")


sub(S / "instruction.md",
    "and we need the daughter's level scheme from this run. The run's files",
    "and we need the daughter's level scheme from this run. " + RULE + " The run's files")

sub(S / "tests" / "requirements.json",
    """    {
      "id": "R10",
""",
    """    {
      "id": "R12",
      "quote": "%s",
      "tests": ["test_levels", "test_transitions_placed"]
    },
    {
      "id": "R10",
""" % RULE)

sub(S / "tests" / "test_outputs.py",
    """TB4_OUTPUT is the unpacked /app/output (the declared deliverable decay_scheme.json only) and TB4_EXPECTED
tests/expected.json, the decay scheme tests/generate.py built the data files from. Every test is listed under a
requirement in tests/requirements.json.
""",
    """TB4_OUTPUT is the unpacked /app/output (the declared deliverable decay_scheme.json only) and TB4_EXPECTED
tests/expected.json, the decay scheme tests/generate.py built the data files from, which is also the scheme with the
fewest levels that agrees with them (tests/checks.txt, [placement search]). Every test is listed under a requirement in
tests/requirements.json.
""")
sub(S / "tests" / "test_outputs.py",
    '''    """one entry per level, in any order, each within 0.5 keV of its level."""''',
    '''    """one entry per level of the scheme with the fewest levels, in any order, each within 0.5 keV of its level."""''')
sub(S / "tests" / "test_outputs.py",
    '''    """one entry per transition of the scheme, between the right two levels, and no other entry."""''',
    '''    """one entry per transition of that scheme, between the right two levels, and no other entry."""''')

# generate.py writes this line; checks.txt gets the same line by hand, so the generator need not run for it.
old = """                                                          ", extra level at %.1f keV" % extra[0] if extra else ""))
"""
new = old + """    out.append("instruction.md asks for the scheme with the fewest levels: the one with %d" % len(expected["levels_keV"]))
"""
sub(S / "tests" / "generate.py", old, new)
sub(Path("work/gamma-decay-scheme/v1/generate_draft.py"), old, new)
sub(S / "tests" / "checks.txt",
    "17 levels, 2 unseen transitions, extra level at 2917.5 keV\n",
    "17 levels, 2 unseen transitions, extra level at 2917.5 keV\n"
    "instruction.md asks for the scheme with the fewest levels: the one with 16\n")

sub(S / "README.md",
    """6. `search` places the lines exhaustively on levels, increasing the number of levels from two until a scheme exists.
""",
    """6. `search` places the lines exhaustively on levels, increasing the number of levels from two until a scheme exists,
   since the instruction wants the scheme with the fewest levels.
""")
sub(S / "README.md",
    """| `test_levels` | R1, R3, R8, R11 | the same number of levels, each within 0.5 keV of its level, in any order |
| `test_transitions_placed` | R1, R4, R5, R9, R11 | each right""",
    """| `test_levels` | R1, R3, R8, R11, R12 | the same number of levels, each within 0.5 keV of its level, in any order |
| `test_transitions_placed` | R1, R4, R5, R9, R11, R12 | each right""")
sub(S / "README.md",
    """calibrated on it and the margins above are stated rather than a spread over seeds. The level count has no band: the
search finds no scheme with 15 levels or fewer and one with 16, and with 17 it finds one more, which adds a level at
2917.5 keV and a second unseen transition that no peak calls for (`[placement search]`). An analyst does not add a
level the data do not need, so the instruction's "every level" means the 16. The `relative_intensity` floor of 0.5
excludes nothing the run could show: the weakest right transition in `tests/expected.json` is above 1.
""",
    """calibrated on it and the margins above are stated rather than a spread over seeds. The level count has no band: the
search finds no scheme with 15 levels or fewer and one with 16, and with 17 it finds one more, which adds a level at
2917.5 keV and a second unseen transition that no peak calls for (`[placement search]`). The data do not exclude that
extra level, so the instruction states the rule that decides: of the schemes that agree with the data, the one with the
fewest levels, which is how spectroscopists adopt a level, only when the data call for it. The rule selects the 16. The
`relative_intensity` floor of 0.5 excludes nothing the run could show: the weakest right transition in
`tests/expected.json` is above 1.
""")
print("done")
