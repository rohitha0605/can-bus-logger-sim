from flask import Flask, jsonify
import csv

app = Flask(__name__)
FAULT_LOG = "logs/fault_log.csv"
#SUMMARY_LOG = "logs/summary_log.csv"

@app.route("/")
def home():
    return jsonify({"message": "CAN Logger Diagnostics API is running."})

@app.route("/faults", methods=["GET"])
def get_faults():
    faults = []
    try:
        with open(FAULT_LOG, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                faults.append(row)
    except FileNotFoundError:
        return jsonify({"error": "Fault log not found"}), 404
    return jsonify(faults)

@app.route("/summary", methods=["GET"])
def get_summary():
    summaries = []
    try:
        with open(SUMMARY_LOG, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                summaries.append(row)
    except FileNotFoundError:
        return jsonify({"error": "Summary log not found"}), 404
    return jsonify(summaries)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
