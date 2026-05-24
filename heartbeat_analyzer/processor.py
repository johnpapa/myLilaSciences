import json
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from models import HeartbeatRecord

# parse_heartbeat_file reads a newline-delimited JSONL file and returns validated
# HeartbeatRecord instances. It skips malformed JSON lines and invalid records,
# printing warnings to stderr so parsing can continue on the rest of the file.
def parse_heartbeat_file(file_path: Path) -> List[HeartbeatRecord]:
    records: List[HeartbeatRecord] = []
    path = Path(file_path)

    with path.open("r", encoding="utf-8") as input_file:
        for line_number, line in enumerate(input_file, start=1):
            text = line.strip()
            if not text:
                # Ignore blank lines in the input file.
                continue

            try:
                raw = json.loads(text)
            except json.JSONDecodeError as exc:
                print(
                    f"Warning: Skipping malformed JSON line {line_number}: {exc}",
                    file=sys.stderr,
                )
                continue

            try:
                record = HeartbeatRecord(**raw)
            except Exception as exc:
                print(
                    f"Warning: Skipping invalid heartbeat line {line_number}: {exc}",
                    file=sys.stderr,
                )
                continue

            records.append(record)

    return records


    # Normalize timestamps to UTC and format them as ISO 8601 strings.
def format_timestamp(timestamp: datetime) -> str:
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=timezone.utc)
    return timestamp.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Group heartbeat records by instrument ID.
def group_by_instrument(records: List[HeartbeatRecord]) -> Dict[str, List[HeartbeatRecord]]:
    grouped: Dict[str, List[HeartbeatRecord]] = defaultdict(list)
    for record in records:
        grouped[record.instrument_id].append(record)
    return grouped


    # Return the average interval in seconds between consecutive heartbeats.
def average_interval_seconds(sorted_records: List[HeartbeatRecord]) -> float:
    if len(sorted_records) < 2:
        return 0.0

    intervals = [
        (sorted_records[i].timestamp - sorted_records[i - 1].timestamp).total_seconds()
        for i in range(1, len(sorted_records))
    ]
    return sum(intervals) / len(intervals)

# Build a summary report for one instrument.
def summarize_instrument(sorted_records: List[HeartbeatRecord]) -> Dict[str, Any]:
    
    total = len(sorted_records)
    status_counts = Counter(record.status.value for record in sorted_records)

    distribution = {
        status: round((count / total) * 100.0, 1)
        for status, count in status_counts.items()
    }

    return {
        "total_heartbeats": total,
        "time_range": {
            "start": format_timestamp(sorted_records[0].timestamp),
            "end": format_timestamp(sorted_records[-1].timestamp),
        },
        "status_distribution": distribution,
        "avg_interval_seconds": round(average_interval_seconds(sorted_records), 1),
    }

 #Detect heartbeat gaps longer than twice the average interval.
def detect_gaps(sorted_records: List[HeartbeatRecord], avg_interval: float) -> List[Dict[str, Any]]:
   
    gaps: List[Dict[str, Any]] = []
    if avg_interval <= 0:
        return gaps

    threshold = avg_interval * 2
    for prev, curr in zip(sorted_records, sorted_records[1:]):
        duration = (curr.timestamp - prev.timestamp).total_seconds()
        if duration > threshold:
            gaps.append({
                "instrument_id": curr.instrument_id,
                "start": format_timestamp(prev.timestamp),
                "end": format_timestamp(curr.timestamp),
                "duration_seconds": round(duration, 1),
            })
    return gaps

#Detect runs of 3 or more consecutive UNKNOWN heartbeat statuses.
def detect_prolonged_unknown(sorted_records: List[HeartbeatRecord]) -> List[Dict[str, Any]]:
    
    alerts: List[Dict[str, Any]] = []
    streak: List[HeartbeatRecord] = []

    def flush() -> None:
        if len(streak) >= 3:
            alerts.append({
                "instrument_id": streak[0].instrument_id,
                "alert_type": "PROLONGED_UNKNOWN",
                "message": f"{len(streak)} consecutive UNKNOWN heartbeats",
                "timestamps": [format_timestamp(r.timestamp) for r in streak],
            })

    for record in sorted_records:
        if record.status.name == "UNKNOWN":
            streak.append(record)
        else:
            flush()
            streak = []

    flush()
    return alerts

#Detect sudden temperature changes greater than 5.0°C.
def detect_temperature_drift(sorted_records: List[HeartbeatRecord]) -> List[Dict[str, Any]]:
    alerts: List[Dict[str, Any]] = []

    for prev, curr in zip(sorted_records, sorted_records[1:]):
        prev_temp = prev.detail.get("temperature_c")
        curr_temp = curr.detail.get("temperature_c")

        if isinstance(prev_temp, (int, float)) and isinstance(curr_temp, (int, float)):
            if abs(curr_temp - prev_temp) > 5.0:
                alerts.append({
                    "instrument_id": curr.instrument_id,
                    "alert_type": "TEMPERATURE_DRIFT",
                    "message": f"Temperature changed by {round(abs(curr_temp - prev_temp), 1)}C",
                    "timestamp": format_timestamp(curr.timestamp),
                    "detail": {"previous": prev_temp, "current": curr_temp},
                })

    return alerts

#Analyze the entire file and produce the final report.
def analyze_file(file_path: Path) -> Dict[str, Any]:
    records = parse_heartbeat_file(file_path)
    grouped = group_by_instrument(records)

    summaries: Dict[str, Any] = {}
    gaps: List[Dict[str, Any]] = []
    alerts: List[Dict[str, Any]] = []

    for instrument_id, records_for_instrument in grouped.items():
       sorted_records = sorted(records_for_instrument, key=lambda r: r.timestamp)
    
    summaries[instrument_id] = summarize_instrument(sorted_records)
    avg_interval = summaries[instrument_id]["avg_interval_seconds"]

    gaps.extend(detect_gaps(sorted_records, avg_interval))
    alerts.extend(detect_prolonged_unknown(sorted_records))
    alerts.extend(detect_temperature_drift(sorted_records))

    return {"summaries": summaries, "gaps": gaps, "alerts": alerts}
