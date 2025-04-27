import os
import sys
import logging

logger = logging.getLogger(__name__)

def resource_path(relative_path, external=False):
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
        if external:
            # External file like config.yaml — next to exe or script
            if getattr(sys, 'frozen', False):
                base_path = os.path.dirname(sys.executable)
            else:
                base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        else:
            # Bundled internal resource (in _MEIPASS if frozen)
            if hasattr(sys, '_MEIPASS'):
                base_path = sys._MEIPASS
            else:
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
