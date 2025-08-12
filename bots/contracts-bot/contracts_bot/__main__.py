import sys

sys.path.insert(0, ".")
import branchbot_env  # noqa: F401

from .run import run_main

if __name__ == "__main__":
    run_main()
