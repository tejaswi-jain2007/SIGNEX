"""
Root launcher for the NTRO SIGINT Desktop GUI Workstation.
"""

import sys
from pathlib import Path

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ntro_sigint.gui.main_window import launch_gui

if __name__ == "__main__":
    launch_gui()
