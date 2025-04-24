import ephem
from datetime import datetime
import numpy as np
from pytz import timezone, utc

# Setup observer for Brisbane
observer = ephem.Observer()
observer.lat = "-27.47"
observer.lon = "153.02"
observer.elev = 0
observer.horizon = '0'  # default horizon (flat)

# Date of interest
observer.date = "2025/04/23"

# Initialize Moon object and compute initial state
moon = ephem.Moon(observer)

# Debug: initial moon state
print("🧭 Observer Date (UTC):", observer.date)
print("🌝 Moon radius (°):", np.degrees(moon.radius))
print("🌝 Moon apparent diameter (°):", np.degrees(moon.radius) * 2)

# Calculate moonrise and moonset using upper limb (use_center=False)
moonrise_utc = observer.next_rising(moon, use_center=False).datetime()
observer.date = moonrise_utc
moon.compute(observer)
moonrise_alt = np.degrees(moon.alt)
moonrise_az = np.degrees(moon.az)

moonset_utc = observer.next_setting(moon, use_center=False).datetime()
observer.date = moonset_utc
moon.compute(observer)
moonset_alt = np.degrees(moon.alt)
moonset_az = np.degrees(moon.az)

# Convert to AEST for comparison
aest = timezone('Australia/Brisbane')
moonrise_aest = utc.localize(moonrise_utc).astimezone(aest)
moonset_aest = utc.localize(moonset_utc).astimezone(aest)

# 🌙 Output everything
print("\n🌙 Moonrise (UTC) :", moonrise_utc)
print("🌙 Moonrise (AEST):", moonrise_aest.strftime('%Y-%m-%d %H:%M:%S %Z'))
print("🌙 Altitude at Moonrise:", f"{moonrise_alt:.4f}°")
print("🌙 Azimuth at Moonrise :", f"{moonrise_az:.2f}°")

print("\n🌘 Moonset (UTC)  :", moonset_utc)
print("🌘 Moonset (AEST) :", moonset_aest.strftime('%Y-%m-%d %H:%M:%S %Z'))
print("🌘 Altitude at Moonset :", f"{moonset_alt:.4f}°")
print("🌘 Azimuth at Moonset  :", f"{moonset_az:.2f}°")

# Extra validation
if abs(moonrise_alt) < 0.5:
    print("✅ Moonrise altitude is near 0°, as expected.")
else:
    print("⚠️  Moonrise altitude is NOT near 0°. Something might be off.")

if abs(moonset_alt) < 0.5:
    print("✅ Moonset altitude is near 0°, as expected.")
else:
    print("⚠️  Moonset altitude is NOT near 0°. Something might be off.")