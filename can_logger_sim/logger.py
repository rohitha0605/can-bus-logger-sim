import csv
import time
from datetime import datetime, timedelta

# === CONFIG ===
LOG_CSV = "logs/can_log.csv"
FAULT_LOG = "logs/fault_log.csv"
TIMEOUT_SECONDS = 4
SUMMARY_INTERVAL = 10  # seconds

# === SIGNAL DEFINITIONS ===
SIGNALS = {
    "0x101": {"name": "Speed", "unit": "km/h", "min": 0, "max": 160},
    "0x102": {"name": "RPM", "unit": "rpm", "min": 800, "max": 6000},
    "0x103": {"name": "Temp", "unit": "°C", "min": 70, "max": 110},
}

# === STATE ===
last_seen = {}
fault_counts = {can_id: 0 for can_id in SIGNALS}
last_summary = time.time()

# === HELPERS ===
def parse_row(row):
    try:
        timestamp = datetime.fromisoformat(row[0])
        can_id = row[1]
        signal = row[2]
        value = int(row[4])
        return timestamp, can_id, signal, value
    except Exception:
        return None, None, None, None

def log_fault(can_id, signal, fault_type, severity, details):
    timestamp = datetime.now().isoformat()
    row = [timestamp, can_id, signal, fault_type, severity, details]

    with open(FAULT_LOG, mode='a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(row)

    print(f"[{severity}] {fault_type} on {signal} ({can_id}): {details}")
    fault_counts[can_id] += 1

def check_timeout(now):
    for can_id, info in SIGNALS.items():
        last_time = last_seen.get(can_id)
        if not last_time:
            continue
        delta = (now - last_time).total_seconds()
        if delta > TIMEOUT_SECONDS:
            log_fault(
                can_id,
                info['name'],
                "Timeout",
                "Critical",
                f"No message in {delta:.1f} seconds"
            )
            last_seen[can_id] = now  # Avoid duplicate alerts

def check_range(can_id, signal, value):
    cfg = SIGNALS[can_id]
    if value < cfg["min"] or value > cfg["max"]:
        severity = "Critical" if abs(value - cfg["max"]) > 20 else "Warning"
        log_fault(
            can_id,
            signal,
            "Out-of-Range",
            severity,
            f"Value={value}{cfg['unit']} (Expected: {cfg['min']}–{cfg['max']})"
        )

def print_summary():
    print("==== Diagnostic Summary ====")
    for can_id, cfg in SIGNALS.items():
        seen = last_seen.get(can_id)
        status = "OK"
        if not seen:
            status = "Never Received"
        elif (datetime.now() - seen).total_seconds() > TIMEOUT_SECONDS:
            status = "Timeout"
        count = fault_counts.get(can_id, 0)
        print(f"{cfg['name']:>6} ({can_id}): {status:15} | Faults: {count}")
    print("=" * 30)

# === MAIN LOOP ===
def follow_log():
    # Prepare fault log file
    with open(FAULT_LOG, mode='w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Timestamp", "CAN_ID", "Signal", "Fault_Type", "Severity", "Details"])

    with open(LOG_CSV, "r") as f:
        f.readline()

        while True:
            pos = f.tell()
            line = f.readline()
            now = datetime.now()
            if not line:
                check_timeout(now)
                global last_summary
                if time.time() - last_summary > SUMMARY_INTERVAL:
                    print_summary()
                    last_summary = time.time()
                time.sleep(1)
                f.seek(pos)
                continue

            row = line.strip().split(",")
            timestamp, can_id, signal, value = parse_row(row)
            if not timestamp:
                continue

            last_seen[can_id] = timestamp
            print(f"[LOG] {signal}={value} at {timestamp.time()}")
            check_range(can_id, signal, value)

if __name__ == "__main__":
    print("Starting advanced CAN logger with fault detection...")
    follow_log()
