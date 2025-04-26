# Starmap 4K Wallpaper

A Python tool that generates 4K (3840x2160) star map wallpapers showing the night sky from any location at any date and time.

## Purpose

This tool creates high-resolution star map wallpapers (3840x2160) that accurately display:
- Stars with proper brightness and temperature-based colors
- Planets with their current positions
- Constellation lines and labels
- Celestial reference lines (equator, ecliptic)
- Moon phase information
- Location and time details

## Installation

```bash
pip install -r requirements.txt
```

## Usage

Generate a star map wallpaper with default settings (Brisbane, April 26, 2025, 22:00):

```bash
python starmap.py
```

### Command-line Options

```bash
python starmap.py --date YYYY-MM-DD --time HH:MM:SS --lat LATITUDE --lon LONGITUDE --timezone TIMEZONE --output FILENAME --setAsWallpaper
```

#### Options:

- `--date`: Date in YYYY-MM-DD format (default: 2025-04-26)
- `--time`: Time in HH:MM:SS format (default: 22:00:00)
- `--lat`: Latitude in decimal degrees (default: -27.47 for Brisbane)
- `--lon`: Longitude in decimal degrees (default: 153.02 for Brisbane)
- `--elev`: Elevation in meters (default: 0)
- `--timezone`: Timezone (default: Australia/Brisbane)
- `--output`: Output filename (default: starmap.png)
- `--setAsWallpaper`: Set the generated image as desktop wallpaper and suppress plot display

### Examples

New York City, May 15, 2025, 23:30:
```bash
python starmap.py --date 2025-05-15 --time 23:30:00 --lat 40.7128 --lon -74.0060 --timezone America/New_York
```

Tokyo, June 1, 2025, 20:00:
```bash
python starmap.py --date 2025-06-01 --time 20:00:00 --lat 35.6762 --lon 139.6503 --timezone Asia/Tokyo
```

Set as wallpaper:
```bash
python starmap.py --setAsWallpaper
```

## Creating a Standalone Executable

### Windows

1. Install PyInstaller:
```bash
pip install pyinstaller
```

2. Run PyInstaller using the Python module syntax:
```bash
python -m PyInstaller --onefile --windowed starmap.py
```

3. The executable will be in the `dist` directory.

### Linux/Mac

```bash
pip install pyinstaller
pyinstaller --onefile --windowed starmap.py
```

## Files

- `starmap.py`: Main script
- `star_plotter.py`: Star plotting functions
- `planet_plotter.py`: Planet plotting functions
- `sunmoon_plotter.py`: Sun and moon path plotting
- `constellation_plotter.py`: Constellation line plotting
- `info_plotter.py`: Location information display
- `moonphase_plotter.py`: Moon phase display
- `line_plotter.py`: Celestial reference lines
- `set_wallpaper.py`: Desktop wallpaper setting functionality
- `moonphase/`: Moon phase images

## Dependencies

- ephem: Astronomical calculations
- numpy: Numerical computations
- matplotlib: Plotting
- pytz: Timezone handling
- pillow: Image processing 