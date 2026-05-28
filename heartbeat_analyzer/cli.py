import argparse
import json
from pathlib import Path

if __package__:
    from .processor import analyze_file
else:
    from processor import analyze_file


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Analyze heartbeat JSONL files and print a JSON report."
    )
    parser.add_argument("file", help="Path to the heartbeat JSONL file")
    args = parser.parse_args()

    report = analyze_file(Path(args.file))
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
