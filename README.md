# myLilaSciences

## Heartbeat Analyzer

This project parses newline-delimited JSON heartbeat logs, validates records, computes per-instrument summaries, detects missed-heartbeat gaps, and generates alerts. The output is a structured JSON report printed to stdout.

## Prerequisites

- Python 3.9+
- On macOS, use `python3`

## Setup

Install dependencies:

```bash
python3 -m pip install -r requirements.txt
```

## Usage

From the repository root:

```bash
cd heartbeat_analyzer
python3 cli.py heartbeats.jsonl
```

## Output

The report contains:

- `summaries`: per-instrument heartbeat stats
- `gaps`: detected heartbeat gaps
- `alerts`: prolonged unknown status and temperature drift alerts

Example output shape:

```json
{
  "alerts": [],
  "gaps": [],
  "summaries": {
    "SPEC-001": {
      "avg_interval_seconds": 30.5,
      "status_distribution": {
        "IDLE": 25.0,
        "RUNNING": 75.0
      },
      "time_range": {
        "start": "2025-01-15T08:00:00Z",
        "end": "2025-01-15T08:30:00Z"
      },
      "total_heartbeats": 60
    }
  }
}
```

## Project Structure

- `heartbeat_analyzer/cli.py`: CLI argument parsing and output rendering
- `heartbeat_analyzer/models.py`: heartbeat model and validation
- `heartbeat_analyzer/processor.py`: parsing, summaries, gaps, and alerts
- `heartbeat_analyzer/__main__.py`: package entrypoint for `python -m`
- `heartbeat_analyzer/heartbeats.jsonl`: sample input data

## Related Docs

- [Implementation Plan](PLAN.md)
- [Presentation Notes](PRESENTATION.md)