import ephem
import numpy as np
import matplotlib.pyplot as plt
import logging
from pytz import timezone, utc
from datetime import datetime, timedelta
# Import the planet plotting module
from planet_plotter import plot_planets
# Import the star plotting module
from star_plotter import plot_brightest_stars
# Import the sun and moon plotting module
from sunmoon_plotter import plot_sun_and_moon
# Import the constellation plotting module
from constellation_plotter import plot_constellations
# Import the info plotting module
from info_plotter import plot_location_info
# Import the moon phase plotting module
from moonphase_plotter import plot_moon_phase_info
from matplotlib.colors import to_rgba

# Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Observer location: Brisbane
observer = ephem.Observer()
observer.lat = "-27.47"
observer.lon = "153.02"
observer.elev = 0

# Local time and UTC conversion
local_tz = timezone("Australia/Brisbane")
local_dt = local_tz.localize(datetime(2025, 4, 24, 0, 0, 0))

# Plot setup
fig, ax = plt.subplots(figsize=(3840/100, 2160/100), dpi=100)

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
    end_purple = int(height * 0.2)
    end_navy = int(height * 0.5)

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

    #ax.set_facecolor("#000733")

# Call the function to set the background gradient
set_background_gradient(ax)

# Add location and time information to the top right corner
plot_location_info(ax, observer, local_dt, local_tz)

# Add moon phase information to the top left corner
plot_moon_phase_info(ax, observer, local_dt, local_tz)

# Plot sun and moon paths
celestial_data = plot_sun_and_moon(ax, observer, local_dt, local_tz)

# Log the ranges for debugging
logging.info(f"Sun path points: {len(celestial_data['sun']['azimuth'])}")
logging.info(f"Sun altitude range: min={min(celestial_data['sun']['altitude']):.2f}, max={max(celestial_data['sun']['altitude']):.2f}")
logging.info(f"Moon path points: {len(celestial_data['moon']['azimuth'])}")
if len(celestial_data['moon']['altitude']) > 0:
    logging.info(f"Moon altitude range: min={min(celestial_data['moon']['altitude']):.2f}, max={max(celestial_data['moon']['altitude']):.2f}")

# Plot brightest stars at midnight (can be commented out to disable)

local_dt = local_tz.localize(datetime(2025, 4, 24, 20, 0, 0))
stars_data = plot_brightest_stars(ax, observer, local_dt, local_tz)

# Plot constellation lines
plot_constellations(ax, stars_data, observer, local_dt)

# Plot planets (can be commented out to disable)
plot_planets(ax, observer, local_dt, local_tz)

# Cardinal directions with North at 0 degrees
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
        ax.text(degree, y_pos-2, f"{degLabel}°", color='white', ha='center', fontsize=10)
    
    # Add minor ticks
    for degree in minor_ticks:
        if degree not in major_ticks:  # Skip major tick positions
            ax.plot([degree, degree], [y_pos-0.25, y_pos+0.25], color='white', linewidth=1)

# Add vertical altitude scale
def add_altitude_scale(ax, x_pos=0):
    # Major ticks every 15 degrees
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
        ax.text(x_pos-2, degree, f"{degree}°", color='white', ha='right', fontsize=10)
    
    # Add minor ticks
    for degree in minor_ticks:
        if degree not in major_ticks:  # Skip major tick positions
            ax.plot([x_pos-0.25, x_pos+0.25], [degree, degree], color='white', linewidth=1)

# Add both scales
add_degree_scale(ax)
add_altitude_scale(ax)

# Formatting
ax.set_xlim(-180, 180)  # Extended x-axis to accommodate the altitude scale
ax.set_ylim(-10, 90)  # Extended y-axis to accommodate the azimuth scale
ax.set_xlabel("Azimuth (°)", color='white')
ax.set_ylabel("Altitude (°)", color='white')  # Moved down by 10 pixels
ax.set_title("Sun & Moon Paths — 23 April 2025 (Brisbane, Australia)", color='white', fontsize=20)
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
print("Plot generated successfully!")
plt.savefig("starmap.png")  # Save the plot to a file
plt.show()
