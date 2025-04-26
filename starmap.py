import ephem
import numpy as np
import matplotlib.pyplot as plt
import logging
from pytz import timezone, utc
from datetime import datetime, timedelta
import argparse
# Import the planet plotting module
from plotters.planet_plotter import plot_planets
# Import the star plotting module
from plotters.star_plotter import plot_brightest_stars
# Import the sun and moon plotting module
from plotters.sunmoon_plotter import plot_sun_and_moon
# Import the constellation plotting module
from plotters.constellation_plotter import plot_constellations
# Import the info plotting module
from plotters.info_plotter import plot_location_info
# Import the moon phase plotting module
from plotters.moonphase_plotter import plot_moon_phase_info
# Import the celestial lines plotting module
from plotters.line_plotter import plot_celestial_lines
# Import the wallpaper setting module
from utils.set_wallpaper import set_wallpaper
from matplotlib.colors import to_rgba

# Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Generate a star map for a specific date and time.')
    
    # Date and time arguments
    parser.add_argument('--date', type=str, default=datetime.now().strftime('%Y-%m-%d'),
                        help='Date in YYYY-MM-DD format (default: 2025-04-26)')
    parser.add_argument('--time', type=str, default='22:00:00',
                        help='Time in HH:MM:SS format (default: 22:00:00)')
    
    # Location arguments
    parser.add_argument('--lat', type=str, default='-27.47',
                        help='Latitude in decimal degrees (default: -27.47 for Brisbane)')
    parser.add_argument('--lon', type=str, default='153.02',
                        help='Longitude in decimal degrees (default: 153.02 for Brisbane)')
    parser.add_argument('--elev', type=float, default=0,
                        help='Elevation in meters (default: 0)')
    parser.add_argument('--timezone', type=str, default='Australia/Brisbane',
                        help='Timezone (default: Australia/Brisbane)')
    
    # Output arguments
    parser.add_argument('--output', type=str, default='starmap.png',
                        help='Output filename (default: starmap.png)')
    
    # Wallpaper setting
    parser.add_argument('--setAsWallpaper', action='store_true',
                        help='Set the generated image as desktop wallpaper and suppress plot display')
    
    return parser.parse_args()

def set_background_gradient(ax):
    # Define color stops (from bottom to top)
    black = to_rgba("#000000")
    purple = to_rgba("#160B21") ##4b2673
    navy = to_rgba("#000012") ##0b1a40
    space_black = to_rgba("#000000")

    # Create vertical gradient
    height = 2160
    # Define breakpoints
    break_horizon = int(height * 0.1)  # bottom 5% = black (ground)
    start_purple = break_horizon
    end_purple = int(height * 0.15)
    end_navy = int(height * 0.4)

    gradient = np.zeros((height, 1, 4))
    for i in range(height):
        if i < break_horizon:
            c = black # ground
        elif i < end_purple:
            t = (i - start_purple) / (end_purple - start_purple)
            c = (1 - t) * np.array(purple) + t * np.array(navy)
        elif i < end_navy:
            t = (i - end_purple) / (end_navy - end_purple)
            c = (1 - t) * np.array(navy) + t * np.array(space_black)
        else:
            c = space_black
        gradient[i, 0] = c

    # Display gradient as background
    ax.imshow(gradient, extent=[0, 1, 0, 1], transform=ax.transAxes,
              aspect='auto', origin='lower', zorder=0)

def set_background_gradient_option2(ax):
    # Define color stops (from bottom to top)
    black = to_rgba("#000000")
    purple = to_rgba("#000012") ##4b2673
    space_black = to_rgba("#000000")

    # Create vertical gradient
    height = 2160
    # Define breakpoints
    break_horizon = int(height * 0.1)  # bottom 5% = black (ground)
    start_purple = break_horizon
    end_purple = int(height * 0.9)

    gradient = np.zeros((height, 1, 4))
    for i in range(height):
        if i < break_horizon:
            c = black # ground
        elif i < end_purple:
            t = (i - start_purple) / (end_purple - start_purple)
            c = (1 - t) * np.array(purple) + t * np.array(space_black)
        else:
            c = space_black
        gradient[i, 0] = c

    # Display gradient as background
    ax.imshow(gradient, extent=[0, 1, 0, 1], transform=ax.transAxes,
              aspect='auto', origin='lower', zorder=0)


def add_cardinal_directions(ax):
    """Add cardinal direction labels (N,S,E,W etc) along the horizon."""
    cardinals_centered = {
        "N": 0,
        "NE": 45,
        "E": 90,
        "SE": 135,
        "S": 180,
        "SW": -135,
        "W": -90,
        "NW": -45
    }
    for dir, az in cardinals_centered.items():
        ax.text(az, 1, dir, color='white', ha='center', fontsize=14, fontweight='bold')

# Add degree scale (ruler)
def add_degree_scale(ax, y_pos=-5):
    # Major ticks every 30 degrees
    major_ticks = np.arange(-180, 181, 30)
    # Minor ticks every 10 degrees
    minor_ticks = np.arange(-180, 181, 10)
    
    # Plot the main line
    ax.plot([-180, 180], [y_pos, y_pos], color='white', linewidth=1)
    
    # Add major ticks and labels
    for degree in major_ticks:
        # Major tick
        ax.plot([degree, degree], [y_pos-0.5, y_pos+0.5], color='white', linewidth=1.5)
        
        degLabel = 360 + degree if degree < 0 else degree
        # Label
        ax.text(degree, y_pos+4, f"{degLabel}°", color='white', ha='center', fontsize=10)
    
    # Add minor ticks
    for degree in minor_ticks:
        if degree not in major_ticks:  # Skip major tick positions
            ax.plot([degree, degree], [y_pos-0.25, y_pos+0.25], color='white', linewidth=1)

# Add vertical altitude scale
def add_altitude_scale(ax, x_pos=0):
    # Major ticks every 15 degrees
    ax.xaxis.set_label_position('top')  # Move label to top
    ax.xaxis.tick_top()                 # Move ticks to top (optional, if you want)

    major_ticks = np.arange(0, 91, 15)
    # Minor ticks every 5 degrees
    minor_ticks = np.arange(0, 91, 5)
    
    # Plot the main line
    ax.plot([x_pos, x_pos], [0, 90], color='white', linewidth=1)
    
    # Add major ticks and labels
    for degree in major_ticks:
        # Major tick
        ax.plot([x_pos-0.5, x_pos+0.5], [degree, degree], color='white', linewidth=1.5)
        # Label
        ax.text(x_pos-2, degree, f"{degree}°", color='white', ha='left', fontsize=10)
    
    # Add minor ticks
    for degree in minor_ticks:
        if degree not in major_ticks:  # Skip major tick positions
            ax.plot([x_pos-0.25, x_pos+0.25], [degree, degree], color='white', linewidth=1)


def main():
    """Main function to generate the star map."""
    # Parse command line arguments
    args = parse_arguments()
    
    # Observer location
    observer = ephem.Observer()
    observer.lat = args.lat
    observer.lon = args.lon
    observer.elev = args.elev
    
    # Local time and UTC conversion
    local_tz = timezone(args.timezone)
    
    # Parse date and time
    try:
        date_parts = args.date.split('-')
        time_parts = args.time.split(':')
        
        year = int(date_parts[0])
        month = int(date_parts[1])
        day = int(date_parts[2])
        
        hour = int(time_parts[0])
        minute = int(time_parts[1])
        second = int(time_parts[2]) if len(time_parts) > 2 else 0
        
        local_dt = local_tz.localize(datetime(year, month, day, hour, minute, second))
    except (ValueError, IndexError) as e:
        logging.error(f"Error parsing date/time: {e}")
        logging.error("Using default date/time: 2025-04-26 22:00:00")
        local_dt = local_tz.localize(datetime(2025, 4, 26, 22, 0, 0))
    
    logging.info(f"Local date and time: {local_dt}")
    local_dt_midnight = local_tz.localize(datetime(year, month, day, 0, 0, 0))
    logging.info(f"Local date and time midnight: {local_dt_midnight}")
    
    # Convert local time to UTC for ephem calculations
    utc_dt = local_dt.astimezone(utc)
    today = ephem.Date(utc_dt.replace(tzinfo=None))
    
    # Set observer date - this is the critical fix
    observer.date = today
    
    # Plot setup
    fig, ax = plt.subplots(figsize=(3840/100, 2160/100), dpi=100)
    
    # Call the function to set the background gradient
    set_background_gradient_option2(ax)

    # Add location and time information to the top right corner
    plot_location_info(ax, observer, local_dt, local_tz)

    # Add moon phase information to the top left corner
    plot_moon_phase_info(ax, observer, local_dt_midnight, local_tz)

    # Plot sun and moon paths
    celestial_data = plot_sun_and_moon(ax, observer, local_dt_midnight, local_tz)

    # Plot brightest stars
    stars_data = plot_brightest_stars(ax, observer, local_dt, local_tz)

    # Plot constellation lines
    plot_constellations(ax, stars_data, observer, local_dt)

    # Plot celestial equator and ecliptic lines
    # celestial_lines_data = plot_celestial_lines(ax, observer, local_dt, local_tz)

    # Plot planets (can be commented out to disable)
    plot_planets(ax, observer, local_dt, local_tz)
            
    # turn off labels
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    ax.tick_params(bottom=False, left=False)
    for spine in ax.spines.values():
        spine.set_visible(False)

    # Add both scales
    add_cardinal_directions(ax)
    add_degree_scale(ax)
    add_altitude_scale(ax)

    # Formatting
    ax.set_xlim(-180, 180)  # Extended x-axis to accommodate the altitude scale
    ax.set_ylim(-10, 90)  # Extended y-axis to accommodate the azimuth scale
    #ax.set_xlabel("Azimuth (°)", color='white')
    #ax.set_ylabel("Altitude (°)", color='white')  # Moved down by 10 pixels
    ax.tick_params(colors='white')

    # Set major grid lines every 30 degrees
    ax.set_xticks(np.arange(-180, 181, 30))
    # Set major grid lines every 30 degrees
    ax.set_yticks(np.arange(0, 91, 20))
    ax.grid(True, which='major', linestyle='-', alpha=0.3, color='white')
    # Add minor grid lines every 10 degrees
    ax.set_xticks(np.arange(-180, 181, 10), minor=True)
    ax.set_yticks(np.arange(0, 91, 10), minor=True)
    ax.grid(True, which='minor', linestyle=':', alpha=0.1, color='white')

    ax.axhline(0, color='white', linewidth=1)
    ax.axvline(0, color='white', linestyle=':', linewidth=0.8)  # North marker
    #ax.legend(facecolor='#000733', edgecolor='white', fontsize=12)

    plt.tight_layout()
    print("Skymap generated successfully!")

    def save_figure(fig, filename, dpi=150, target_width_px=3840, target_height_px=2160):
        """Save the figure to a file."""
        # Calculate required figure size in inches
        width_inch = target_width_px / dpi
        height_inch = target_height_px / dpi

        # Set the figure size
        fig.set_size_inches(width_inch, height_inch)

        # Remove any white space around the figure
        fig.tight_layout(pad=0)
        
        # Save with black background and black border
        fig.savefig(filename, dpi=dpi, bbox_inches='tight', pad_inches=0, facecolor='black', edgecolor='black')
        logging.info(f"Saved figure to {filename}")
        
        # If setAsWallpaper is True, set the image as wallpaper
        if args.setAsWallpaper:
            if set_wallpaper(filename):
                print(f"Successfully set {filename} as desktop wallpaper")
            else:
                print(f"Failed to set {filename} as desktop wallpaper")

    save_figure(fig, args.output)  # Save the plot to a file
    
    # Only show the plot if setAsWallpaper is False
    if not args.setAsWallpaper:
        plt.show()
    
if __name__ == "__main__":
    main()
