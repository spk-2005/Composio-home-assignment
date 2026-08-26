import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agent.pipeline import run_first_pass


if __name__ == "__main__":
    run_first_pass()
