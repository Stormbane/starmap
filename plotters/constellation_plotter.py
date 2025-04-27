import json
import numpy as np
import matplotlib.pyplot as plt
import logging
import ephem
import yaml
from pathlib import Path
from datetime import datetime
from utils.constellation_utils import get_constellation_full_name
from pytz import utc
from utils.resource_utils import resource_path

# --- Configuration ---
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
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        return config
    except Exception as e:
        logging.error(f"Error loading config: {e}")
        return {}

# Load configuration
CONFIG = load_config()
MAX_CONSTELLATIONS_TO_PLOT = CONFIG["max_constellations_to_plot"]
SHOW_ONLY_CONSTELLATIONS = CONFIG["show_only_constellations"]

def load_constellation_data():
    """
    Load constellation line data from the JSON file.
    
    Returns:
    --------
    dict
        Dictionary containing constellation line data
    """
    try:
        json_path = resource_path('data/constellations.lines.json')
        with open(json_path, 'r') as f:
            data = json.load(f)
        return data
    except Exception as e:
        logging.error(f"Error loading constellation data: {e}")
        return None

def center_azimuth(azimuths):
    """Convert from 0-360 to -180 to 180 with North at 0."""
    return (azimuths - 180) % 360 - 180

def plot_wrapped_line(ax, points, **kwargs):
    """
    Plot a line that wraps around the sky correctly.
    
    Parameters:
    -----------
    ax : matplotlib.axes.Axes
        The axes to plot on
    points : numpy.ndarray
        Array of (x, y) points to plot
    **kwargs : dict
        Additional keyword arguments to pass to ax.plot
    """
    if len(points) < 2:
        return
    
    # Check if the line crosses the boundary
    x = points[:, 0]
    y = points[:, 1]
    
    # Find where the line crosses the boundary
    crossings = []
    for i in range(len(x) - 1):
        # Check if this segment crosses the boundary
        if abs(x[i] - x[i+1]) > 180:
            # This segment crosses the boundary
            # Calculate the crossing point
            if x[i] > x[i+1]:
                # Crossing from right to left
                ratio = (180 - x[i]) / (x[i] - x[i+1])
                cross_x = 180
            else:
                # Crossing from left to right
                ratio = (-180 - x[i]) / (x[i] - x[i+1])
                cross_x = -180
            
            # Interpolate y at the crossing point
            cross_y = y[i] + ratio * (y[i+1] - y[i])
            
            # Add the crossing point
            crossings.append((i, cross_x, cross_y))
    
    # If there are no crossings, just plot the line normally
    if not crossings:
        ax.plot(x, y, **kwargs)
        return
    
    # Plot the line segments with wrapping
    for i, (idx, cross_x, cross_y) in enumerate(crossings):
        # Plot the segment before the crossing
        if i == 0:
            # First segment
            ax.plot(x[:idx+1], y[:idx+1], **kwargs)
        else:
            # Middle segments
            prev_crossing = crossings[i-1]
            ax.plot(x[prev_crossing[0]+1:idx+1], y[prev_crossing[0]+1:idx+1], **kwargs)
        
        # Plot the segment after the crossing
        if i == len(crossings) - 1:
            # Last segment
            ax.plot(x[idx+1:], y[idx+1:], **kwargs)
        
        # Plot the crossing point
        ax.plot([cross_x], [cross_y], 'o', color=kwargs.get('color', 'white'), 
                markersize=2, alpha=kwargs.get('alpha', 0.3))

def plot_constellations(ax, stars, observer, local_dt):
    """
    Plot constellation lines on the given axes.
    
    Parameters:
    -----------
    ax : matplotlib.axes.Axes
        The axes to plot on
    stars : dict
        Dictionary of star dictionaries containing position information
    observer : ephem.Observer
        The observer's location
    local_dt : datetime
        The local date and time
    """
    # Load constellation data
    constellation_data = load_constellation_data()
    if not constellation_data:
        logging.warning("No constellation data available")
        return

    # Calculate midnight time
    time_utc = local_dt.astimezone(utc)

    # Set observer date and time
    obs = ephem.Observer()
    obs.lat, obs.lon, obs.elev = observer.lat, observer.lon, observer.elev
    obs.date = time_utc.strftime('%Y/%m/%d %H:%M:%S')

    logging.info(f"Observer location: lat={obs.lat}, lon={obs.lon}, elev={obs.elev}")
    logging.info(f"Observer date/time (UTC): {obs.date}")

    # Create a dictionary of star positions for easy lookup
    star_positions = {}
    for star_name, star_info in stars.items():
        star_positions[star_name] = (star_info["azimuth"], star_info["altitude"])
    
    # Filter constellations if SHOW_ONLY_CONSTELLATIONS is set
    features = constellation_data['features']
    if SHOW_ONLY_CONSTELLATIONS is not None:
        features = [f for f in features if f['id'] in SHOW_ONLY_CONSTELLATIONS]
        logging.info(f"Filtered to show only {len(features)} constellations from the specified list")
    
    # Limit the number of constellations to plot
    if MAX_CONSTELLATIONS_TO_PLOT is not None and len(features) > MAX_CONSTELLATIONS_TO_PLOT:
        features = features[:MAX_CONSTELLATIONS_TO_PLOT]
        logging.info(f"Limited to plotting {MAX_CONSTELLATIONS_TO_PLOT} constellations")
    
    # Dictionary to store all points for each constellation
    constellation_points = {}
    
    # Plot each constellation
    for feature in features:
        constellation_id = feature['id']
        coordinates = feature['geometry']['coordinates']
        
        # Initialize points list for this constellation
        all_points = []
        
        # Plot each line segment in the constellation
        for line_segment in coordinates:
            # Convert coordinates to plot coordinates
            points = []
            for coord in line_segment:
                ra, dec = coord                
                if ra < 0:
                    ra += 360
                ra_hours = ra / 15.0

                # Convert RA/Dec to Az/Alt
                star = ephem.FixedBody()
                star._ra = ephem.degrees(str(ra))
                #star._ra = ephem.hours(ra_hours)
                star._dec = ephem.degrees(str(dec))
                star.compute(obs)
                
                # Only plot if point is above horizon
                if star.alt > 0:
                    az = float(star.az) * 180 / np.pi
                    # Center the azimuth on North (0 degrees)
                    az_centered = center_azimuth(az)
                    alt = float(star.alt) * 180 / np.pi
                    points.append((az_centered, alt))
            
            # Plot the line segment if we have at least 2 points
            if len(points) >= 2:
                points = np.array(points)
                # Use the wrapped line plotting function
                plot_wrapped_line(ax, points, color='white', alpha=0.3, linewidth=0.5)
                
                # Add points to the constellation's collection
                all_points.extend(points)
        
        # Store all points for this constellation
        if all_points:
            constellation_points[constellation_id] = np.array(all_points)
    
    # Add labels for each constellation (only once per constellation)
    for constellation_id, points in constellation_points.items():
        if len(points) > 0:
            # Find the middle-most point of the constellation
            # Calculate the centroid (average position)
            centroid = np.mean(points, axis=0)
            
            # Find the point closest to the centroid
            distances = np.sqrt(np.sum((points - centroid) ** 2, axis=1))
            middle_idx = np.argmin(distances)
            middle_point = points[middle_idx]
            
            # Add the constellation label at the middle point
            ax.text(middle_point[0], middle_point[1], 
                   get_constellation_full_name(constellation_id),
                   color='white', alpha=0.5, fontsize=8) 