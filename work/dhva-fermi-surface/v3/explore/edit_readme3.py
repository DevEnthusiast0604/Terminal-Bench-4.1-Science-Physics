import textwrap
from pathlib import Path
p = Path("tasks/active/dhva-fermi-surface/README.md")
t = p.read_text(encoding="utf-8")

def sub(old, new):
    global t
    assert t.count(old) == 1, old[:70]
    t = t.replace(old, new)

sub("""- **A heavy orbit seen only at high field.** δ (7415 T, mass 3.35) is damped below 20 T by scattering and above 2 K by
  temperature. It is a clear peak only in a high-field spectrum of the coldest sweep (7414.5 T, signal to noise 21, over
  22-35 T); it is absent from the 6-35 T spectrum and from both spectra of the whole sweep [2]. An inventory from the
  6-35 T window alone never reports it [4].""",
"""- **A heavy orbit seen only at high field.** δ (7300 T, mass 3.35) is damped below 20 T by scattering and above 2 K by
  temperature. It is a clear peak only in a high-field spectrum of the coldest sweep (7299.9 T, signal to noise 23, over
  22-35 T); it is absent from the 6-35 T spectrum and from both spectra of the whole sweep [2]. An inventory from the
  6-35 T window alone never reports it [4]. Nothing else explains it: the nearest harmonic of another orbit, 8 x γ, is
  120.8 T above it, and of the integer combinations of the other orbits that come within 0.1% of its frequency, none
  has a summed mass within 15% of its own [1].""")

sub("""- **0.5% on frequencies.** The reference is within 0.009% on every frequency [3], and within 0.024% on the further
  draws [5].""", """- **0.5% on frequencies.** The reference is within 0.002% on every frequency [3], and within 0.005% on the further
  draws [5].""")

i = t.index("- **15% on masses.**")
j = t.index("\n\nWhat the checks leave out")
new_mass = ("- **15% on masses.** The reference is within 1.6% on the shipped sweeps for every orbit but δ, the weakest, at "
            "-3.7% [3]. On the further draws it stays within 1.6% for every orbit but δ, at -0.01, +2.8 and -4.4% [5]. "
            "The textbook route, Fourier peak heights with R_T at the window's mean in 1/B, lands within 9.5% for every "
            "orbit but γ over 14-35 T [4]. The band rejects γ's mass from the blended peak (346 to 446% too heavy) and a "
            "harmonic's mass taken for its orbit's (twice the right value); the arithmetic-mean field over 14-35 T puts "
            "α and the β neck outside it, 17 and 16% too heavy [4].")
w = textwrap.wrap(new_mass[2:], width=118, break_on_hyphens=False, break_long_words=False)
t = t[:i] + "\n".join(["- " + w[0]] + ["  " + x for x in w[1:]]) + t[j:]

sub("The reference takes about 14 minutes on one CPU [3],", "The reference takes about 31 minutes on one CPU [3],")
p.write_text(t, encoding="utf-8", newline="\n")
print("ok")
