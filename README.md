# Sky Map Generator

A simple Windows UI application that allows users to generate sky map images with customizable options and set them as wallpapers.

## Features

- Modern dark-themed UI
- Multiple style options (abstract, nature, space, minimal)
- Color scheme selection (warm, cool, monochrome, vibrant)
- Resolution options (1920x1080, 2560x1440, 3840x2160)
- Option to set generated image as wallpaper
- Automatic image opening after generation

## Installation

1. Make sure you have Python 3.7+ installed
2. Install the required packages:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the application:
```bash
python skymap_ui.py
```

2. Select your desired options:
   - Choose an image style
   - Select a color scheme
   - Pick a resolution
   - Check "Set as Wallpaper" if you want to set the generated image as your desktop background

3. Click "Generate Image" to create and view the image

## Note

Currently, the app generates a simple white placeholder image. You can modify the `generate_image` method in `skymap_ui.py` to implement your own sky map generation logic. 