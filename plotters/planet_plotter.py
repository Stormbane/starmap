import ephem
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from pytz import timezone, utc
import matplotlib.colors as mcolors
import logging
import yaml
from pathlib import Path
from utils.resource_utils import resource_path

def load_config():
    """
    Load configuration from config.yaml file.
    
    Returns:
    --------
    dict
        Configuration dictionary
    """
    try:
        config_path = resource_path('config.yaml', external=True)
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        return config
    except Exception as e:
        logging.error(f"Error loading config: {e}")
        return {}

# Load configuration
CONFIG = load_config()

def get_planet_position(planet, observer, local_dt, planetName):
    """
    Calculate the position of a planet at a specific date and time.
    
    Parameters:
    -----------
    planet : ephem.Planet
        The planet to calculate the position for
    observer : ephem.Observer
        The observer location
    local_dt : datetime
        The local date and time
        
    Returns:
    --------
    tuple
        (azimuth, altitude) in degrees, or (None, None) if planet is below horizon
    """
    # Convert local datetime to UTC
    utc_dt = local_dt.astimezone(utc)
    
    # Create a copy of the observer
    obs = ephem.Observer()
    obs.lat, obs.lon, obs.elev = observer.lat, observer.lon, observer.elev
    obs.date = utc_dt.strftime('%Y/%m/%d %H:%M:%S')
    
    if planetName in ['Rahu', 'Ketu']:
        # For Rahu and Ketu, compute using the Moon's ascending node
        # Compute Moon and Sun positions
        moon = ephem.Moon()
        moon.compute(obs)

        sun = ephem.Sun()
        sun.compute(obs)
        
        # Get their ecliptic longitudes
        moon_ecl = ephem.Ecliptic(moon)
        sun_ecl = ephem.Ecliptic(sun)

         # Rahu: Moon longitude - Sun longitude
        rahu_long = (moon_ecl.lon - sun_ecl.lon) % (2 * ephem.pi)

        if planetName == 'Ketu':
            rahu_long = (rahu_long + ephem.pi) % (2 * ephem.pi)

        # Node lies on the ecliptic plane (lat = 0)
        node_ecl = ephem.Ecliptic(rahu_long, 0)

        # Convert to RA/Dec
        ra, dec = node_ecl.to_radec()

         # Create a fixed body at that position
        node = ephem.FixedBody()
        node._ra = ra
        node._dec = dec
        node.compute(obs)

        altitude = np.degrees(node.alt)
        azimuth = np.degrees(node.az)

        if altitude > 0:
            return azimuth, altitude
        else:
            return None, None
    else:
        # For regular planets, use the standard calculation
        planet.compute(obs)
        
        # Get altitude and azimuth
        altitude = np.degrees(planet.alt)
        azimuth = np.degrees(planet.az)
        
        # Check if planet is above horizon
        if altitude > 0:
            return azimuth, altitude
        else:
            return None, None

def center_azimuth(azimuth):
    """Convert from 0-360 to -180 to 180 with North at 0."""
    return (azimuth - 180) % 360 - 180

def mark_planet(ax, x, y, symbol, color, text_color, local_dt, local_tz, y_offset=1):
    """Mark a point on the plot with a planet symbol."""
    # Plot the planet as a dot
    ax.scatter([x], [y], color=color, edgecolor='black', s=300, zorder=5)
    
    # Add the planet symbol as text
    ax.text(x, y, symbol, color=text_color, fontsize=12, fontweight='bold', ha='center', va='center', zorder=10)


def plot_planets(ax, observer, local_dt, local_tz, include_planets=None):
    """
    Plot the positions of planets at the specified date and time.
    Only planets visible at the specified date and time will be plotted.
    
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
        Options: ['Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'Uranus', 'Neptune', 'Pluto', 'Moon']
    
    Returns:
    --------
    dict
        Dictionary of planet objects that were plotted
    """
    # Get planet information from config
    planet_info = CONFIG["planets"]
    
    # Create planet objects
    planets = {
        'Sun': ephem.Sun(),
        'Mercury': ephem.Mercury(),
        'Venus': ephem.Venus(),
        'Mars': ephem.Mars(),
        'Jupiter': ephem.Jupiter(),
        'Saturn': ephem.Saturn(),
        'Uranus': ephem.Uranus(),
        'Neptune': ephem.Neptune(),
        'Pluto': ephem.Pluto(),
        'Moon': ephem.Moon(),
        'Rahu': ephem.Moon(),  # Rahu is the Moon's North Node
        'Ketu': ephem.Moon(),   # Ketu is the Moon's South Node
    }
    
    # If include_planets is None, include all planets
    if include_planets is None:
        include_planets = list(planets.keys())
    
    # Plot each planet
    plotted_planets = {}
    visible_planets = []
    
    # Check which planets are visible and plot them
    for planet_name, planet in planets.items():
        if planet_name in include_planets:
            # Get planet position
            azimuth, altitude = get_planet_position(planet, observer, local_dt, planet_name)
            
            if azimuth is not None and altitude is not None:
                # Planet is visible
                visible_planets.append(planet_name)
                logging.info(f"{planet_name} is visible at {local_dt} at azimuth {azimuth:.2f}°, altitude {altitude:.2f}°")
                
                # Center the azimuth
                az_centered = center_azimuth(azimuth)
                
                # Get planet color and symbol
                color = planet_info[planet_name]['color']
                text_color = planet_info[planet_name]['text_color']
                symbol = planet_info[planet_name]['symbol']
                
                # Mark the planet
                mark_planet(ax, az_centered, altitude, symbol, color, text_color, local_dt, local_tz)
                
                plotted_planets[planet_name] = planet
            
    
    # Log summary of visible planets
    if visible_planets:
        logging.info(f"Visible planets: {', '.join(visible_planets)}")
    else:
        logging.info("No planets are visible at this time")
    
    return plotted_planets 