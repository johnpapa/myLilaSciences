"""Simple tests for the heartbeat analyzer."""

from datetime import datetime, timezone
from heartbeat_analyzer.models import HeartbeatRecord, HeartbeatStatus
from heartbeat_analyzer.processor import (
    average_interval_seconds,
    detect_gaps,
    detect_prolonged_unknown,
    detect_temperature_drift,
    summarize_instrument,
)


def make_record(ts, status="RUNNING", temp=None, instrument="SPEC-001"):
    """Helper to create a HeartbeatRecord quickly."""
    detail = {"temperature_c": temp} if temp is not None else {}

    return HeartbeatRecord(
        timestamp=datetime(2025, 1, 15, ts[0], ts[1], ts[2], tzinfo=timezone.utc),
        instrument_id=instrument,
        status=HeartbeatStatus(status),
        message="test",
        detail=detail,
    )


# --- Model tests ---


def test_valid_status():
    r = make_record((8, 0, 0), "IDLE")
    assert r.status == HeartbeatStatus.IDLE


def test_invalid_status_becomes_unknown():
    r = HeartbeatRecord(
        timestamp="2025-01-15T08:00:00Z",
        instrument_id="X",
        status="BANANA",
        message="test",
    )
    assert r.status == HeartbeatStatus.UNKNOWN


# --- Summary tests ---


def test_summarize_instrument():
    records = [
        make_record((8, 0, 0), "IDLE"),
        make_record((8, 0, 30), "RUNNING"),
    ]
    summary = summarize_instrument(records)
    assert summary["total_heartbeats"] == 2
    assert summary["avg_interval_seconds"] == 30.0


# --- Gap detection ---


def test_detect_gaps():
    # 4 records at 30s intervals, then a 5-minute gap
    # avg interval = (30+30+30+300)/4 = 97.5, threshold = 195
    # 300s > 195 so it's a gap
    records = [
        make_record((8, 0, 0)),
        make_record((8, 0, 30)),
        make_record((8, 1, 0)),
        make_record((8, 1, 30)),
        make_record((8, 6, 30)),  # 300s gap
    ]
    avg = average_interval_seconds(records)
    gaps = detect_gaps(records, avg)
    assert len(gaps) == 1
    assert gaps[0]["duration_seconds"] == 300.0


def test_no_gaps():
    records = [
        make_record((8, 0, 0)),
        make_record((8, 0, 30)),
        make_record((8, 1, 0)),
    ]
    avg = average_interval_seconds(records)
    gaps = detect_gaps(records, avg)
    assert len(gaps) == 0


# --- Prolonged unknown ---


def test_prolonged_unknown_detected():
    records = [
        make_record((8, 0, 0), "UNKNOWN"),
        make_record((8, 0, 30), "UNKNOWN"),
        make_record((8, 1, 0), "UNKNOWN"),
    ]
    alerts = detect_prolonged_unknown(records)
    assert len(alerts) == 1
    assert alerts[0]["alert_type"] == "PROLONGED_UNKNOWN"


def test_no_prolonged_unknown():
    records = [
        make_record((8, 0, 0), "UNKNOWN"),
        make_record((8, 0, 30), "RUNNING"),
        make_record((8, 1, 0), "UNKNOWN"),
    ]
    alerts = detect_prolonged_unknown(records)
    assert len(alerts) == 0


# --- Temperature drift ---


def test_temperature_drift_detected():
    records = [
        make_record((8, 0, 0), temp=20.0),
        make_record((8, 0, 30), temp=26.0),  # 6 degree change
    ]
    alerts = detect_temperature_drift(records)
    assert len(alerts) == 1
    assert alerts[0]["alert_type"] == "TEMPERATURE_DRIFT"


def test_no_temperature_drift():
    records = [
        make_record((8, 0, 0), temp=20.0),
        make_record((8, 0, 30), temp=22.0),  # only 2 degrees
    ]
    alerts = detect_temperature_drift(records)
    assert len(alerts) == 0
