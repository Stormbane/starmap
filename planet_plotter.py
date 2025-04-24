import ephem
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from pytz import timezone, utc

def get_planet_path(planet, observer, start_time, end_time):
    """Calculate the path of a planet over a given time period."""
    # Sample every 30 minutes
    times = [start_time + timedelta(minutes=i) for i in range(0, int((end_time - start_time).total_seconds() / 60), 30)]
    az, alt, tlist = [], [], []
    
    for t in times:
        obs = ephem.Observer()
        obs.lat, obs.lon, obs.elev = observer.lat, observer.lon, observer.elev
        obs.date = t.strftime('%Y/%m/%d %H:%M:%S')
        planet.compute(obs)
        altitude = np.degrees(planet.alt)
        if altitude > 0:  # Only include points above horizon
            az.append(np.degrees(planet.az))
            alt.append(altitude)
            tlist.append(t)
    
    return np.array(az), np.array(alt), tlist

def center_azimuth(azimuths):
    """Convert from 0-360 to -180 to 180 with North at 0."""
    return (azimuths - 180) % 360 - 180

def mark_planet(ax, x, y, label, color, time, local_tz, y_offset=2):
    """Mark a point on the plot with a label and time."""
    if time:
        # Handle timezone conversion properly
        if time.tzinfo is None:
            # If time is naive, assume it's UTC
            local_time = utc.localize(time).astimezone(local_tz)
        else:
            # If time already has timezone info, just convert it
            local_time = time.astimezone(local_tz)
        label = f"{label} {local_time.strftime('%H:%M')}"
    ax.scatter([x], [y], color=color, edgecolor='black', s=100, zorder=5)
    ax.text(x, y + y_offset, label, color=color, fontsize=12, fontweight='bold', ha='center')

def plot_planets(ax, observer, local_dt, local_tz, include_planets=None):
    """
    Plot the paths of planets on the given axes.
    
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
    include_planets : list, optional
        List of planets to include. If None, all planets are included.
        Options: ['Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn']
    
    Returns:
    --------
    dict
        Dictionary of planet objects that were plotted
    """
    # Define planet colors
    planet_colors = {
        'Mercury': '#1A873A',  # Green
        'Venus': '#FFFFE3',    # White
        'Mars': '#700101',     # Red
        'Jupiter': '#FFDD40',  # Yellow
        'Saturn': '#042682'    # Blue
    }
    
    # Create planet objects
    planets = {
        'Mercury': ephem.Mercury(),
        'Venus': ephem.Venus(),
        'Mars': ephem.Mars(),
        'Jupiter': ephem.Jupiter(),
        'Saturn': ephem.Saturn()
    }
    
    # If include_planets is None, include all planets
    if include_planets is None:
        include_planets = list(planets.keys())
    
    # Calculate planet paths for the full day
    day_start = local_dt.replace(hour=0, minute=0, second=0, microsecond=0)
    day_end = day_start + timedelta(days=1)
    
    # Plot each planet
    plotted_planets = {}
    for planet_name, planet in planets.items():
        if planet_name in include_planets:
            # Get planet path
            az, alt, times = get_planet_path(planet, observer, day_start, day_end)
            
            if len(az) > 0:
                # Center the azimuths
                az_centered = center_azimuth(az)
                
                # Plot the path
                ax.plot(az_centered, alt, color=planet_colors[planet_name], linewidth=1, label=f'{planet_name} Path')
                
                # Mark highest point
                max_alt_idx = np.argmax(alt)
                mark_planet(ax, az_centered[max_alt_idx], alt[max_alt_idx], planet_name, 
                           planet_colors[planet_name], times[max_alt_idx], local_tz)
                
                plotted_planets[planet_name] = planet
    
    return plotted_planets 