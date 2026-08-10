#!/usr/bin/env python3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from influencer_discovery.run import main

if __name__ == "__main__":
    main()
