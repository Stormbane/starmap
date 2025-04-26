import os
import sys
import ctypes
import logging
from pathlib import Path
from utils.resource_utils import resource_path

# Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def set_wallpaper(image_path):
    """
    Set the specified image as the desktop wallpaper on Windows.
    
    Args:
        image_path (str): Path to the image file to set as wallpaper
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Convert to absolute path using resource_path
        abs_path = resource_path(image_path)
        
        # Check if file exists
        if not os.path.exists(abs_path):
            logger.error(f"Image file not found: {abs_path}")
            return False
            
        # Windows API constants
        SPI_SETDESKWALLPAPER = 20
        SPIF_UPDATEINIFILE = 0x01
        SPIF_SENDCHANGE = 0x02
        
        # Set the wallpaper using Windows API
        # SystemParametersInfoW updates Windows system parameters
        # Parameters:
        # uiAction (SPI_SETDESKWALLPAPER=20): The system parameter to set
        # uiParam (0): Additional parameter info, unused for wallpaper
        # pvParam (abs_path): Pointer to wallpaper path string
        # fWinIni (flags): Flags for how to apply the change
        #   SPIF_UPDATEINIFILE (0x01): Write change to user profile
        #   SPIF_SENDCHANGE (0x02): Notify applications of change
        # Returns: True if successful, False if failed
        # Example: SystemParametersInfoW(20, 0, "C:\\wallpaper.jpg", 3)
        result = ctypes.windll.user32.SystemParametersInfoW(
            SPI_SETDESKWALLPAPER, 0, abs_path, 
            SPIF_UPDATEINIFILE | SPIF_SENDCHANGE
        )
        
        
        if result:
            logger.info(f"Successfully set wallpaper to: {abs_path}")
            return True
        else:
            logger.error("Failed to set wallpaper")
            return False
            
    except Exception as e:
        logger.error(f"Error setting wallpaper: {e}")
        return False

if __name__ == "__main__":
    # If run directly, take the image path as a command line argument
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
        set_wallpaper(image_path)
    else:
        logger.error("Please provide an image path as an argument") 