import matplotlib.pyplot as plt
import logging
import ephem
from datetime import datetime
from pytz import timezone, utc

def format_coordinate(coord, is_latitude=True):
    """
    Format a coordinate (latitude or longitude) in a human-readable format.
    
    Parameters:
    -----------
    coord : float
        The coordinate value in degrees
    is_latitude : bool, optional
        Whether the coordinate is latitude (True) or longitude (False)
        
    Returns:
    --------
    str
        Formatted coordinate string
    """
    direction = 'N' if coord >= 0 else 'S'
    if not is_latitude:
        direction = 'E' if coord >= 0 else 'W'
    
    # Convert to absolute value and format with 2 decimal places
    abs_coord = abs(coord)
    return f"{abs_coord:.2f}°{direction}"

def plot_location_info(ax, observer, local_dt, local_tz):
    """
    Add location and time information to the top right corner of the plot.
    
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
    # Get location information
    lat_deg = float(observer.lat) * 180 / ephem.pi
    lon_deg = float(observer.lon) * 180 / ephem.pi
    
    # Format coordinates
    lat_str = format_coordinate(lat_deg, is_latitude=True)
    lon_str = format_coordinate(lon_deg, is_latitude=False)
    
    # Get location name (if available)
    location_name = get_location_name(lat_deg, lon_deg)
    
    # Format date and time
    date_str = local_dt.strftime('%Y-%m-%d')
    time_str = local_dt.strftime('%I:%M%p').lower().lstrip('0')
    tz_name = local_tz.zone
    
    # Create the location info text
    info = (fr"$\bf{{Location:}}$ {location_name} ({lat_str}; {lon_str})"
           "\n"
           fr"$\bf{{Time:}}$ {date_str} {time_str} {tz_name}")
    
    # Add text to the top right corner
    # Use transform=ax.transAxes to position relative to the axes (0-1 range)
    
    # Draw the detailed moon phase diagram
    #draw_celestial_moon(ax, phase, center_az=-175, center_alt=88, moon_diameter_deg=5)
    
    # Add text to the top left corner with 50px padding
    ax.text(0.98, 0.98, info,
            transform=ax.transAxes,
            horizontalalignment='right',
            verticalalignment='top',
            color='white',
            fontsize=8,
            bbox=dict(facecolor='black', alpha=0.5, edgecolor='none', pad=5))

def get_location_name(lat_deg, lon_deg):
    """
    Get a human-readable location name based on coordinates using reverse geocoding.
    
    Parameters:
    -----------
    lat_deg : float
        Latitude in degrees
    lon_deg : float
        Longitude in degrees
        
    Returns:
    --------
    str
        Location name
    """
    try:
        # Use the geopy library for reverse geocoding
        from geopy.geocoders import Nominatim
        from geopy.exc import GeocoderTimedOut, GeocoderUnavailable

        # Initialize the geolocator
        geolocator = Nominatim(user_agent="starmap_app")

        # Attempt reverse geocoding
        try:
            location = geolocator.reverse((lat_deg, lon_deg), language='en')
            if location:
                address_parts = location.raw.get('address', {})
                logging.debug(f"location: {location}")
                logging.debug(f"address_parts: {address_parts}")
                return (
                    address_parts.get('suburb') or
                    address_parts.get('city_district') or
                    address_parts.get('city') or
                    address_parts.get('district') or
                    address_parts.get('town') or
                    address_parts.get('village') or
                    address_parts.get('state') or
                    address_parts.get('country') or
                    location.address.split(',')[0]
                )
            else:
                return "Unknown Location"
        except (GeocoderTimedOut, GeocoderUnavailable):
            return "Geocoding Service Unavailable"

    except ImportError:
        # If geopy is not installed, fall back to a simple method
        return f"Location at {lat_deg:.2f}°, {lon_deg:.2f}°"
