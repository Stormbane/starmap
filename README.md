# Sky Map Generator

A Python application that generates accurate night sky maps for use as desktop wallpapers.

## Features

- Accurate planet and star positions based on your location and time
- Configurable resolution options (1080p, 1440p, 4K) in config.yaml
- Automatic wallpaper setting
- Configurable planet visibility and appearance

## Requirements

- Python 3.7+
- Required packages listed in requirements.txt

## Installation

```bash
pip install -r requirements.txt
```

## Usage

Run the application:
```bash
python starmap.py
```

The application will:
1. Generate a sky map based on your current location and time
2. Display the visible planets and stars
3. Save the image and optionally set it as your wallpaper

## Command Line Arguments

```bash
python starmap.py [options]
```

Options:
- `--date YYYY-MM-DD`     Date in YYYY-MM-DD format (default: current date)
- `--time HH:MM:SS`       Time in HH:MM:SS format (default: 22:00:00)
- `--lat DECIMAL`         Latitude in decimal degrees (default: -27.47)
- `--lon DECIMAL`         Longitude in decimal degrees (default: 153.02)
- `--elev METERS`         Elevation in meters (default: 0)
- `--timezone TIMEZONE`   Timezone (default: Australia/Brisbane)
- `--output FILENAME`     Output filename (default: starmap.png)
- `--setAsWallpaper`      Set the generated image as desktop wallpaper

Example:
```bash
python starmap.py --date 2024-04-15 --time 20:00:00 --lat 40.7128 --lon -74.0060 --timezone America/New_York --setAsWallpaper
python starmap.py --time 20:00:00 --lat -27.47 --lon 153.02 --timezone Australia/Brisbane --setAsWallpaper
python starmap.py --lat 35.6762 --lon 139.6503 --timezone Asia/Tokyo --output tokyo_stars.png
python starmap.py --lat 51.5074 --lon -0.1278 --timezone Europe/London --date 2024-12-21 --time 23:00:00

```

## Configuration

Edit `config.yaml` to customize:
- Planet colors and symbols
- Visible celestial bodies
- Resolution options (1080p, 1440p, 4K)
- Other display settings 