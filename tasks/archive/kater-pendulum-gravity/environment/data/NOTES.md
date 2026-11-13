# Kater pendulum: release sessions

A rigid steel bar carries two pivots, A and B, facing each other, a fixed brass bob near pivot A and two
sliding weights, heavy and light, that lock at any position along the bar. In a session the bar is hung on
one pivot at a time, always on the same stand, and released from rest a few times on each pivot. Before
each release an electromagnetic catch holds the bar still at a chosen angle, on one side of the vertical
or the other; the release angles are not measured and differ from run to run. A camera films each swing
and a tracker logs the bar's angle in every frame.

## Pivots

The stand carries two flat, level agate plates, one on either side of the bar, and the pivot in use rests
on both. A pivot is either a knife edge, ground sharp, or a hardened steel dowel pin pressed through the
bar at right angles to it and parallel to the other pivot (the workshop replaces a chipped edge with a
pin). When the bar hangs on a pin, the two ends of the pin rest on the agate plates, and as the bar
swings the pin rolls on them without slipping.

Every length along the bar is measured along its axis from a pivot's rest line: for a knife edge, its
edge; for a pin, the line of the pin's surface that faces the other pivot, which is the line on which the
pin rests on the plates when the bar hangs on it. The centre of mass lies on the bar's axis, between the
two pivots.

## session.json

The session's record, typed up at the end of the day from the operator's paper logbook:

    date                                   the day of the runs
    pivots.a, pivots.b                     {"kind": "knife_edge"} or {"kind": "pin", "pin_diameter_m": d},
                                           d measured with a micrometer
    pivot_separation_m                     from pivot A's rest line to pivot B's, gauge blocks
    centre_of_mass.from_pivot_a_m          from pivot A's rest line to the centre of mass, found by
                                           balancing the bar across a third knife edge
    centre_of_mass.balanced_on             the day of that balance
    centre_of_mass.weight_marks_m          {"heavy": m, "light": m}: where the weights were locked for it
    weights.heavy, weights.light           {"mass_kg": m, "mark_m": x}: each weight's mass, and where it was
                                           locked for this session's runs
    bar_mass_kg                            the whole bar as swung, with its pins or edges, the bob and both
                                           weights, workshop scale
    runs                                   {"<run>": "a" or "b"}: every run of the session, with the pivot
                                           the operator wrote down for it in the logbook

A weight's mark is the distance of its centre from pivot A's rest line, along the bar. The balance may
have been made on an earlier day, with the weights where they were then; the weights were locked at their
marks for the runs before the first run and were not touched during the session. The operator names the
runs after the pivot written down for them: a1, a2, ... and b1, b2, ....

## Camera

One camera on a tripod films every run of a session. It is placed afresh for each session and is not
moved during it, so the same view applies to all the runs of a session. In general it does not look
square-on at the plane of the swing: it stands off to one side of the stand and above the bar, turned
about the vertical and tilted down towards the bar, by angles that are not measured. Its lens is a long
telephoto, so the picture is a parallel (orthographic) projection of the scene to well within the
tracker's accuracy. The camera may also be slightly rolled about its own optical axis. The tracker
measures the angle of the bar's image in the picture, from the picture's vertical axis, and makes no
correction for the view. No angle calibration of the camera is made.

## Files of a session

    session.json          the session's record (above)
    runs/<run>.csv        tracker log, one row per frame the tracker received
    sync/<run>.csv        camera clock check for the same run

### runs/<run>.csv

Leading lines that start with `#` are metadata: `run` is the run's name, `unit` is the angle unit used in
this file (`deg` or `rad`) and `nominal_fps` is the frame rate the camera is set to. Then a header row and
one row per frame:

    frame_counter   the camera's hardware frame counter, 16 bits, counting each frame delivered to the
                    tracker; no time stamps are recorded
    theta           angle of the bar's image from the picture's vertical axis, in the unit named in the
                    header
    tracker_ok      1 when the tracker found the bar in that frame; 0 when it lost the bar, in which case
                    theta repeats the last good value

Each log starts while the catch still holds the bar, so its first rows show the bar at rest at the release
angle; the catch lets go between half a second and a second and a half into the log.

### sync/<run>.csv

The camera's own oscillator is free-running and is not locked to anything. To check it, an LED in the
camera's view is switched on by a GPS-disciplined pulse at the start of every GPS second. `gps_s` is the
whole GPS second and `frame_counter` is the counter value of the first frame in which the LED was seen
lit. The detector occasionally misses a second; those rows are absent.

Now and then the camera's sensor stalls and loses a few consecutive frames. Those frames are never
delivered and the counter does not count them, so the frames either side of a stall have consecutive
counter values although more time passed between them.

## Damping

The bar loses amplitude through air drag and pivot friction; both are small, but at the larger release
angles the swing decays noticeably over a run.

## How sessions differ

Every session follows the description above. Within it, these differ from session to session, within
these limits:

- each pivot is a knife edge or a pin, of 1.5 to 4 mm diameter: a session may have a pin on A, on B, on
  both or on neither;
- the weights' marks for the runs, and the day and the marks of the balance;
- the bar hangs on each pivot for two to four runs of the session; releases are between 0.2 and 0.9 rad
  from the vertical, on either side, and in every session at least one run is released beyond 0.6 rad;
- the logbook's pivots: the pivot written down for a run, and with it the run's name, may be the wrong one,
  for any number of a session's runs;
- the camera: turned about the vertical by up to 35 degrees either way, tilted down by 0 to 25 degrees and
  rolled by up to 0.03 rad either way; it may also look square-on;
- the camera's frame rate is within 0.6 % of the nominal 240 frames per second, and differs a little from
  run to run;
- a run has up to three sensor stalls, each of 2 to 15 frames, all at least 5 s after the release and 5 s
  before the end of the log; a stall never swallows the first lit frame of an LED second;
- the LED detector misses a few per cent of the seconds, rarely more than one in ten;
- the log of a run lasts 60 to 120 s, the catch lets go 0.5 to 1.5 s into it, and its angles are in degrees
  or in radians;
- the tracker loses the bar for a few per cent of the frames, in bursts of a few to a few tens of frames.
