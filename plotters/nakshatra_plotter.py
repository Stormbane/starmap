import ephem
import numpy as np
import logging
from pytz import utc

# The 27 Nakshatras with their sidereal longitude start points
# Each spans 13°20' (13.3333... degrees)
NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira",
    "Ardra", "Punarvasu", "Pushya", "Ashlesha", "Magha",
    "P.Phalguni", "U.Phalguni", "Hasta", "Chitra", "Swati",
    "Vishakha", "Anuradha", "Jyeshtha", "Mula", "P.Ashadha",
    "U.Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
    "P.Bhadra", "U.Bhadra", "Revati",
]

NAKSHATRA_SPAN = 360.0 / 27.0  # 13.3333... degrees


def get_ayanamsa(year):
    """
    Approximate Lahiri ayanamsa for a given year.
    The ayanamsa increases by ~50.3 arcseconds per year.
    Reference: 2000.0 = 23.856 degrees (Lahiri).
    """
    return 23.856 + (year - 2000) * 50.3 / 3600.0


def sidereal_to_tropical(sidereal_lon, ayanamsa):
    """Convert sidereal ecliptic longitude to tropical."""
    return (sidereal_lon + ayanamsa) % 360.0


def get_moon_nakshatra(observer, local_dt):
    """Get the nakshatra the Moon currently occupies."""
    utc_dt = local_dt.astimezone(utc)
    obs = ephem.Observer()
    obs.lat, obs.lon, obs.elev = observer.lat, observer.lon, observer.elev
    obs.date = utc_dt.strftime('%Y/%m/%d %H:%M:%S')

    moon = ephem.Moon()
    moon.compute(obs)

    # Get Moon's ecliptic longitude
    ecl = ephem.Ecliptic(moon)
    moon_tropical_lon = np.degrees(float(ecl.lon))

    # Convert to sidereal
    ayanamsa = get_ayanamsa(local_dt.year)
    moon_sidereal_lon = (moon_tropical_lon - ayanamsa) % 360.0

    # Determine nakshatra index
    nakshatra_idx = int(moon_sidereal_lon / NAKSHATRA_SPAN)
    return nakshatra_idx, NAKSHATRAS[nakshatra_idx], moon_sidereal_lon


def ecliptic_to_altaz(tropical_lon, observer, obs):
    """Convert a tropical ecliptic longitude (lat=0) to alt/az."""
    ecl = ephem.Ecliptic(np.radians(tropical_lon), 0)
    eq = ephem.Equatorial(ecl, epoch=obs.date)

    body = ephem.FixedBody()
    body._ra = eq.ra
    body._dec = eq.dec
    body.compute(obs)

    return np.degrees(float(body.alt)), np.degrees(float(body.az))


def center_azimuth(azimuth):
    """Convert from 0-360 to -180 to 180 with North at 0."""
    return (azimuth - 180) % 360 - 180


def plot_nakshatras(ax, observer, local_dt, local_tz):
    """
    Draw the ecliptic line with nakshatra boundaries and labels.
    Highlights the Moon's current nakshatra.
    """
    utc_dt = local_dt.astimezone(utc)
    obs = ephem.Observer()
    obs.lat, obs.lon, obs.elev = observer.lat, observer.lon, observer.elev
    obs.date = utc_dt.strftime('%Y/%m/%d %H:%M:%S')

    ayanamsa = get_ayanamsa(local_dt.year)
    moon_idx, moon_nakshatra, moon_sid_lon = get_moon_nakshatra(observer, local_dt)

    # --- Draw the ecliptic line ---
    # Sample 360 points along the ecliptic (tropical longitude 0-360, lat=0)
    ecl_lons = np.linspace(0, 360, 361)
    ecl_az = []
    ecl_alt = []

    for lon in ecl_lons:
        alt, az = ecliptic_to_altaz(lon, observer, obs)
        if alt > 0:
            ecl_az.append(center_azimuth(az))
            ecl_alt.append(alt)
        else:
            ecl_az.append(np.nan)
            ecl_alt.append(np.nan)

    ecl_az = np.array(ecl_az)
    ecl_alt = np.array(ecl_alt)

    # Split at large azimuth jumps (wrapping) and NaN gaps
    # Plot segments without connecting wrapped portions
    valid = ~np.isnan(ecl_az)
    if np.any(valid):
        # Find segments
        segments = []
        seg_az, seg_alt = [], []
        for i in range(len(ecl_az)):
            if valid[i]:
                if len(seg_az) > 0 and abs(ecl_az[i] - seg_az[-1]) > 150:
                    # Azimuth wrap - start new segment
                    if len(seg_az) > 1:
                        segments.append((np.array(seg_az), np.array(seg_alt)))
                    seg_az, seg_alt = [ecl_az[i]], [ecl_alt[i]]
                else:
                    seg_az.append(ecl_az[i])
                    seg_alt.append(ecl_alt[i])
            else:
                if len(seg_az) > 1:
                    segments.append((np.array(seg_az), np.array(seg_alt)))
                seg_az, seg_alt = [], []
        if len(seg_az) > 1:
            segments.append((np.array(seg_az), np.array(seg_alt)))

        for seg_az_arr, seg_alt_arr in segments:
            ax.plot(seg_az_arr, seg_alt_arr, color='#DAA520', linewidth=0.6,
                    alpha=0.5, zorder=3, linestyle='-')

    # --- Draw nakshatra boundaries and labels ---
    for i in range(27):
        # Boundary at start of each nakshatra (sidereal longitude)
        boundary_sidereal = i * NAKSHATRA_SPAN
        boundary_tropical = sidereal_to_tropical(boundary_sidereal, ayanamsa)

        alt, az = ecliptic_to_altaz(boundary_tropical, observer, obs)
        if alt > 0:
            az_c = center_azimuth(az)
            # Draw a small tick mark perpendicular to ecliptic
            ax.plot([az_c, az_c], [alt - 1.0, alt + 1.0],
                    color='#DAA520', linewidth=0.5, alpha=0.6, zorder=3)

        # Label at midpoint of each nakshatra
        mid_sidereal = boundary_sidereal + NAKSHATRA_SPAN / 2.0
        mid_tropical = sidereal_to_tropical(mid_sidereal, ayanamsa)
        alt_m, az_m = ecliptic_to_altaz(mid_tropical, observer, obs)

        if alt_m > 2:  # Only label if reasonably above horizon
            az_mc = center_azimuth(az_m)
            is_moon_nakshatra = (i == moon_idx)

            label_color = '#FFD700' if is_moon_nakshatra else '#8B7536'
            label_alpha = 1.0 if is_moon_nakshatra else 0.6
            fontweight = 'bold' if is_moon_nakshatra else 'normal'
            fontsize = 7 if is_moon_nakshatra else 5.5

            name = NAKSHATRAS[i]
            if is_moon_nakshatra:
                name = f"\u263D {name}"  # Moon symbol prefix

            ax.text(az_mc, alt_m + 2.0, name, color=label_color,
                    fontsize=fontsize, ha='center', va='bottom',
                    fontweight=fontweight, alpha=label_alpha, zorder=7)

    logging.info(f"Nakshatras rendered. Moon in {moon_nakshatra} "
                 f"(sidereal {moon_sid_lon:.1f} deg)")
