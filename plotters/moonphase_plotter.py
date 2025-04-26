import matplotlib.pyplot as plt
import ephem
import numpy as np
from datetime import datetime
from pytz import timezone, utc
import logging
from matplotlib.patches import Circle, Arc, Path, PathPatch
import matplotlib.cm as cm
import matplotlib.colors as mcolors
from datetime import timezone as dt_timezone
import os
from PIL import Image
import matplotlib.image as mpimg
from utils.resource_utils import resource_path

def get_moon_phase(local_dt):
    """
    Returns detailed moon phase data.

    Parameters:
    -----------
    local_dt : datetime.datetime (timezone-aware or naive local time)

    Returns:
    --------
    illumination : float
        Fraction of the Moon's disk illuminated (0.0 to 1.0)
    phase_name : str
        Human-readable phase name
    lunar_day : float
        Number of days since the last new moon
    next_new_dt : datetime.datetime
        Datetime of the next new moon (UTC)
    next_full_dt : datetime.datetime
        Datetime of the next full moon (UTC)
    """
    # Convert to UTC
    utc_dt = local_dt.astimezone(utc)
    moon = ephem.Moon()
    moon.compute(utc_dt)
    illumination = moon.phase / 100.0

    # Find surrounding new moons
    prev_new = ephem.previous_new_moon(utc_dt)
    next_new = ephem.next_new_moon(utc_dt)
    next_full = ephem.next_full_moon(utc_dt)

    # Convert to timezone-aware UTC datetime
    prev_new_dt = prev_new.datetime().replace(tzinfo=dt_timezone.utc)
    next_new_dt = next_new.datetime().replace(tzinfo=dt_timezone.utc)
    next_full_dt = next_full.datetime().replace(tzinfo=dt_timezone.utc)

    # Calculate lunar age and cycle
    lunar_day = (utc_dt - prev_new_dt).total_seconds() / 86400.0
    moon_cycle_days = (next_new_dt - prev_new_dt).total_seconds() / 86400.0
    waxing = lunar_day < (moon_cycle_days / 2)

    # Phase classification
    if illumination < 0.03:
        phase_name = "New Moon"
    elif illumination < 0.25:
        phase_name = "Waxing Crescent" if waxing else "Waning Crescent"
    elif illumination < 0.45:
        phase_name = "First Quarter" if waxing else "Last Quarter"
    elif illumination < 0.75:
        phase_name = "Waxing Gibbous" if waxing else "Waning Gibbous"
    else:
        phase_name = "Full Moon"

    return illumination, phase_name, lunar_day, next_new_dt, next_full_dt

def plot_moon_phase_info(ax, observer, local_dt, local_tz):
    """
    Add moon phase information to the top left corner of the star map.
    
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
    """
    # Create moon object
    moon = ephem.Moon()
    
    # Convert local time to UTC for ephem calculations
    utc_dt = local_dt.astimezone(utc)
    today = ephem.Date(utc_dt.replace(tzinfo=None))
    
    # Set observer date
    observer.date = today
    
    # Calculate moon phase using last new moon and last full moon
    last_new_moon = ephem.previous_new_moon(today).datetime()
    last_full_moon = ephem.previous_full_moon(today).datetime()
    next_new_moon = ephem.next_new_moon(today).datetime()
    next_full_moon = ephem.next_full_moon(today).datetime()
    
    # Convert to local time
    last_new_moon = utc.localize(last_new_moon).astimezone(local_tz)
    last_full_moon = utc.localize(last_full_moon).astimezone(local_tz)
    next_new_moon = utc.localize(next_new_moon).astimezone(local_tz)
    next_full_moon = utc.localize(next_full_moon).astimezone(local_tz)
    
    # Calculate lunar day (1-30)
    # Lunar month is approximately 29.53 days
    lunar_month = 29.53
    
    # Calculate days since last new moon
    days_since_new = (local_dt - last_new_moon).total_seconds() / (24 * 3600)
    
    # Calculate lunar day (1-30)
    lunar_day = int(days_since_new % lunar_month) + 1
    
    # Calculate phase as a fraction (0.0 to 1.0)
    # 0.0 = new moon, 0.5 = full moon, 1.0 = next new moon
    phase = (days_since_new % lunar_month) / lunar_month
    
    # Get moon phase name
    name = get_moon_phase_name(phase)
    
    # Calculate Bengali date
    bengali_month, bengali_date = calculate_bengali_date(local_dt)
    
    # Determine which is closer by comparing total seconds
    days_to_full = (next_full_moon - local_dt).total_seconds()
    days_to_new = (next_new_moon - local_dt).total_seconds()
    
    if days_to_full < days_to_new:
        next_event = "Full Moon"
        next_date = next_full_moon
        days_until = (next_full_moon - local_dt).days
    else:
        next_event = "New Moon"
        next_date = next_new_moon
        days_until = (next_new_moon - local_dt).days
    
    # Format the next moon date
    next_moon_str = next_date.strftime("%d %b %H:%M")
    
    # Create the moon phase info text with multiple lines
    moon_info = (f"$\\bf{{Phase:}}$ {name}\n"
                f"$\\bf{{Lunar Day:}}$ {lunar_day:.1f}\n"
                f"$\\bf{{Bengali:}}$ {bengali_month} {bengali_date}\n"
                f"{next_event}: {next_moon_str} ({days_until} days)")
    
    # Load the appropriate moon phase image
    moonphase_folder = "images/moonphase"
    moon_day = int(lunar_day)

    logging.info(f"Moon day: {lunar_day}")
    logging.info(f"moon_image_path: {f"moon_day_{moon_day:02d}.png"}")

    moon_image_path = resource_path(os.path.join(moonphase_folder, f"moon_day_{moon_day:02d}.png"))
    
    # Position: left, bottom, width, height (in axes coordinates)
    padding = 0  # 2% padding from top and left
    size = 0.03     # 15% of figure size
    # Check if the image exists
    if os.path.exists(moon_image_path):
        # Load the image
        moon_img = mpimg.imread(moon_image_path)
        logging.info(f"Moon image path: {moon_image_path}")
        # Create an inset axes for the moon image
        
        moon_ax = ax.inset_axes([padding, 1 - padding - size - 0.017 , size, size])  
        moon_ax.imshow(moon_img)
        moon_ax.axis('off')  # Hide the axes
        
        # Add text to the right of the moon image
    ax.text(padding + size + 0.003, 1 - padding - size/2, moon_info, transform=ax.transAxes,
            color='white', fontsize=8, ha='left', va='top',
            bbox=dict(facecolor='black', alpha=0.7, edgecolor='none', pad=5))
    
    # Return the moon phase data for potential use elsewhere
    return {
        'phase': phase,
        'phase_name': name,
        'date': next_date.strftime('%Y-%m-%d')
    }

def get_moon_phase_name(phase):
    if phase < 0.03 or phase > 0.97:
        return "New Moon"
    elif phase < 0.22:
        return "Waxing Crescent"
    elif phase < 0.28:
        return "First Quarter"
    elif phase < 0.47:
        return "Waxing Gibbous"
    elif phase < 0.53:
        return "Full Moon"
    elif phase < 0.72:
        return "Waning Gibbous"
    elif phase < 0.78:
        return "Last Quarter"
    else:
        return "Waning Crescent"

def calculate_bengali_date(local_dt):
    """
    Rough Bengali date approximation.
    """
    bengali_months = ["Boishakh", "Jyoishtho", "Asharh", "Shrabon", "Bhadro", "Ashwin",
                      "Kartik", "Ogrohayon", "Poush", "Magh", "Falgun", "Choitro"]
    
    # Bengali new year typically starts April 14-15
    if (local_dt.month < 4) or (local_dt.month == 4 and local_dt.day < 14):
        bengali_year = local_dt.year - 594
    else:
        bengali_year = local_dt.year - 593

    # Month determination
    if local_dt.month == 4 and local_dt.day >= 14:
        month_idx = 0  # Boishakh
        bengali_day = local_dt.day - 13
    else:
        # Mapping
        # Note: This part is still rough, true Bengali months start mid-Gregorian month
        rough_month_offsets = {
            1: 8,  # January - Poush
            2: 9,  # February - Magh
            3: 10, # March - Falgun
            4: 11, # April (before 14) - Choitro
            5: 1,  # May - Jyoishtho
            6: 2,  # June - Asharh
            7: 3,  # July - Shrabon
            8: 4,  # August - Bhadro
            9: 5,  # September - Ashwin
            10: 6, # October - Kartik
            11: 7, # November - Ogrohayon
            12: 8  # December - Poush
        }
        month_idx = rough_month_offsets[local_dt.month]
        bengali_day = local_dt.day

    bengali_month = bengali_months[month_idx]
    return bengali_month, bengali_day