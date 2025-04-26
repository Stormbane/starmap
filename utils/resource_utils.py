import os
import sys
import logging

logger = logging.getLogger(__name__)

def resource_path(relative_path):
    """
    Get absolute path to resource, works for Nuitka, PyInstaller, and normal execution.
    
    Args:
        relative_path (str): The relative path to the resource
        
    Returns:
        str: The absolute path to the resource
        
    Raises:
        FileNotFoundError: If the resource cannot be found
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        if hasattr(sys, '_MEIPASS'):
            base_path = sys._MEIPASS
        # Nuitka creates a temp folder and stores path in __compiled__
        elif hasattr(sys, 'frozen'):
            base_path = os.path.dirname(sys.executable)
        else:
            # Normal execution - use the directory of the script
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        full_path = os.path.join(base_path, relative_path)
        
        # Verify the path exists
        if not os.path.exists(full_path):
            logger.warning(f"Resource not found: {full_path}")
            # Return the path anyway, let the caller handle the error
            return full_path
            
        return full_path
        
    except Exception as e:
        logger.error(f"Error resolving resource path: {e}")
        # Return the original path as fallback
        return os.path.join(os.path.abspath("."), relative_path)

def ensure_directory_exists(directory_path):
    """
    Ensure that a directory exists, creating it if necessary.
    
    Args:
        directory_path (str): The path to the directory
        
    Returns:
        str: The absolute path to the directory
    """
    try:
        abs_path = os.path.abspath(directory_path)
        os.makedirs(abs_path, exist_ok=True)
        return abs_path
    except Exception as e:
        logger.error(f"Error creating directory {directory_path}: {e}")
        raise 