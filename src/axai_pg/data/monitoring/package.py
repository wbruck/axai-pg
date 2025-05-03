from pathlib import Path
import sys

# Add src directory to Python path for proper imports
src_path = str(Path(__file__).parent.parent.parent)
if src_path not in sys.path:
    sys.path.append(src_path)
