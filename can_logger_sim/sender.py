import time
import random
import csv
import json
from datetime import datetime

LOG_CSV = "logs/can_log.csv"
LOG_JSON = "logs/can_log.json"

MESSAGE_DEFINITIONS = [
    {"id": "0x101", "name": "Speed", "unit": "km/h", "min": 0, "max": 160},
    {"id": "0x102", "name": "RPM", "unit": "rpm", "min": 800, "max": 6000},
    {"id": "0x103", "name": "Temp", "unit": "°C", "min": 70, "max": 110},
]

def generate_message(msg_def):
    value = random.randint(msg_def["min"], msg_def["max"])
    data_bytes = value.to_bytes(2, byteorder="big").hex()
    timestamp = datetime.now().isoformat()
    return {
        "timestamp": timestamp,
        "can_id": msg_def["id"],
        "signal": msg_def["name"],
        "data_bytes": data_bytes,
        "decoded_value": value,
        "unit": msg_def["unit"]
    }

def simulate_can_sender():
    print("Starting multi-ID CAN sender...")

    # Write headers
    with open(LOG_CSV, mode='w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Timestamp", "CAN_ID", "Signal", "Data_Bytes", "Decoded_Value", "Unit"])

    with open(LOG_JSON, mode='w') as f:
        json.dump([], f)  # start with empty JSON array

    while True:
        for msg_def in MESSAGE_DEFINITIONS:
            message = generate_message(msg_def)

            # Append to CSV
            with open(LOG_CSV, mode='a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    message["timestamp"],
                    message["can_id"],
                    message["signal"],
                    message["data_bytes"],
                    message["decoded_value"],
                    message["unit"]
                ])

            # Append to JSON
            try:
                with open(LOG_JSON, "r") as f:
                    data = json.load(f)
            except json.JSONDecodeError:
                data = []

            data.append(message)

            with open(LOG_JSON, "w") as f:
                json.dump(data[-100:], f, indent=2)  # keep only last 100 messages

            print(f"[SENT] {message['timestamp']} | {message['signal']}={message['decoded_value']} {message['unit']}")

            time.sleep(1)

if __name__ == "__main__":
    simulate_can_sender()
