import ephem
import numpy as np
import logging
from pytz import utc
from scipy.ndimage import gaussian_filter

def plot_milky_way(ax, observer, local_dt, local_tz):
    """
    Render the Milky Way as a soft luminous band along the galactic plane
    with a dithered star-like texture to mimic unresolved stars.
    """
    utc_dt = local_dt.astimezone(utc)

    obs = ephem.Observer()
    obs.lat, obs.lon, obs.elev = observer.lat, observer.lon, observer.elev
    obs.date = utc_dt.strftime('%Y/%m/%d %H:%M:%S')

    # Build a grid of galactic coordinates
    num_l = 720
    num_b = 60

    l_vals = np.linspace(0, 360, num_l)
    b_vals = np.linspace(-15, 15, num_b)

    # Brightness profile across galactic latitude (gaussian centered on plane)
    b_brightness = np.exp(-0.5 * (b_vals / 5.0) ** 2)

    # Brightness profile along galactic longitude
    def longitude_brightness(l):
        return 0.15 + 0.85 * np.exp(-0.5 * ((l - 360 * (l > 180).astype(float)) / 60) ** 2)

    # Create the alt/az image grid
    az_bins = 360
    alt_bins = 90
    mw_image = np.zeros((alt_bins, az_bins))

    for i, l in enumerate(l_vals):
        l_bright = longitude_brightness(np.array([l]))[0]

        for j, b in enumerate(b_vals):
            gal = ephem.Galactic(np.radians(l), np.radians(b))
            eq = ephem.Equatorial(gal)

            body = ephem.FixedBody()
            body._ra = eq.ra
            body._dec = eq.dec
            body.compute(obs)

            alt_deg = np.degrees(float(body.alt))
            az_deg = np.degrees(float(body.az))

            if alt_deg <= 0:
                continue

            az_centered = ((az_deg - 180) % 360) - 180

            ax_idx = int((az_centered + 180) / 360 * az_bins)
            ay_idx = int(alt_deg / 90 * alt_bins)

            ax_idx = min(ax_idx, az_bins - 1)
            ay_idx = min(ay_idx, alt_bins - 1)

            brightness = l_bright * b_brightness[j]
            mw_image[ay_idx, ax_idx] = max(mw_image[ay_idx, ax_idx], brightness)

    # Apply gaussian blur to smooth the band
    mw_image = gaussian_filter(mw_image, sigma=(3, 5))

    # Normalize
    if mw_image.max() > 0:
        mw_image = mw_image / mw_image.max()

    # --- Dither texture: scattered faint "stars" weighted by MW brightness ---
    rng = np.random.default_rng(42)  # fixed seed for consistency
    dither = np.zeros((alt_bins, az_bins))
    num_dither_stars = 8000
    dy = rng.integers(0, alt_bins, num_dither_stars)
    dx = rng.integers(0, az_bins, num_dither_stars)
    # Only place dither stars where there's MW brightness
    for k in range(num_dither_stars):
        if mw_image[dy[k], dx[k]] > 0.05:
            # Brightness proportional to MW intensity with random variation
            dither[dy[k], dx[k]] = mw_image[dy[k], dx[k]] * rng.uniform(0.3, 1.0)

    # Light blur on dither to give stars a slight spread
    dither = gaussian_filter(dither, sigma=0.6)

    # Combine: smooth glow + dither stars
    combined = mw_image * 0.7 + dither * 0.5
    if combined.max() > 0:
        combined = combined / combined.max()

    # Create RGBA image with blue-white tint
    # Alpha at 50% of original (0.18 * 0.5 = 0.09)
    rgba = np.zeros((alt_bins, az_bins, 4))
    rgba[:, :, 0] = 0.7   # R
    rgba[:, :, 1] = 0.75  # G
    rgba[:, :, 2] = 1.0   # B
    rgba[:, :, 3] = combined * 0.09

    # Render the Milky Way band
    ax.imshow(rgba, extent=[-180, 180, 0, 90], aspect='auto', origin='lower',
              zorder=1, interpolation='bilinear')

    logging.info("Milky Way band rendered")
