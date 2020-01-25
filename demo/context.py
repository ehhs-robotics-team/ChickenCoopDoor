import os
import sys

# Allows test and development files to access settings.py
# Use: 
# "from context import settings"
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import settings