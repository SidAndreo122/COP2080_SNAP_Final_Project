import sys
import os

# tells pytest to add project root to path so imports like app.tool work

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))