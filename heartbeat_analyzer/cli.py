import argparse
import json
import sys
from pathlib import Path

from .processor import analyze_file


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Analyze heartbeat JSONL files and print a JSON report."
    )
    parser.add_argument("file", help="Path to the heartbeat JSONL file")
    args = parser.parse_args()

    report = analyze_file(Path(args.file))
    json.dump(report, sys.stdout, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
