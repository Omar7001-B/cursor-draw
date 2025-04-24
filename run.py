#!/usr/bin/env python
# Simple script to run the CursorDraw application

import os
import sys
import subprocess

if __name__ == "__main__":
    # Get the absolute path to the src directory
    src_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
    main_script = os.path.join(src_dir, "main.py")
    
    # Run the main.py script
    try:
        subprocess.run([sys.executable, main_script], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running the application: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nApplication closed by user.")
        sys.exit(0) 