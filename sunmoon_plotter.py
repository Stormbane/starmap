import ephem
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from pytz import timezone, utc
import logging

def center_azimuth(azimuths):
    """Convert from 0-360 to -180 to 180 with North at 0."""
    return (azimuths - 180) % 360 - 180

def get_body_path(body, observer, rise, set):
    """Calculate the path of a celestial body between rise and set times."""
    if set < rise:
        set += timedelta(days=1)
    times = [rise + timedelta(minutes=i) for i in range(0, int((set - rise).total_seconds() / 60), 20)]
    az, alt, tlist = [], [], []
    for t in times:
        obs = ephem.Observer()
        obs.lat, obs.lon, obs.elev = observer.lat, observer.lon, observer.elev
        obs.date = t.strftime('%Y/%m/%d %H:%M:%S')
        body.compute(obs)
        altitude = np.degrees(body.alt)
        if altitude >= 0:
            az.append(np.degrees(body.az))
            alt.append(altitude)
            tlist.append(t)
    return np.array(az), np.array(alt), tlist

def get_body_path_with_riseset(body, observer, rise, set):
    """Calculate the path of a celestial body between rise and set times, including exact rise/set positions."""
    if set < rise:
        set += timedelta(days=1)
    
    # Times sampled every 20 minutes
    times = [rise + timedelta(minutes=i) for i in range(0, int((set - rise).total_seconds() / 60), 20)]
    
    az, alt, tlist = [], [], []
    for t in times:
        obs = ephem.Observer()
        obs.lat, obs.lon, obs.elev = observer.lat, observer.lon, observer.elev
        obs.date = t.strftime('%Y/%m/%d %H:%M:%S')
        body.compute(obs)
        altitude = np.degrees(body.alt)
        if altitude > 0:
            az.append(np.degrees(body.az))
            alt.append(altitude)
            tlist.append(t)

    # Add exact rise and set positions
    for event_time in [rise, set]:
        obs = ephem.Observer()
        obs.lat, obs.lon, obs.elev = observer.lat, observer.lon, observer.elev
        obs.date = event_time.strftime('%Y/%m/%d %H:%M:%S')
        body.compute(obs)
        az_deg = np.degrees(body.az)
        alt_deg = np.degrees(body.alt)  # This will be ~0°
        az.insert(0 if event_time == rise else len(az), az_deg)
        alt.insert(0 if event_time == rise else len(alt), alt_deg)
        tlist.insert(0 if event_time == rise else len(tlist), event_time)

    return np.array(az), np.array(alt), tlist

def mark_point(ax, x, y, label, color, time=None, local_tz=None, y_offset=3):
    """Mark a point on the plot with a label and optional time."""
    logging.debug(f"mark_point called with label='{label}', time={time}, local_tz={local_tz}")
    
    if time and local_tz:
        # Handle timezone conversion properly
        if time.tzinfo is None:
            # If time is naive, assume it's UTC
            logging.debug(f"Time is naive, localizing to UTC: {time}")
            local_time = utc.localize(time).astimezone(local_tz)
        else:
            # If time already has timezone info, just convert it
            logging.debug(f"Time has timezone info: {time.tzinfo}, converting to {local_tz}")
            local_time = time.astimezone(local_tz)
        
        logging.debug(f"Converted time: {local_time}")
        label = f"{label} {local_time.strftime('%H:%M')}"
        logging.debug(f"Final label: {label}")
    else:
        logging.debug(f"No time or timezone provided, using original label: {label}")
    
    ax.scatter([x], [y], color=color, edgecolor='black', s=100, zorder=5)
    ax.text(x, y + y_offset, label, color=color, fontsize=12, fontweight='bold', ha='center')

def plot_sun_path(ax, observer, local_dt, local_tz):
    """
    Plot the sun's path for the day.
    
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
        Dictionary containing sun path data
    """
    # Create sun object
    sun = ephem.Sun()
    
    # Convert local time to UTC for ephem calculations
    utc_dt = local_dt.astimezone(utc)
    today = ephem.Date(utc_dt.replace(tzinfo=None))
    
    # Set observer date
    observer.date = today
    
    # Calculate sunrise and sunset
    sunrise = observer.next_rising(sun, use_center=False).datetime()
    observer.date = sunrise
    sunset = observer.next_setting(sun, use_center=False).datetime()
    
    # Get sun path
    sun_az, sun_alt, sun_times = get_body_path_with_riseset(sun, observer, sunrise, sunset)
    
    # Center the azimuths
    sun_az_centered = center_azimuth(sun_az)
    
    # Plot sun path
    ax.plot(sun_az_centered, sun_alt, color='gold', linewidth=2)
    
    # Mark key Sun moments
    if len(sun_az_centered) > 0:
        mark_point(ax, sun_az_centered[0], sun_alt[0], "Sunrise", 'orange', sun_times[0], local_tz, y_offset=-2)
        mark_point(ax, sun_az_centered[-1], sun_alt[-1], "Sunset", 'orange', sun_times[-1], local_tz, y_offset=-2)

        # Find max altitude point
        max_alt_idx = np.argmax(sun_alt)
        
        logging.debug(f"Noon time: {sun_times[max_alt_idx]}")
        logging.debug(f"Noon time type: {type(sun_times[max_alt_idx])}")
        logging.debug(f"Noon time tzinfo: {sun_times[max_alt_idx].tzinfo if hasattr(sun_times[max_alt_idx], 'tzinfo') else 'None'}")

        mark_point(ax, sun_az_centered[max_alt_idx], sun_alt[max_alt_idx], f"Noon {sun_alt[max_alt_idx]:.0f}°", 'gold', sun_times[max_alt_idx], local_tz)
        # Calculate midpoint altitude between max and horizon
        mid_alt = sun_alt[max_alt_idx] / 2
        
        # Find points closest to mid altitude on rising and setting sides
        rising_diffs = np.abs(sun_alt[:max_alt_idx] - mid_alt)
        setting_diffs = np.abs(sun_alt[max_alt_idx:] - mid_alt)
        rising_mid_idx = np.argmin(rising_diffs)
        setting_mid_idx = max_alt_idx + np.argmin(setting_diffs)
        
        mark_point(ax, sun_az_centered[rising_mid_idx], sun_alt[rising_mid_idx], "↖️", 'gold', sun_times[rising_mid_idx], local_tz)
        mark_point(ax, sun_az_centered[setting_mid_idx], sun_alt[setting_mid_idx], "↙️", 'gold', sun_times[setting_mid_idx], local_tz)
    
    return {
        'azimuth': sun_az_centered,
        'altitude': sun_alt,
        'times': sun_times
    }

def plot_moon_path(ax, observer, local_dt, local_tz):
    """
    Plot the moon's path for the day.
    
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
        Dictionary containing moon path data
    """
    # Create moon object
    moon = ephem.Moon()
    
    # Convert local time to UTC for ephem calculations
    utc_dt = local_dt.astimezone(utc)
    today = ephem.Date(utc_dt.replace(tzinfo=None))
    
    # Set observer date
    observer.date = today
    
    # Calculate moonrise and moonset
    moonrise = observer.next_rising(moon, use_center=False).datetime()
    observer.date = moonrise
    moonset = observer.next_setting(moon, use_center=False).datetime()
    
    # Get moon path
    moon_az, moon_alt, moon_times = get_body_path_with_riseset(moon, observer, moonrise, moonset)
    
    # Center the azimuths
    moon_az_centered = center_azimuth(moon_az)
    
    # Plot moon path
    ax.plot(moon_az_centered, moon_alt, color='silver', linewidth=1.5)
    
    # Mark key Moon moments
    if len(moon_az_centered) > 0:
        mark_point(ax, moon_az_centered[0], moon_alt[0], "Moonrise", 'silver', moon_times[0], local_tz, y_offset=-3)
        mark_point(ax, moon_az_centered[-1], moon_alt[-1], "Moonset", 'silver', moon_times[-1], local_tz, y_offset=-3)
        
        # Find the point of maximum altitude
        max_alt_idx = np.argmax(moon_alt)
        mark_point(ax, moon_az_centered[max_alt_idx], moon_alt[max_alt_idx], f"High Moon {moon_alt[max_alt_idx]:.0f}°", 'silver', moon_times[max_alt_idx], local_tz, y_offset=2)
    
    return {
        'azimuth': moon_az_centered,
        'altitude': moon_alt,
        'times': moon_times
    }

def plot_sun_and_moon(ax, observer, local_dt, local_tz):
    """
    Plot both the sun and moon paths for the day.
    
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
        Dictionary containing sun and moon data
    """
    # Plot sun path and get data
    sun_data = plot_sun_path(ax, observer, local_dt, local_tz)
    
    # Plot moon path and get data
    moon_data = plot_moon_path(ax, observer, local_dt, local_tz)
    
    # Return combined data for logging
    return {
        'sun': sun_data,
        'moon': moon_data
    } 