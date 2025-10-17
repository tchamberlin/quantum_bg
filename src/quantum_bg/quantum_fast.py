"""Fast entry point that ensures Python runs in optimized mode.

This module exists to provide a convenient entry point for production use.
It's equivalent to running: python -O -m quantum_bg.quantum
"""

import sys
import os

if __debug__:
    # Re-execute with optimization flag
    os.execvp(sys.executable, [sys.executable, '-O'] + sys.argv)

# If we get here, we're already in optimized mode
from quantum_bg.quantum import main

if __name__ == "__main__":
    main()
