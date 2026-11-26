"""Entry point: render the Thursday 26 November 2026 broadsheet.

Usage:
    python3 main.py            # writes entry.png next to this file
    python3 main.py out.png    # writes the render to out.png instead

Stdlib only. The render is deterministic: running it twice produces
byte-identical PNGs.
"""

import os
import sys

from broadsheet import render


def main(argv):
    out = argv[1] if len(argv) > 1 else os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "entry.png")
    render().save(out)
    print("wrote", out)


if __name__ == "__main__":
    main(sys.argv)
