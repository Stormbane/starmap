import os
import requests
from PIL import Image, ImageDraw
from io import BytesIO

# --- Configuration ---
moonphase_folder = "moonphase"
base_url = "https://svs.gsfc.nasa.gov/vis/a000000/a005400/a005416/frames/730x730_1x1_30p/moon.{:04d}.jpg"
frames_per_day = 24  # 1 frame per hour
num_days = 28  # Just one day for now

# Create folder if it doesn't exist
os.makedirs(moonphase_folder, exist_ok=True)

# --- Functions ---
def download_image(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return Image.open(BytesIO(response.content))
    except Exception as e:
        print(f"Failed to download {url}: {e}")
        return None

def crop_round_moon(img, extra_padding=10):
    img = img.convert("RGBA")
    w, h = img.size

    # Assume Moon is centered
    center_x = w // 2
    center_y = h // 2
    radius = min(center_x, center_y) - 30

    # Increase radius by padding
    radius += extra_padding

    # Create mask
    mask = Image.new('L', (w, h), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse(
        (center_x - radius, center_y - radius, center_x + radius, center_y + radius),
        fill=255
    )

    # Apply mask
    new_img = Image.new("RGBA", (w, h))
    new_img.paste(img, (0, 0), mask)
    return new_img

# --- Main Loop ---
for day in range(num_days):
    frame_number = day * frames_per_day + 1
    url = base_url.format(frame_number)
    print(f"Downloading Day {day+1} from {url}...")
    img = download_image(url)
    if img:
        img = crop_round_moon(img, extra_padding=10)
        save_path = os.path.join(moonphase_folder, f"moon_day_{day+1:02d}.png")
        img.save(save_path)
        print(f"Saved: {save_path}")

print("✅ Done!")
