# Implementation Plan

## 1. Data Model

- Create `heartbeat_analyzer/models.py`
- Define `HeartbeatStatus` enum: `IDLE`, `RUNNING`, `UNKNOWN`
- Define `HeartbeatRecord` model with:
- `timestamp: datetime`
- `instrument_id: str`
- `status: HeartbeatStatus`
- `message: str`
- `detail: Dict[str, Any]`
- Normalize invalid status values to `UNKNOWN`

## 2. Parsing

- Read the JSONL file line by line
- Parse JSON and instantiate `HeartbeatRecord`
- Skip malformed lines with warnings to stderr
- Group records by `instrument_id`

## 3. Per-Instrument Summary

- Sort heartbeats by timestamp
- Compute:
- total heartbeat count
- time range start/end
- status distribution percentages
- average interval in seconds

## 4. Gap Detection

- Detect gaps where interval between consecutive heartbeats exceeds `2x average interval`
- Report instrument ID, gap start/end timestamps, and duration

## 5. Alert Generation

- `PROLONGED_UNKNOWN`: 3+ consecutive `UNKNOWN` heartbeats
- `TEMPERATURE_DRIFT`: temperature changes by more than `5.0` degrees between consecutive heartbeats when `temperature_c` is present

## 6. CLI

- Add `heartbeat_analyzer/cli.py`
- Use `argparse` to accept the JSONL file path
- Print JSON report to stdout
- Add package entrypoint so it runs with `python -m heartbeat_analyzer`

## 7. Tests

- Add `tests/test_heartbeat_analyzer.py`
- Cover malformed line handling, invalid status normalization, summaries, gap detection, and alerts
