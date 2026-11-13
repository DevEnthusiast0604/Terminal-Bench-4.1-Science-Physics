# Kater pendulum, release runs

A rigid steel bar carries two knife-edge pivots, A and B, facing each other, and a movable
mass. The bar was hung on one knife edge at a time, always on the same agate support, and
released from rest. Runs a1, a2, a3 hang on edge A; runs b1, b2, b3 hang on edge B. Before each
release an electromagnetic catch held the bar still at a chosen angle, on one side of the
vertical or the other; the release angles were not measured and differ from run to run. A
camera filmed each swing and a tracker logged the bar angle per frame.

## Geometry (measured, SI units)

These two lengths were measured once and apply to every run.

    knife_edge_separation_m = 1.00003
    centre_of_mass_from_edge_a_m = 0.20011

The centre of mass lies between the two edges, on the line joining them. The first value is the
distance between the edges; the second is the distance from edge A to the centre of mass, found
by balancing the bar on a third edge.

## Camera

One camera on a tripod filmed all six runs. It does not look square-on at the plane of the
swing: it stands off to one side of the stand and above the bar, turned about the vertical and
tilted down towards the bar, by angles that were not measured. Its lens is a long telephoto, so
the picture is a parallel (orthographic) projection of the scene to well within the tracker's
accuracy. The camera may also be slightly rolled about its own optical axis. The tracker measures
the angle of the bar's image in the picture, from the picture's vertical axis, and makes no
correction for the oblique view. The camera, its tripod and the stand were not moved during the
session, so the same view applies to every run. No angle calibration of the camera was made.

## Files

    /app/data/runs/<run>.csv    tracker log, one row per frame the tracker received
    /app/data/sync/<run>.csv    camera clock check for the same run

### /app/data/runs/<run>.csv

Leading lines that start with `#` are metadata: `unit` is the angle unit used in this file and
`nominal_fps` is the frame rate the camera is set to. Then a header row and one row per frame:

    frame_counter   the camera's hardware frame counter, 16 bits, counting each frame delivered
                    to the tracker; no time stamps are recorded
    theta           angle of the bar's image from the picture's vertical axis, in the unit named
                    in the header
    tracker_ok      1 when the tracker found the bar in that frame; 0 when it lost the bar, in
                    which case theta repeats the last good value

Each log starts while the catch still holds the bar, so its first rows show the bar at rest at
the release angle; the catch lets go between half a second and a second and a half into the log.

### /app/data/sync/<run>.csv

The camera's own oscillator is free-running and is not locked to anything. To check it, an LED
in the camera's view is switched on by a GPS-disciplined pulse at the start of every GPS second.
`gps_s` is the whole GPS second and `frame_counter` is the counter value of the first frame in
which the LED was seen lit. The detector occasionally misses a second; those rows are absent.

## Damping

The bar loses amplitude through air drag and pivot friction; both are small, but at the larger
release angles the swing decays noticeably over a run.
