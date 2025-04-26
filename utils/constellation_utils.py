import json
import logging
from pathlib import Path
from utils.resource_utils import resource_path

def get_constellation_full_name(abbreviation):
    """
    Convert a constellation abbreviation to its full name.
    
    Parameters:
    -----------
    abbreviation : str
        The three-letter constellation abbreviation (e.g., 'Psc', 'Peg', 'Cas')
        
    Returns:
    --------
    str
        The full name of the constellation, or the abbreviation if not found
    """
    try:
        # Load constellation map from JSON file using resource_path
        json_path = resource_path('data/constellations.json')
        if not Path(json_path).exists():
            logging.error("Constellation map file not found. Using hardcoded fallback.")
        
        with open(json_path, 'r') as f:
            constellation_map = json.load(f)
            
        return constellation_map.get(abbreviation, abbreviation)
    except Exception as e:
        logging.error(f"Error loading constellation map: {e}")
        return _get_constellation_full_name_fallback(abbreviation)
