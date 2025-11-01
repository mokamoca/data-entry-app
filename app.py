from flask import Flask, render_template, request, send_file
import csv
import os
from datetime import datetime

app = Flask(__name__)

# 保存先
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
CSV_PATH = os.path.join(DATA_DIR, "records_v2.csv")  # 新しい列構成に変更
os.makedirs(DATA_DIR, exist_ok=True)

def ensure_header():
    """CSVが無い/空ならヘッダを書き込む（v2：shift, machine, model, shots）"""
    if not os.path.exists(CSV_PATH) or os.path.getsize(CSV_PATH) == 0:
        with open(CSV_PATH, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "shift", "machine", "model", "shots"])

def append_record(shift: str, machine: str, model: str, shots: int):
    ensure_header()
    ts = datetime.now().isoformat(timespec="seconds")
    with open(CSV_PATH, "a", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow([ts, shift, machine, model, shots])

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
    # 受け取り（空白除去）
    shift   = request.form.get("shift", "").strip()      # 勤務帯 A/B/C
    machine = request.form.get("machine", "").strip()    # 号機 2~6
    model   = request.form.get("model", "").strip()      # 機種名 sample1~10
    shots_raw = request.form.get("shots", "0").strip()

    # 数値バリデーション
    try:
        shots = int(shots_raw)
        if shots < 0:
            shots = 0
    except ValueError:
        shots = 0

    append_record(shift, machine, model, shots)
    return render_template("result.html", shift=shift, machine=machine, model=model, shots=shots)

@app.route("/records", methods=["GET"])
def records():
    rows = read_records(limit=50)
    return render_template("records.html", rows=rows)

@app.route("/export", methods=["GET"])
def export_csv():
    ensure_header()
    return send_file(
        CSV_PATH,
        mimetype="text/csv; charset=utf-8",
        as_attachment=True,
        download_name="records_v2.csv",
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
