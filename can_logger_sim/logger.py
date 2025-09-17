import csv
import argparse
import time
from datetime import datetime
from collections import defaultdict

# ========== ARGUMENT PARSING ==========
parser = argparse.ArgumentParser()
parser.add_argument("--timeout", type=float, default=3.0, help="Timeout in seconds")
parser.add_argument("--logfile", type=str, default="logs/can_log.csv", help="Log file to read")
parser.add_argument("--faultlog", type=str, default="logs/fault_log.csv", help="File to write faults")
parser.add_argument("--summary_interval", type=int, default=30, help="Diagnostic summary interval (sec)")
args = parser.parse_args()

TIMEOUT_SEC = args.timeout
LOG_FILE = args.logfile
FAULT_LOG_FILE = args.faultlog
SUMMARY_INTERVAL = args.summary_interval

print(f"\n[CONFIG] Timeout: {TIMEOUT_SEC} sec")
print(f"[CONFIG] Log file: {LOG_FILE}")
print(f"[CONFIG] Fault log: {FAULT_LOG_FILE}")
print(f"[CONFIG] Summary every: {SUMMARY_INTERVAL} sec\n")

# ========== SIGNAL DEFINITIONS ==========
SIGNALS = {
    "0x101": "Speed",
    "0x102": "RPM",
    "0x103": "Temp"
}

# ========== STATE ==========
last_seen = {}
fault_counts = defaultdict(int)
dtc_map = {
    "0x101": "P0500",  # Speed Sensor Error
    "0x102": "P0300",  # RPM Sensor Fault
    "0x103": "P0128",  # Coolant Temp
}

# ========== FUNCTIONS ==========

def log_fault(signal_id, msg):
    fault_counts[signal_id] += 1
    dtc = dtc_map.get(signal_id, "UNKNOWN")
    with open(FAULT_LOG_FILE, mode='a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([datetime.now(), signal_id, SIGNALS.get(signal_id, "Unknown"), msg, dtc, "Critical"])
    print(f"[Critical] {msg}")

def print_summary():
    print("==== Diagnostic Summary ====")
    for sid, name in SIGNALS.items():
        faults = fault_counts[sid]
        status = "OK" if faults == 0 else "⚠️"
        print(f"{name:>6} ({sid}): OK\t| Faults: {faults}")
    print("=" * 30)

def check_timeout(now):
    for signal_id, last_time in last_seen.items():
        delta = (now - last_time).total_seconds()
        if delta > TIMEOUT_SEC:
            log_fault(signal_id, f"Timeout on {SIGNALS[signal_id]} ({signal_id}): No message in {delta:.1f} seconds")

def follow_log():
    last_summary_time = time.time()

    with open(LOG_FILE, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                timestamp = datetime.fromisoformat(row["Timestamp"])
                signal_id = row["CAN_ID"]
                value = row.get("Decoded_Value", "N/A")
                signal_name = SIGNALS.get(signal_id, "Unknown")

                print(f"[LOG] {signal_name}={value} at {timestamp.time()}")
                last_seen[signal_id] = timestamp
            except Exception as e:
                print(f"[Error in parsing row]: {e}")

        # Move to the end of file to follow
        while True:
            now = datetime.now()
            check_timeout(now)

            if time.time() - last_summary_time > SUMMARY_INTERVAL:
                print_summary()
                last_summary_time = time.time()

            line = f.readline()
            if not line:
                time.sleep(1)
                continue

            try:
                row = dict(zip(reader.fieldnames, next(csv.reader([line]))))
                timestamp = datetime.fromisoformat(row["Timestamp"])
                signal_id = row["CAN_ID"]
                value = row.get("Decoded_Value", "N/A")
                signal_name = SIGNALS.get(signal_id, "Unknown")

                print(f"[LOG] {signal_name}={value} at {timestamp.time()}")
                last_seen[signal_id] = timestamp
            except Exception as e:
                print(f"[Error in animate]: {e}")

# ========== START ==========
print("Starting advanced CAN logger with fault detection...")
with open(FAULT_LOG_FILE, mode='w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(["Timestamp", "Signal_ID", "Signal_Name", "Fault_Message", "DTC_Code", "Severity"])

follow_log()
