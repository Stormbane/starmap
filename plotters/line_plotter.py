import ephem
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from pytz import timezone, utc
import logging

def center_azimuth(azimuth):
    """Convert from 0-360 to -180 to 180 with North at 0."""
    return (azimuth - 180) % 360 - 180

def plot_celestial_equator(ax, observer, local_dt, local_tz):
    """
    Plot the celestial equator line on the star map.
    
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
    # Convert local time to UTC for ephem calculations
    utc_dt = local_dt.astimezone(utc)
    today = ephem.Date(utc_dt.replace(tzinfo=None))
    
    # Set observer date
    observer.date = today
    
    # Calculate the declination of the celestial equator (always 0 degrees)
    # We need to calculate the altitude and azimuth for points along the equator
    
    # Generate points along the celestial equator (every 15 degrees of right ascension)
    ra_points = np.linspace(0, 360, 25)  # 0 to 360 degrees in 15-degree steps
    dec_points = np.zeros_like(ra_points)  # All points are at 0 degrees declination
    
    # Convert RA/Dec to Alt/Az for each point
    alt_points = []
    az_points = []
    
    for ra, dec in zip(ra_points, dec_points):
        # Create a star at this RA/Dec
        star = ephem.FixedBody()
        star._ra = np.radians(ra)
        star._dec = np.radians(dec)
        
        # Compute the star's position
        star.compute(observer)
        
        # Get altitude and azimuth
        alt = np.degrees(star.alt)
        az = np.degrees(star.az)
        
        # Only include points above the horizon
        if alt > 0:
            alt_points.append(alt)
            az_points.append(az)
    
    # Convert to numpy arrays
    alt_points = np.array(alt_points)
    az_points = np.array(az_points)
    
    # Center the azimuths
    az_centered = center_azimuth(az_points)
    
    # Plot the celestial equator
    ax.plot(az_centered, alt_points, '--', color='cyan', linewidth=1, alpha=0.7, label='Celestial Equator')
    
    # Add a label at the highest point
    if len(alt_points) > 0:
        max_alt_idx = np.argmax(alt_points)
        ax.text(az_centered[max_alt_idx], alt_points[max_alt_idx], 'CE', 
                color='cyan', fontsize=10, ha='center', va='bottom')
    
    return {
        'azimuth': az_centered,
        'altitude': alt_points
    }

def plot_ecliptic(ax, observer, local_dt, local_tz):
    """
    Plot the ecliptic line on the star map.
    
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
    # Convert local time to UTC for ephem calculations
    utc_dt = local_dt.astimezone(utc)
    today = ephem.Date(utc_dt.replace(tzinfo=None))
    
    # Set observer date
    observer.date = today
    
    # The ecliptic is the path of the sun through the sky
    # We can approximate it by calculating the sun's position at different times of the year
    
    # Generate points along the ecliptic (every 15 degrees of ecliptic longitude)
    ecliptic_longitudes = np.linspace(0, 360, 25)  # 0 to 360 degrees in 15-degree steps
    
    # Convert ecliptic longitude to RA/Dec
    # The ecliptic is inclined at about 23.5 degrees to the celestial equator
    ecliptic_inclination = np.radians(23.5)
    
    # Convert to RA/Dec
    ra_points = []
    dec_points = []
    
    for ecl_lon in ecliptic_longitudes:
        # Convert ecliptic longitude to RA/Dec
        # This is a simplified calculation and may need refinement
        ecl_lon_rad = np.radians(ecl_lon)
        
        # Convert to RA/Dec
        # RA = atan2(sin(λ) * cos(ε), cos(λ))
        # Dec = asin(sin(λ) * sin(ε))
        ra = np.degrees(np.arctan2(np.sin(ecl_lon_rad) * np.cos(ecliptic_inclination), 
                                  np.cos(ecl_lon_rad)))
        dec = np.degrees(np.arcsin(np.sin(ecl_lon_rad) * np.sin(ecliptic_inclination)))
        
        ra_points.append(ra)
        dec_points.append(dec)
    
    # Convert to numpy arrays
    ra_points = np.array(ra_points)
    dec_points = np.array(dec_points)
    
    # Convert RA/Dec to Alt/Az for each point
    alt_points = []
    az_points = []
    
    for ra, dec in zip(ra_points, dec_points):
        # Create a star at this RA/Dec
        star = ephem.FixedBody()
        star._ra = np.radians(ra)
        star._dec = np.radians(dec)
        
        # Compute the star's position
        star.compute(observer)
        
        # Get altitude and azimuth
        alt = np.degrees(star.alt)
        az = np.degrees(star.az)
        
        # Only include points above the horizon
        if alt > 0:
            alt_points.append(alt)
            az_points.append(az)
    
    # Convert to numpy arrays
    alt_points = np.array(alt_points)
    az_points = np.array(az_points)
    
    # Center the azimuths
    az_centered = center_azimuth(az_points)
    
    # Plot the ecliptic
    ax.plot(az_centered, alt_points, '--', color='yellow', linewidth=1, alpha=0.7, label='Ecliptic')
    
    # Add a label at the highest point
    if len(alt_points) > 0:
        max_alt_idx = np.argmax(alt_points)
        ax.text(az_centered[max_alt_idx], alt_points[max_alt_idx], 'Ecl', 
                color='yellow', fontsize=10, ha='center', va='bottom')
    
    return {
        'azimuth': az_centered,
        'altitude': alt_points
    }

def plot_celestial_lines(ax, observer, local_dt, local_tz):
    """
    Plot both the celestial equator and ecliptic lines on the star map.
    
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
        Dictionary containing the celestial lines data
    """
    # Plot the celestial equator
    equator_data = plot_celestial_equator(ax, observer, local_dt, local_tz)
    
    # Plot the ecliptic
    ecliptic_data = plot_ecliptic(ax, observer, local_dt, local_tz)
    
    # Add a legend
    ax.legend(loc='upper right', framealpha=0.7, facecolor='black', edgecolor='white')
    
    # Return the data
    return {
        'equator': equator_data,
        'ecliptic': ecliptic_data
    } 