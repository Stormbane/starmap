import ephem
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from pytz import timezone, utc
import logging
import json
import re
import matplotlib.colors as mcolors
from constellation_utils import get_constellation_full_name

# --- Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
NAKED_EYE_MAG_LIMIT = 6.5 # Apparent magnitude limit for naked eye visibility
LABEL_MAG_LIMIT = 1.5 # Show labels only for stars brighter than this magnitude

def temperature_to_color(temp_k):
    """
    Convert a star's temperature in Kelvin to an RGB color.
    
    Parameters:
    -----------
    temp_k : float or str
        Temperature in Kelvin
        
    Returns:
    --------
    str
        Color name or hex code
    """
    # Convert string to float if needed
    if isinstance(temp_k, str):
        try:
            temp_k = float(temp_k)
        except (ValueError, TypeError):
            # If conversion fails, return default color
            return '#FFFFFF'  # Default to white
    
    # Handle None or invalid values
    if temp_k is None or not isinstance(temp_k, (int, float)):
        return '#FFFFFF'  # Default to white
    
    # Now we can safely compare with numeric values
    if temp_k > 30000:
        return '#FFFFFF'  # Blue-white
    elif temp_k > 10000:
        # Blue to white
        ratio = (temp_k - 10000) / 20000
        return mcolors.to_hex((0.8 + 0.2*ratio, 0.8 + 0.2*ratio, 1.0))
    elif temp_k > 7500:
        return '#FFFFFF'  # White
    elif temp_k > 6000:
        # Yellow-white
        ratio = (temp_k - 6000) / 1500
        return mcolors.to_hex((1.0, 0.9 + 0.1*ratio, 0.8))
    elif temp_k > 5000:
        # Yellow
        ratio = (temp_k - 5000) / 1000
        return mcolors.to_hex((1.0, 0.8 + 0.2*ratio, 0.6))
    elif temp_k > 3500:
        # Orange
        ratio = (temp_k - 3500) / 1500
        return mcolors.to_hex((1.0, 0.6 + 0.2*ratio, 0.4))
    else:
        return '#FF4500'  # Red

def center_azimuth(azimuths):
    """Convert from 0-360 to -180 to 180 with North at 0."""
    return (azimuths - 180) % 360 - 180

def mark_star(ax, x, y, name, constellation, magnitude, color='white', y_offset=1.5, show_label=False, temp_k=None):
    """
    Mark a star on the plot with improved visual representation.

    Parameters:
    -----------
    ax : matplotlib.axes.Axes
        The axes to plot on.
    x : float
        Azimuth coordinate (centered, -180 to 180).
    y : float
        Altitude coordinate (0 to 90).
    name : str
        Name of the star.
    constellation : str
        Constellation of the star.
    magnitude : float
        Apparent magnitude of the star.
    color : str, optional
        Color of the star marker, by default 'white'.
    y_offset : float, optional
        Vertical offset for the label, by default 1.5.
    temp_k : float, optional
        Temperature in Kelvin, used to determine star color.
    """
    # --- Realistic Size Scaling ---
    # Stars brighter than the limit get exponentially larger sizes.
    # We use (NAKED_EYE_MAG_LIMIT - magnitude) as a measure of brightness excess.
    # Clamp magnitude to avoid issues with extremely bright (negative mag) or faint stars.
    clamped_mag = max(-2.0, min(magnitude, NAKED_EYE_MAG_LIMIT)) # Clamp between -2 and limit
    
    # Exponential scaling: size ~ (brightness_factor)^exponent
    # A base size for the faintest visible star, scaling up from there.
    # Adjust base_size and scale_power to control the visual range.
    base_size = 1.0 # Size of a star at the magnitude limit
    scale_power = 2.0 # How rapidly size increases with brightness (try 1.5 to 2.5)
    size = base_size + (NAKED_EYE_MAG_LIMIT - clamped_mag)**scale_power * 10 # Added a multiplier for visibility

    # Cap the size to prevent excessively large markers for very bright stars
    max_marker_size = 150
    size = min(size, max_marker_size)
    size = max(size, base_size) # Ensure minimum size

    # --- Realistic Alpha Scaling ---
    # Alpha decreases for fainter stars.
    # Make stars near the limit very faint.
    min_alpha = 0.1 # Minimum visibility for the faintest stars
    max_alpha = 1.0 # Maximum visibility for the brightest stars
    alpha_range = max_alpha - min_alpha
    
    # Linear scaling within the range, could also be non-linear
    alpha = min_alpha + alpha_range * ((NAKED_EYE_MAG_LIMIT - clamped_mag) / (NAKED_EYE_MAG_LIMIT - (-2.0))) # Normalize based on clamped mag range
    alpha = max(min_alpha, min(max_alpha, alpha)) # Clamp alpha between min and max

    if magnitude < LABEL_MAG_LIMIT:
        marker = '*'
    else:
        marker = '.'
    
    # Use temperature-based color if available
    if temp_k is not None:
        color = temperature_to_color(temp_k)

    # Plot the star with softer edges (edgecolor=None)
    ax.scatter([x], [y], color=color, edgecolor='none', marker=marker, s=size, zorder=5, alpha=alpha)

    # Add label only if the star is bright enough
    if magnitude < LABEL_MAG_LIMIT:
        label = f"{name} m={magnitude:.2f}" #({constellation})\n
        # Smaller font size for labels
        ax.text(x, y + y_offset, label, color=color, fontsize=8, ha='center', va='bottom', zorder=6)

def parse_ra_dec(ra_str, dec_str):
    """
    Parse RA and Dec strings into ephem-compatible format.
    
    Parameters:
    -----------
    ra_str : str
        Right ascension string (e.g., "12h 34m 56.7s" or "12:34:56.7")
    dec_str : str
        Declination string (e.g., "+45° 30' 15.3" or "+45:30:15.3")
    
    Returns:
    --------
    tuple
        (ephem.hours, ephem.degrees) for RA and Dec
    """
    # Handle RA format like "12h 34m 56.7s" or "12:34:56.7"
    if 'h' in ra_str or ':' in ra_str:
        # Convert to ephem format
        ra_parts = re.findall(r'(\d+)[h:]?\s*(\d+)[m:]?\s*([\d.]+)[s:]?', ra_str)
        if ra_parts:
            h, m, s = ra_parts[0]
            ra_ephem = f"{h}:{m}:{s}"
        else:
            # Try direct conversion if format is different
            ra_ephem = ra_str.replace('h', ':').replace('m', ':').replace('s', '')
    else:
        # Assume it's already in ephem format
        ra_ephem = ra_str
    
    # Handle Dec format like "+45° 30' 15.3"" or "+45:30:15.3"
    if '°' in dec_str or ':' in dec_str:
        # Convert to ephem format
        dec_parts = re.findall(r'([+-]?\d+)[°:]?\s*(\d+)[\':]?\s*([\d.]+)[\"]?', dec_str)
        if dec_parts:
            d, m, s = dec_parts[0]
            dec_ephem = f"{d}:{m}:{s}"
        else:
            # Try direct conversion if format is different
            dec_ephem = dec_str.replace('°', ':').replace('\'', ':').replace('"', '')
    else:
        # Assume it's already in ephem format
        dec_ephem = dec_str
    
    try:
        return ephem.hours(ra_ephem), ephem.degrees(dec_ephem)
    except ValueError as e:
        logging.warning(f"Error parsing RA/Dec: RA={ra_str}, Dec={dec_str}, Error={e}")
        # Return default values if parsing fails
        return ephem.hours("0:0:0"), ephem.degrees("0:0:0")

def get_brightest_stars(observer, local_dt, local_tz, num_stars=None, mag_limit=NAKED_EYE_MAG_LIMIT):
    """
    Get stars brighter than mag_limit visible at the specified location and time.

    Parameters:
    -----------
    observer : ephem.Observer
        The observer location.
    local_dt : datetime
        The local date and time for calculation.
    local_tz : timezone
        The local timezone.
    num_stars : int, optional
        Maximum number of stars to return (after magnitude filtering). If None, return all visible.
    mag_limit : float, optional
        Magnitude limit for stars to include. Defaults to NAKED_EYE_MAG_LIMIT.

    Returns:
    --------
    list
        List of dictionaries containing star information, sorted by magnitude.
    """
    
    # Calculate midnight time
    midnight = local_dt.replace(hour=0, minute=0, second=0, microsecond=0)
    midnight_utc = midnight.astimezone(utc)

    # Set observer date and time
    obs = ephem.Observer()
    obs.lat, obs.lon, obs.elev = observer.lat, observer.lon, observer.elev
    obs.date = midnight_utc.strftime('%Y/%m/%d %H:%M:%S')

    logging.info(f"Observer location: lat={obs.lat}, lon={obs.lon}, elev={obs.elev}")
    logging.info(f"Observer date/time (UTC): {obs.date}")

    try:
        # Ensure the path to your JSON file is correct
        with open('bsc5-short.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
        logging.info(f"Loaded {len(data)} stars from bsc5-short.json")
    except FileNotFoundError:
        logging.error("bsc5-short.json file not found. Please ensure the file exists.")
        # Return empty list or raise error if file is crucial
        return []
    except json.JSONDecodeError:
        logging.error("Error decoding JSON from bsc5-short.json.")
        return []

    star_data = []
    processed_count = 0
    visible_count = 0
    below_horizon_count = 0
    fainter_than_limit_count = 0
    error_count = 0
    unnamed_stars = 0

    for i, star in enumerate(data):
        processed_count += 1
        name = star.get("N")
        ra_str = star.get("RA")
        dec_str = star.get("Dec")
        mag_str = star.get("V") # Visual magnitude
        temp_k = star.get("K") # Temperature in Kelvin
        constellation_abbr = star.get("C", "Unknown") # Get constellation abbreviation from "C" field
        constellation = get_constellation_full_name(constellation_abbr) # Convert to full name

        if name is None:
            # Generate a name for unnamed stars
            name = f"Star_{i+1}"
            unnamed_stars += 1

        if mag_str is None:
            logging.debug(f"Star {name} missing magnitude (V). Skipping.")
            error_count += 1
            continue

        try:
            magnitude = float(mag_str)
        except (ValueError, TypeError):
            logging.warning(f"Invalid magnitude for star {name}: '{mag_str}'. Skipping.")
            error_count += 1
            continue

        # --- Filter by magnitude early ---
        if magnitude > mag_limit:
            fainter_than_limit_count += 1
            continue # Skip stars fainter than the limit

        try:
            ra_ephem, dec_ephem = parse_ra_dec(ra_str, dec_str)

            # Create a star using RA/Dec
            body = ephem.FixedBody()
            body._ra = ra_ephem
            body._dec = dec_ephem
            body.name = name
            body.compute(obs) # Compute position for the observer's time/location

            altitude = np.degrees(body.alt)
            logging.debug(f"Star {name}: altitude={altitude:.2f}°, magnitude={magnitude}")

            if altitude > 0: # Check if star is above the horizon
                visible_count += 1
                azimuth = np.degrees(body.az)
                azimuth_centered = center_azimuth(azimuth)

                star_data.append({
                    "name": name,
                    "magnitude": magnitude,
                    "constellation": constellation,
                    "altitude": altitude,
                    "azimuth": azimuth_centered,
                    "object": body, # Store the ephem object if needed later
                    "temp_k": temp_k # Store the temperature for coloring
                })
                logging.debug(f"Visible: {name} (Mag: {magnitude:.2f}) at Alt: {altitude:.2f}, Az: {azimuth_centered:.2f}")
            else:
                below_horizon_count += 1
                logging.debug(f"Below horizon: {name} (Alt: {altitude:.2f})")

        except Exception as e:
            logging.warning(f"Could not process star {name} (RA: {ra_str}, Dec: {dec_str}): {e}")
            error_count += 1
            continue

    logging.info(f"--- Star Processing Summary ---")
    logging.info(f"Total stars from file: {len(data)}")
    logging.info(f"Processed: {processed_count}")
    logging.info(f"Visible above horizon & brighter than {mag_limit}: {visible_count}")
    logging.info(f"Below horizon: {below_horizon_count}")
    logging.info(f"Fainter than limit ({mag_limit}): {fainter_than_limit_count}")
    logging.info(f"Unnamed stars: {unnamed_stars}")
    logging.info(f"Errors/Skipped: {error_count}")
    
    # Sort stars by magnitude (lower = brighter)
    star_data.sort(key=lambda x: x["magnitude"])

    # Return either all visible stars or the top N
    if num_stars is not None:
        result = star_data[:num_stars]
        logging.info(f"Returning top {len(result)} brightest visible stars (out of {visible_count})")
    else:
        result = star_data
        logging.info(f"Returning all {len(result)} visible stars brighter than {mag_limit}")

    logging.info(f"Returning {len(result)} brightest stars")
    return result

def plot_brightest_stars(ax, observer, local_dt, local_tz):
    """
    Plot the brightest stars at midnight of the selected day.
    
    Parameters:
    -----------
    ax : matplotlib.axes.Axes
        The axes to plot on
    observer : ephem.Observer
        The observer location
    local_dt : datetime
        The local date and time
    local_tz : timezone
        The local timezone
    
    Returns:
    --------
    dict
        Dictionary of star objects that were plotted
    """
    # Get the brightest stars
    brightest_stars = get_brightest_stars(observer, local_dt, local_tz, mag_limit=NAKED_EYE_MAG_LIMIT)
    
    logging.info(f"Plotting {len(brightest_stars)} stars")
    
    # Plot each star
    plotted_stars = {}
    if not brightest_stars:
        logging.warning("No stars found to plot.")
        return plotted_stars

    for i, star_info in enumerate(brightest_stars):
        # Only show labels for the 10 brightest stars
        show_label = i < 10
        
        # Plot the star
        mark_star(ax, star_info["azimuth"], star_info["altitude"], 
                 star_info["name"], 
                 star_info["constellation"], 
                 star_info["magnitude"],
                 show_label=show_label,
                 temp_k=star_info.get("temp_k"))
        
        plotted_stars[star_info["name"]] = {
            "object": star_info["object"],
            "azimuth": star_info["azimuth"],
            "altitude": star_info["altitude"],
            "constellation": star_info["constellation"],
            "magnitude": star_info["magnitude"],
            "temp_k": star_info.get("temp_k")
        }
        
    return plotted_stars 