"""
Logging Configuration
Centralized logging setup for the application
"""

import logging
import sys

def setup_logging():
    """
    Configure application-wide logging
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Set specific loggers
    logging.getLogger('werkzeug').setLevel(logging.WARNING)  # Reduce Flask request logs
    logging.getLogger('pymongo').setLevel(logging.WARNING)  # Reduce MongoDB logs
