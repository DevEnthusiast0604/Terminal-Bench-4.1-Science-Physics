- **2% on periods.** The reference is within 0.87% on every period: e at 114.29 d, the other three within 0.05%.
  Under four other noise models e's period runs from 113.34 to 114.42 d (-1.7 to -0.8%) and c's from 17.634 to
  17.652 d, and d's and b's hardly move (`[the same planets under other noise models: period, K, e]`). The band
  rejects every one-day alias, the one-year aliases of c (-4.6 and +5.1%) and e (-24.0 and +46.1%), and half the
  rotation, 2.9% below c (`[other routes]`). It accepts the one-year aliases of d and b, 0.3% and 0.8% away: a census
  that picks one of those has still found the planet.
- **25% on semi-amplitudes and minimum masses.** The reference is within 8.0% on K and 12.0% on minimum mass, the
  largest error being c's, whose eccentricity it fits at 0.30 against 0.07. Under the other noise models the
  semi-amplitudes stay within 12% of the right ones (c from 2.65 to 2.89 m/s, e from 3.20 to 3.47 m/s). The band is
  wider because the activity model is a choice the data do not settle, and a loosely fixed eccentricity moves the
  minimum mass.
- **8% on radii.** RADIUS
- **10% on the rotation period.** The reference gives 34.32 d, 0.1% off, and the spot belt's latitudes rotate at
  34.05 to 34.68 d, -0.7 to +1.2% (`[rotation and the activity process]`). The band rejects the Hα index's highest
  periodogram peak (42.81 d, +24.9%), its third (64.22 d) and the dLW and CRX peaks near 11 d. It accepts the index's
  second peak, 32.92 d (-4.0%).

What the checks leave out: they do not ask how the census was reached, so any route through the data that lands on
these numbers scores 1. They do not grade eccentricities, arguments of periastron, transit times, impact parameters or
uncertainties, which the census does not need. Only one realization of the noise exists, because the task is a single
fixed set of files, so the bands are calibrated on it and the margins above are stated rather than a spread over
seeds. The census's limits exclude nothing the system holds: its periods run from 1.2196 to 115.30 d and its
semi-amplitudes from 1.75 to 3.30 m/s (`tests/expected.json`). They do exclude the next signal the reference's search
meets, 3.011 d with K 0.83 ± 0.19 m/s in the visible velocities, which also raises the log-likelihood by only 11.6, below the search's threshold of 15
(`[the radial-velocity search, step by step]`).
