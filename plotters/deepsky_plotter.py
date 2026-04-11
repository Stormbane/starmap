import ephem
import numpy as np
import logging
from pytz import utc

# Catalog of the brightest naked-eye deep sky objects
# RA in hours:min:sec, Dec in deg:min:sec, size in arcminutes, visual magnitude
DEEP_SKY_OBJECTS = [
    {
        "name": "Orion Nebula",
        "designation": "M42",
        "ra": "5:35:17",
        "dec": "-5:23:28",
        "size": 85,       # arcminutes
        "mag": 4.0,
        "color": (0.9, 0.5, 0.6),  # pinkish
        "type": "nebula",
    },
    {
        "name": "Pleiades",
        "designation": "M45",
        "ra": "3:47:00",
        "dec": "24:07:00",
        "size": 110,
        "mag": 1.6,
        "color": (0.6, 0.7, 1.0),  # blue haze
        "type": "cluster",
    },
    {
        "name": "LMC",
        "designation": "Large Magellanic Cloud",
        "ra": "5:23:35",
        "dec": "-69:45:22",
        "size": 650,       # very large
        "mag": 0.9,
        "color": (0.8, 0.8, 0.9),  # pale
        "type": "galaxy",
    },
    {
        "name": "SMC",
        "designation": "Small Magellanic Cloud",
        "ra": "0:52:45",
        "dec": "-72:49:43",
        "size": 320,
        "mag": 2.7,
        "color": (0.8, 0.8, 0.85),  # pale
        "type": "galaxy",
    },
    {
        "name": "\u03C9 Cen",
        "designation": "NGC 5139",
        "ra": "13:26:47",
        "dec": "-47:28:46",
        "size": 36,
        "mag": 3.7,
        "color": (1.0, 0.95, 0.8),  # warm white
        "type": "globular",
    },
    {
        "name": "47 Tuc",
        "designation": "NGC 104",
        "ra": "0:24:05",
        "dec": "-72:04:53",
        "size": 31,
        "mag": 4.1,
        "color": (1.0, 0.93, 0.75),  # warm
        "type": "globular",
    },
    {
        "name": "Ptolemy Cluster",
        "designation": "M7",
        "ra": "17:53:51",
        "dec": "-34:47:34",
        "size": 80,
        "mag": 3.3,
        "color": (0.9, 0.9, 1.0),  # white-blue
        "type": "cluster",
    },
    {
        "name": "Butterfly Cluster",
        "designation": "M6",
        "ra": "17:40:20",
        "dec": "-32:15:12",
        "size": 33,
        "mag": 4.2,
        "color": (0.9, 0.85, 1.0),  # white
        "type": "cluster",
    },
    {
        "name": "Carina Nebula",
        "designation": "NGC 3372",
        "ra": "10:43:48",
        "dec": "-59:52:00",
        "size": 120,
        "mag": 1.0,
        "color": (1.0, 0.55, 0.5),  # pinkish-red
        "type": "nebula",
    },
    {
        "name": "Jewel Box",
        "designation": "NGC 4755",
        "ra": "12:53:42",
        "dec": "-60:22:00",
        "size": 10,
        "mag": 4.2,
        "color": (0.7, 0.75, 1.0),  # blue
        "type": "cluster",
    },
]


def center_azimuth(azimuth):
    """Convert from 0-360 to -180 to 180 with North at 0."""
    return (azimuth - 180) % 360 - 180


def plot_deep_sky_objects(ax, observer, local_dt, local_tz):
    """
    Plot the brightest deep sky objects as soft fuzzy patches.
    Only renders objects currently above the horizon.
    """
    utc_dt = local_dt.astimezone(utc)
    obs = ephem.Observer()
    obs.lat, obs.lon, obs.elev = observer.lat, observer.lon, observer.elev
    obs.date = utc_dt.strftime('%Y/%m/%d %H:%M:%S')

    plotted = []

    for dso in DEEP_SKY_OBJECTS:
        body = ephem.FixedBody()
        body._ra = ephem.hours(dso["ra"])
        body._dec = ephem.degrees(dso["dec"])
        body.compute(obs)

        alt_deg = np.degrees(float(body.alt))
        az_deg = np.degrees(float(body.az))

        if alt_deg <= 0:
            continue

        az_c = center_azimuth(az_deg)
        color = dso["color"]

        # Scale size: angular size in arcminutes -> plot units
        # Cap angular size for rendering so extended objects don't dominate
        angular_size_deg = min(dso["size"], 120) / 60.0  # cap at 2 degrees for rendering

        # Brightness based on magnitude (brighter = more visible)
        mag = dso["mag"]
        base_alpha = max(0.03, min(0.12, 0.15 - mag * 0.025))

        # Extended objects (galaxies) get reduced alpha
        if dso["type"] == "galaxy":
            base_alpha *= 0.5

        # Render as layered scatter for soft glow effect
        layers = [
            (1.0, base_alpha * 1.2),
            (2.0, base_alpha * 0.5),
            (3.5, base_alpha * 0.15),
        ]

        for size_mult, alpha in layers:
            # Convert angular size to matplotlib scatter point size
            scatter_size = (angular_size_deg * size_mult * 20) ** 2
            scatter_size = max(scatter_size, 40)
            scatter_size = min(scatter_size, 15000)

            ax.scatter([az_c], [alt_deg], color=color, edgecolor='none',
                       s=scatter_size, alpha=alpha, zorder=2, marker='o')

        # Label
        ax.text(az_c, alt_deg - 1.5, dso["name"], color=(*color, 0.6),
                fontsize=5.5, ha='center', va='top', zorder=3,
                fontstyle='italic')

        plotted.append(dso["name"])

    if plotted:
        logging.info(f"Deep sky objects rendered: {', '.join(plotted)}")
    else:
        logging.info("No deep sky objects above horizon")
