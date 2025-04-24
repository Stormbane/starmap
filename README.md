# Star Map Generator

A Python application that generates interactive star maps showing the positions of stars, planets, the sun, and the moon in the night sky for a specific location and time.

## Features

- **Star Visualization**: Displays stars with realistic brightness, size, and color based on their temperature
- **Planet Tracking**: Shows the positions and paths of visible planets
- **Sun and Moon Paths**: Visualizes the sun and moon's paths across the sky
- **Constellation Information**: Labels stars with their constellation names
- **Customizable View**: Adjust parameters like magnitude limits and number of stars to display
- **Location and Time Specific**: Generate maps for any location on Earth at any date and time

## Requirements

- Python 3.6+
- Required Python packages:
  - ephem
  - numpy
  - matplotlib
  - pytz

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/star-map-generator.git
   cd star-map-generator
   ```

2. Install the required packages:
   ```
   pip install ephem numpy matplotlib pytz
   ```

3. Ensure you have the star catalog file (`bsc5-short.json`) in the project directory.

## Usage

### Basic Usage

Run the main script to generate a star map:

```
python starmap.py
```

This will generate a star map for the default location (Brisbane, Australia) and date (April 24, 2025).

### Customizing the Map

You can modify the following parameters in `starmap.py`:

- **Observer Location**: Change the latitude, longitude, and elevation
- **Date and Time**: Set a different date and time for the star map
- **Timezone**: Change the timezone to match your location

Example:
```python
# Observer location: New York
observer = ephem.Observer()
observer.lat = "40.7128"
observer.lon = "-74.0060"
observer.elev = 10

# Local time and UTC conversion
local_tz = timezone("America/New_York")
local_dt = local_tz.localize(datetime(2023, 8, 15, 0, 0, 0))
```

### Adjusting Star Display

In `star_plotter.py`, you can modify:

- `NAKED_EYE_MAG_LIMIT`: The magnitude limit for stars to be displayed (default: 6.5)
- `LABEL_MAG_LIMIT`: The magnitude limit for stars to have labels (default: 1.5)

## Project Structure

- `starmap.py`: Main script that generates the star map
- `star_plotter.py`: Functions for plotting stars
- `planet_plotter.py`: Functions for plotting planets
- `sunmoon_plotter.py`: Functions for plotting the sun and moon
- `constellation_utils.py`: Utilities for constellation name conversion
- `bsc5-short.json`: Star catalog data

## How It Works

1. The application loads star data from the `bsc5-short.json` catalog
2. It calculates the positions of stars, planets, the sun, and the moon for the specified location and time
3. Stars are filtered based on magnitude and visibility (above horizon)
4. The map is generated using matplotlib, with stars colored based on their temperature
5. The brightest stars are labeled with their names and magnitudes

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Star data from the Bright Star Catalog (BSC5)
- Astronomical calculations using the ephem library
- Constellation information based on IAU standards 