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

def draw_moon_phase(ax, phase, x, y, size=0.05):
    """
    Draw a moon phase diagram.
    
    Parameters:
    -----------
    ax : matplotlib.axes.Axes
        The axes to plot on
    phase : float
        Moon phase (0.0 to 1.0)
    x : float
        x-coordinate (in axes coordinates)
    y : float
        y-coordinate (in axes coordinates)
    size : float, optional
        Size of the moon diagram
    """
    # Create a circle for the moon
    moon = Circle((x, y), size, color='white', transform=ax.transAxes)
    ax.add_patch(moon)
    
    # Create a circle for the shadow
    shadow = Circle((x, y), size, color='black', transform=ax.transAxes)
    
    # Calculate the shadow position based on the phase
    if phase < 0.5:  # Waxing moon (shadow on left)
        # Calculate the x-offset for the shadow
        x_offset = size * (1 - 2 * phase)
        shadow.center = (x + x_offset, y)
    else:  # Waning moon (shadow on right)
        # Calculate the x-offset for the shadow
        x_offset = size * (2 * phase - 1)
        shadow.center = (x - x_offset, y)
    
    ax.add_patch(shadow)

def draw_detailed_moon_phase(ax, phase, x, y, size=0.05):
    """
    Draw a more detailed moon phase diagram with craters and shading.
    
    Parameters:
    -----------
    ax : matplotlib.axes.Axes
        The axes to plot on
    phase : float
        Moon phase (0.0 to 1.0)
    x : float
        x-coordinate (in axes coordinates)
    y : float
        y-coordinate (in axes coordinates)
    size : float, optional
        Size of the moon diagram
    """
    # Create the base moon circle
    moon = Circle((x, y), size, color='white', transform=ax.transAxes)
    ax.add_patch(moon)
    
    # Determine if waxing or waning
    is_waxing = phase < 0.5
    
    # Calculate the terminator position (the line between light and dark)
    terminator_x = x + (size * (1 - 2 * phase) if is_waxing else -size * (2 * phase - 1))
    
    # Create the shadow
    if is_waxing:
        # For waxing moon, shadow is on the left
        shadow_path = Path([
            (x - size, y - size),  # Bottom left
            (x - size, y + size),  # Top left
            (terminator_x, y + size),  # Top right
            (terminator_x, y - size),  # Bottom right
            (x - size, y - size),  # Back to start
        ])
    else:
        # For waning moon, shadow is on the right
        shadow_path = Path([
            (x + size, y - size),  # Bottom right
            (x + size, y + size),  # Top right
            (terminator_x, y + size),  # Top left
            (terminator_x, y - size),  # Bottom left
            (x + size, y - size),  # Back to start
        ])
    
    shadow = PathPatch(shadow_path, facecolor='black', transform=ax.transAxes)
    ax.add_patch(shadow)
    
    # Add some craters (simplified representation)
    crater_radius = size * 0.1
    crater_positions = [
        (x + size * 0.3, y + size * 0.2),
        (x - size * 0.2, y + size * 0.3),
        (x + size * 0.1, y - size * 0.3),
        (x - size * 0.3, y - size * 0.1),
    ]
    
    for cx, cy in crater_positions:
        # Only draw craters on the illuminated side
        if (is_waxing and cx > terminator_x) or (not is_waxing and cx < terminator_x):
            crater = Circle((cx, cy), crater_radius, 
                           facecolor='none', 
                           edgecolor='gray', 
                           alpha=0.5,
                           transform=ax.transAxes)
            ax.add_patch(crater)
            
            # Add a highlight to make it look more 3D
            highlight = Circle((cx - crater_radius * 0.3, cy + crater_radius * 0.3), 
                              crater_radius * 0.3, 
                              facecolor='white', 
                              alpha=0.3,
                              transform=ax.transAxes)
            ax.add_patch(highlight)

def draw_celestial_moon(ax, phase, center_az, center_alt, moon_diameter_deg=0.5, resolution=300):
    """
    Draw a realistic moon in data (azimuth/altitude) coordinates.
    
    Parameters:
    -----------
    ax : matplotlib.axes.Axes
        The axes to draw on
    phase : float
        Moon phase (0.0 = new, 0.5 = full)
    center_az : float
        Azimuth in degrees (-180 to 180)
    center_alt : float
        Altitude in degrees (0 to 90)
    moon_diameter_deg : float
        Moon's apparent angular diameter
    resolution : int
        Grid resolution for the moon image
    """
    # Create moon texture grid
    grid = np.linspace(-1, 1, resolution)
    X, Y = np.meshgrid(grid, grid)
    R = np.sqrt(X**2 + Y**2)
    mask = R <= 1

    # Phase-based illumination
    illum = np.clip(np.cos((X + (2 * phase - 1)) * np.pi), 0, 1)

    # Earthshine glow for crescent
    earthshine = 0
    if 0.0 < phase < 0.1 or 0.9 < phase < 1.0:
        earthshine = 0.1 * (1 - illum) * mask

    # Crater effect
    np.random.seed(42)
    crater_noise = 0.85 + 0.15 * np.random.normal(0, 1, size=illum.shape)
    crater_noise = np.clip(crater_noise, 0.6, 1.1)
    final_img = (illum + earthshine) * crater_noise * mask

    # RGBA moon image
    moon_image = np.zeros((*final_img.shape, 4))
    moon_image[..., :3] = final_img[..., np.newaxis]
    moon_image[..., 3] = mask

    # Convert angular diameter to extent
    radius = moon_diameter_deg / 2
    extent = [
        center_az - radius,
        center_az + radius,
        center_alt - radius,
        center_alt + radius
    ]

    # Draw the moon
    ax.imshow(moon_image, extent=extent, origin='lower', transform=ax.transData, zorder=5)

    # Optional: glow using a faint outer circle
    glow = Circle((center_az, center_alt), radius * 2.5, color='white', alpha=0.03, lw=0, zorder=4)
    ax.add_patch(glow)

    # Outline
    ax.add_patch(Circle((center_az, center_alt), radius, edgecolor='white', facecolor='none', lw=0.3, zorder=6))


def plot_moon_phase_info(ax, observer, local_dt, local_tz):
    """
    Add moon phase information to the top left corner of the plot.
    
    Parameters:
    -----------
    ax : matplotlib.axes.Axes
        The axes to plot on
    observer : ephem.Observer
        The observer's location
    local_dt : datetime
        The local date and time
    local_tz : timezone
        The local timezone
    """
    # Get moon phase
    illum, name, lunar_day, next_new, next_full = get_moon_phase(local_dt)
    
    # Format date
    date_str = local_dt.strftime('%Y-%m-%d')
    
    
    # Calculate Bengali calendar date
    # Note: This is a simplified calculation and may need refinement
    bengali_months = ["Boishakh", "Jyoishtho", "Asharh", "Shrabon", "Bhadro", "Ashwin", 
                     "Kartik", "Ogrohayon", "Poush", "Magh", "Falgun", "Choitro"]
    bengali_year = local_dt.year - 593  # Approximate conversion
    bengali_month_idx = (local_dt.month + 3) % 12  # Bengali year starts in mid-April
    bengali_date = local_dt.day
    bengali_month = bengali_months[bengali_month_idx]
    
    # Create the moon phase info text with multiple lines
    moon_info = (f"Moon Phase: {name}\n"
                f"Lunar Day: {lunar_day:.0f}\n"
                f"Bengali: {bengali_month} {bengali_date}, {bengali_year}")
    
    # Draw the detailed moon phase diagram
    #draw_celestial_moon(ax, phase, center_az=-175, center_alt=88, moon_diameter_deg=5)
    
    # Add text to the top left corner with 50px padding
    ax.text(20/ax.get_window_extent().width, 1 - 20/ax.get_window_extent().height, moon_info,
            transform=ax.transAxes,
            horizontalalignment='left',
            verticalalignment='top',
            color='white',
            fontsize=10,
            bbox=dict(facecolor='black', alpha=0.5, edgecolor='none', pad=5))
    
    # Return the moon phase data for potential use elsewhere
    return {
        'phase': illum,
        'phase_name': name,
        'date': date_str
    } 