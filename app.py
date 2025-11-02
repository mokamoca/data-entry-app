from datetime import date, datetime
from flask import Flask, render_template, request, redirect, url_for, send_file, flash
from sqlalchemy import create_engine, Column, Integer, String, Date, Float, Text, inspect
from sqlalchemy.orm import declarative_base, sessionmaker
import pandas as pd

app = Flask(__name__)
app.secret_key = "change-me"  # フラッシュメッセージ用

# --- DB セットアップ（SQLite） ---
DB_PATH = "production_log.db"
engine = create_engine(f"sqlite:///{DB_PATH}", echo=False, future=True)
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# 選択肢（必要に応じて編集）
SHIFT_CHOICES = ["A", "B", "C"]
MACHINE_CHOICES = [2, 3, 4, 5, 6]
MODEL_CHOICES = [f"sample{i}" for i in range(1, 11)]

# --- モデル ---
class Entry(Base):
    __tablename__ = "entries"
    id = Column(Integer, primary_key=True, autoincrement=True)
    work_date = Column(Date, nullable=False)            # 日付
    shift = Column(String(1), nullable=False)           # 勤務帯 A/B/C
    machine_no = Column(Integer, nullable=False)        # 号機 2..6
    model_name = Column(String(50), nullable=False)     # 機種名

    # ▼ 実測値（モニタ値） — 全て必須扱い（アプリ側でバリデーション）
    inj_time = Column(Float, nullable=True)             # 射出時間(s, 0.001)
    metering_time = Column(Float, nullable=True)        # 計量時間(s, 0.01)
    vp_position = Column(Float, nullable=True)          # V-P位置(mm, 0.001)
    vp_pressure = Column(Float, nullable=True)          # V-P圧力(MPa, 0.1)
    min_cushion = Column(Float, nullable=True)          # 最小クッション(mm, 0.01)
    peak_pressure = Column(Float, nullable=True)        # ピーク圧(MPa, 0.1)
    cycle_time = Column(Float, nullable=True)           # サイクル時間(s, 0.01) ※前フィールド流用
    shot_count = Column(Integer, nullable=True)         # 現在ショット数（必須扱い）

    # ▼ 将来の「成形条件」用に残しておくフィールド（任意入力のまま）
    material = Column(String(50), nullable=True)        # 材料名
    melt_temp = Column(Float, nullable=True)            # 樹脂温度(℃)
    mold_temp = Column(Float, nullable=True)            # 金型温度(℃)
    inj_pressure = Column(Float, nullable=True)         # 射出圧(MPa)
    hold_pressure = Column(Float, nullable=True)        # 保圧(MPa)
    note = Column(Text, nullable=True)                  # メモ

def init_db():
    # 初回のみ作成（既存テーブルがある場合は列追加等は行わない）
    if not inspect(engine).has_table("entries"):
        Base.metadata.create_all(bind=engine)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        try:
            # フォーム値を取得
            work_date_str = request.form.get("work_date") or date.today().isoformat()
            work_date = datetime.strptime(work_date_str, "%Y-%m-%d").date()

            shift = request.form.get("shift")
            machine_no = int(request.form.get("machine_no"))
            model_name = request.form.get("model_name")

            def to_float(val):
                if val is None or val == "":
                    return None
                try:
                    # Windowsで小数点が「,」の入力に来ても置換
                    return float(str(val).replace(",", "."))
                except ValueError:
                    return None

            def to_int(val):
                if val is None or val == "":
                    return None
                try:
                    return int(val)
                except ValueError:
                    return None

            # --- 実測値（必須） ---
            inj_time = to_float(request.form.get("inj_time"))            # 0.001 s
            metering_time = to_float(request.form.get("metering_time"))  # 0.01 s
            vp_position = to_float(request.form.get("vp_position"))      # 0.001 mm
            vp_pressure = to_float(request.form.get("vp_pressure"))      # 0.1 MPa
            min_cushion = to_float(request.form.get("min_cushion"))      # 0.01 mm
            peak_pressure = to_float(request.form.get("peak_pressure"))  # 0.1 MPa
            cycle_time = to_float(request.form.get("cycle_time"))        # 0.01 s
            shot_count = to_int(request.form.get("shot_count"))          # int

            # --- 任意（成形条件の前座：今は保存のみ） ---
            material = request.form.get("material") or None
            melt_temp = to_float(request.form.get("melt_temp"))
            mold_temp = to_float(request.form.get("mold_temp"))
            inj_pressure = to_float(request.form.get("inj_pressure"))
            hold_pressure = to_float(request.form.get("hold_pressure"))
            note = request.form.get("note") or None

            # ざっくりバリデーション
            errors = []
            if shift not in SHIFT_CHOICES:
                errors.append("勤務帯の値が不正です。")
            if machine_no not in MACHINE_CHOICES:
                errors.append("号機の値が不正です。")
            if model_name not in MODEL_CHOICES:
                errors.append("機種名の値が不正です。")

            # 実測値は全て必須
            required_floats = {
                "射出時間": inj_time,
                "計量時間": metering_time,
                "V-P位置": vp_position,
                "V-P圧力": vp_pressure,
                "最小クッション": min_cushion,
                "ピーク圧": peak_pressure,
                "サイクル時間": cycle_time,
            }
            for label, v in required_floats.items():
                if v is None:
                    errors.append(f"{label}は必須です。")
                elif v < 0:
                    errors.append(f"{label}は0以上を入力してください。")

            if shot_count is None:
                errors.append("現在ショット数は必須です。")
            elif shot_count < 0:
                errors.append("現在ショット数は0以上を入力してください。")

            if errors:
                for e in errors:
                    flash(e, "error")
                return redirect(url_for("index"))

            # 保存
            session = SessionLocal()
            entry = Entry(
                work_date=work_date,
                shift=shift,
                machine_no=machine_no,
                model_name=model_name,
                inj_time=inj_time,
                metering_time=metering_time,
                vp_position=vp_position,
                vp_pressure=vp_pressure,
                min_cushion=min_cushion,
                peak_pressure=peak_pressure,
                cycle_time=cycle_time,
                shot_count=shot_count,
                material=material,
                melt_temp=melt_temp,
                mold_temp=mold_temp,
                inj_pressure=inj_pressure,
                hold_pressure=hold_pressure,
                note=note,
            )
            session.add(entry)
            session.commit()
            session.close()
            flash("保存しました。", "success")
            return redirect(url_for("index"))
        except Exception as e:
            flash(f"保存に失敗しました: {e}", "error")
            return redirect(url_for("index"))

    # GET
    today = date.today().isoformat()
    return render_template(
        "index.html",
        today=today,
        shift_choices=SHIFT_CHOICES,
        machine_choices=MACHINE_CHOICES,
        model_choices=MODEL_CHOICES,
    )

@app.route("/records")
def records():
    session = SessionLocal()
    rows = (
        session.query(Entry)
        .order_by(Entry.work_date.desc(), Entry.id.desc())
        .all()
    )
    session.close()
    return render_template("records.html", rows=rows)

@app.route("/export")
def export_csv():
    # 全件をCSV出力
    df = pd.read_sql_table("entries", con=engine)
    export_path = "production_log_export.csv"
    df.to_csv(export_path, index=False, encoding="utf-8-sig")
    return send_file(export_path, as_attachment=True)

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
