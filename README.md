# mylilathingy

# Heartbeat Analyzer

## Overview
This project parses newline-delimited JSON heartbeat logs, validates records, computes per-instrument summaries, detects missed-heartbeat gaps, and generates alerts. The output is a structured JSON report printed to stdout.

## Implementation Plan

### 1. Data Model
- Create `heartbeat_analyzer/models.py`
- Define `HeartbeatStatus` enum: `IDLE`, `RUNNING`, `UNKNOWN`
- Define `HeartbeatRecord` Pydantic model with:
  - `timestamp: datetime`
  - `instrument_id: str`
  - `status: HeartbeatStatus`
  - `message: str`
  - `detail: Dict[str, Any]`
- Add validation to normalize invalid status values to `UNKNOWN`

### 2. Parsing
- Read the JSONL file line by line
- Parse JSON and instantiate `HeartbeatRecord`
- Skip malformed lines with warnings to stderr
- Group records by `instrument_id`

### 3. Per-Instrument Summary
- Sort heartbeats by timestamp
- Compute:
  - total heartbeat count
  - time range start/end
  - status distribution percentages
  - average interval in seconds

### 4. Gap Detection
- Detect gaps where interval between consecutive heartbeats exceeds `2x average interval`
- Report instrument ID, gap start/end timestamps, and duration

### 5. Alert Generation
- `PROLONGED_UNKNOWN`: 3+ consecutive `UNKNOWN` heartbeats
- `TEMPERATURE_DRIFT`: temperature changes by more than `5.0` degrees between consecutive heartbeats when `temperature_c` is present

### 6. CLI
- Add `heartbeat_analyzer/cli.py`
- Use `argparse` to accept the JSONL file path
- Print JSON report to stdout
- Add `__main__.py` so package runs with `python -m heartbeat_analyzer`

### 7. Tests
- Add `tests/test_heartbeat_analyzer.py`
- Cover malformed line handling, invalid status normalization, summaries, gap detection, and alerts

## Presentation Structure

### Opening (4–5 min)
- Problem statement and goal
- Constraints and expected output

### Approach (8–10 min)
- Pipeline stages:
  1. Data model/validation
  2. Parsing
  3. Aggregation
  4. Gap detection
  5. Alerts
- Explain what was built and why

### Decisions & Trade-offs (6–7 min)
- Why Pydantic
- Why invalid status → `UNKNOWN`
- Why counts-based status distribution
- Why `2x avg interval` gap rule

### Results (6–7 min)
- JSON output structure
- Example summary, gap, and alerts
- Mention tests

### Wrap-up (3–4 min)
- What’s complete
- What to extend next:
  - configurable thresholds
  - streaming large files
  - additional alert types
  - alternate outputs

## Notes
- The focus is on clean structure and clarity.
- The data model is the foundation that makes later processing simpler and safer.