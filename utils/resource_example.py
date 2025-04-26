import os
import json
import logging
from utils.resource_utils import resource_path, ensure_directory_exists

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_json_data(file_name):
    """
    Load JSON data from a file using the resource_path utility.
    
    Args:
        file_name (str): The name of the JSON file
        
    Returns:
        dict: The loaded JSON data
    """
    try:
        # Get the absolute path to the data file
        data_path = resource_path(os.path.join("data", file_name))
        
        # Check if the file exists
        if not os.path.exists(data_path):
            logger.error(f"Data file not found: {data_path}")
            return {}
            
        # Load and return the JSON data
        with open(data_path, 'r') as f:
            return json.load(f)
            
    except Exception as e:
        logger.error(f"Error loading JSON data: {e}")
        return {}

def save_json_data(data, file_name):
    """
    Save JSON data to a file using the resource_path utility.
    
    Args:
        data (dict): The data to save
        file_name (str): The name of the JSON file
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Ensure the data directory exists
        data_dir = ensure_directory_exists("data")
        
        # Get the absolute path to the data file
        data_path = os.path.join(data_dir, file_name)
        
        # Save the JSON data
        with open(data_path, 'w') as f:
            json.dump(data, f, indent=4)
            
        logger.info(f"Data saved to {data_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error saving JSON data: {e}")
        return False

if __name__ == "__main__":
    # Example usage
    data_file = "example.json"
    
    # Load data
    data = load_json_data(data_file)
    if data:
        print(f"Loaded data: {data}")
    else:
        # Create some example data
        example_data = {
            "name": "Example",
            "value": 42,
            "items": ["item1", "item2", "item3"]
        }
        
        # Save data
        if save_json_data(example_data, data_file):
            print(f"Saved example data to {data_file}")
        else:
            print("Failed to save example data") 