"""2026-11-09 18:0x: v4 uploaded (T-1383 v4, quick check queued 18:02); tool and procedure points. Adds only."""
import datetime

HM = datetime.datetime.now(datetime.timezone.utc).strftime("%H:%M")
points = (
    "- (%s) v4 is up: T-1383 v4, IN REVIEW, quick check queued at 18:02 (upload 2 of 5 on 11-09, no note; digest "
    "`eebfdfcc…8e47`; v3's zip archived as `gamma-decay-scheme-v3-20261109.zip`). The poller watches T-1383 again.\n"
    "- (%s) `supertasker.py upload-fix` on TB4.1: update cards carry \"Upload the fixed task\" buttons, so it now clicks "
    "the task view's one exact \"Upload the fix\" button, and it stops unanswered if the platform's \"Why upload it "
    "anyway\" dialog (`#ask`) opens. `release.sh` stopped at the upload this time (the old click found three buttons): "
    "the zip was packaged and v3 archived, so the upload and `log_release.py` were run by hand rather than running "
    "`release.sh` again, which would have archived the new zip as v3. CLAUDE.md now says so.\n") % (HM, HM)
p = "logs/BRIEFING.md"
s = open(p, encoding="utf-8", newline="").read()
open(p, "w", encoding="utf-8", newline="").write(s.rstrip("\n") + "\n" + points)
print("done", HM)
