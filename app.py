from flask import Flask, render_template, request, send_file
import csv
import os
from datetime import datetime

app = Flask(__name__)

# 保存先
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
CSV_PATH = os.path.join(DATA_DIR, "records.csv")
os.makedirs(DATA_DIR, exist_ok=True)

def ensure_header():
    if not os.path.exists(CSV_PATH) or os.path.getsize(CSV_PATH) == 0:
        # Excelで文字化けしにくい utf-8-sig
        with open(CSV_PATH, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "operator", "machine", "shots"])

def append_record(operator: str, machine: str, shots: int):
    ensure_header()
    ts = datetime.now().isoformat(timespec="seconds")
    with open(CSV_PATH, "a", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow([ts, operator, machine, shots])

def read_records(limit: int = 50):
    if not os.path.exists(CSV_PATH) or os.path.getsize(CSV_PATH) == 0:
        return []
    with open(CSV_PATH, "r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    rows.sort(key=lambda r: r["timestamp"], reverse=True)
    return rows[:limit]

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/submit", methods=["POST"])
def submit():
    operator = request.form.get("operator", "").strip()
    machine  = request.form.get("machine", "").strip()
    shots_raw = request.form.get("shots", "0").strip()

    try:
        shots = int(shots_raw)
        if shots < 0:
            shots = 0
    except ValueError:
        shots = 0

    append_record(operator, machine, shots)
    return render_template("result.html", operator=operator, machine=machine, shots=shots)

@app.route("/records", methods=["GET"])
def records():
    rows = read_records(limit=50)
    return render_template("records.html", rows=rows)

@app.route("/export", methods=["GET"])
def export_csv():
    """CSVをそのままダウンロード"""
    ensure_header()
    return send_file(
        CSV_PATH,
        mimetype="text/csv; charset=utf-8",
        as_attachment=True,
        download_name="records.csv",
    )

if __name__ == "__main__":
    # スマホから同一LANで使うなら 0.0.0.0 に変更して実行
    app.run(host="0.0.0.0", port=5000, debug=True)
