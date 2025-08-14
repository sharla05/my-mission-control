from datetime import datetime, timedelta

from my_mission_control.entity.log_entry import LogEntry


# Helper to format timestamp
def format_ts(dt: datetime) -> str:
    return dt.strftime("%Y%m%d %H:%M:%S.%f")[:-3]


# Helper to generate log line
def make_log_line(ts: datetime, sat_id: int, red_high: float, yellow_high: float, yellow_low: float, red_low: float, raw_value: float, component: str) -> str:
    return f"{format_ts(ts)}|{sat_id}|{red_high}|{yellow_high}|{yellow_low}|{red_low}|{raw_value}|{component}"


def make_log_entry(ts: datetime, sat_id: int, red_high: float, yellow_high: float, yellow_low: float, red_low: float, raw_value: float, component: str) -> LogEntry:
    return LogEntry(ts, int(sat_id), int(red_high), int(yellow_high), int(yellow_low), int(red_low), float(raw_value), component)
