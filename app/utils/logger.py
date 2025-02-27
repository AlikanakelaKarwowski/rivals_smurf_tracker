import logging
import os

# Ensure the "logs/" directory exists
log_dir = os.path.join(os.path.dirname(__file__), "..", "logs")  
os.makedirs(log_dir, exist_ok=True)  

# Define log file path
log_file = os.path.join(log_dir, "app.log")

# Create a custom logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)  # Set global log level

# Create file handler (only log to file)
f_handler = logging.FileHandler(log_file)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
f_handler.setFormatter(formatter)

# Add only the file handler (no console output)
logger.addHandler(f_handler)
