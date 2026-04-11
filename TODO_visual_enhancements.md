# Starmap Visual Enhancements

## Feature 1: Milky Way Band
Render the galactic plane as a soft luminous glow across the sky. Convert galactic
coordinates (l=0-360, b=-10 to +10) to RA/Dec then to observer alt/az. Draw as a
wide gaussian-blurred band with variable brightness (brighter toward galactic center
in Sagittarius, dimmer at anticenter in Auriga). Subtle blue-white tint.

**Approach**: New plotter `milkyway_plotter.py`. Sample points along the galactic
plane, convert to alt/az, render as overlapping transparent circles or a filled
contour. Z-order behind stars but above background gradient.

## Feature 2: Star Bloom/Glow
Add radial light bleed around the brightest stars (mag < 1.0). Real stars seen by
the naked eye have diffraction and scattering halos. Render as concentric transparent
circles with decreasing alpha radiating outward from each bright star. Color matches
the star's temperature color.

**Approach**: Modify `star_plotter.py`. After plotting the star scatter point, overlay
2-3 additional scatter points at the same position with increasing size and decreasing
alpha. Only for stars brighter than configurable threshold.

## Feature 3: Atmospheric Extinction
Stars near the horizon appear dimmer and redder due to thicker atmosphere. Apply
airmass-based dimming: airmass = 1/sin(altitude), extinction ~0.28 mag per airmass.
Also shift star colors toward red at low altitudes.

**Approach**: Modify alpha and color calculations in `star_plotter.py`. Apply an
altitude-dependent multiplier to both alpha (dimming) and color (reddening). Affects
all stars, strongest effect below 15 degrees altitude.

## Feature 4: Nakshatras Along the Ecliptic
Draw the ecliptic as a golden line with 27 nakshatra division boundaries marked.
Each nakshatra spans 13 deg 20 min of ecliptic longitude. Label each visible nakshatra.
Highlight the nakshatra the Moon currently occupies.

**Approach**: New plotter `nakshatra_plotter.py`. Convert ecliptic coordinates to
RA/Dec to alt/az. Draw the ecliptic line, then mark boundaries and labels. The 27
nakshatras start from 0 deg Aries (Ashwini). Moon's ecliptic longitude determines
its current nakshatra.

## Feature 5: Brightest Deep Sky Objects
Render the most prominent naked-eye deep sky objects as soft fuzzy patches:
- M42 (Orion Nebula) - pinkish glow
- M45 (Pleiades) - blue cluster haze
- Large Magellanic Cloud - diffuse patch
- Small Magellanic Cloud - smaller diffuse patch
- Omega Centauri (NGC 5139) - bright globular
- 47 Tucanae (NGC 104) - globular cluster
- M7 (Ptolemy Cluster) - open cluster in Scorpius

**Approach**: New plotter `deepsky_plotter.py`. Fixed catalog of ~10 objects with
RA/Dec, angular size, color, and brightness. Render as gaussian blobs using scatter
with large size and low alpha. Only show objects above horizon.
