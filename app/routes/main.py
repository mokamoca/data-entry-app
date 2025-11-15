from __future__ import annotations

import csv
from datetime import datetime, time
from io import StringIO
from typing import Iterable, List

from flask import (
    Blueprint,
    Response,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    session,
    stream_with_context,
    url_for,
)

from ..database import create_all, session_scope
from ..forms import EntryForm, RecordsFilterForm
from ..models import Entry

bp = Blueprint("main", __name__)


@bp.before_app_request
def ensure_tables():
    if not current_app.config.setdefault("_tables_ready", False):
        create_all()
        current_app.config["_tables_ready"] = True


def _get_choices():
    cfg = current_app.config
    shift_choices = cfg.get("SHIFT_CHOICES") or ["A", "B", "C"]
    machine_choices = cfg.get("MACHINE_CHOICES") or [2, 3, 4, 5, 6]
    model_choices = cfg.get("MODEL_CHOICES") or [f"sample{i}" for i in range(1, 11)]
    return shift_choices, machine_choices, model_choices


def _resolve_machine(machine_choices: Iterable[int]):
    q_machine = request.args.get("machine", type=int)
    if q_machine in machine_choices:
        session["machine_no"] = q_machine
        return q_machine
    stored = session.get("machine_no")
    if stored in machine_choices:
        return stored
    return None


def _guess_shift(shift_choices: List[str]):
    now = datetime.now().time()
    # Simple heuristic: day (6-14) -> first, evening (14-22) -> second, else -> last
    if len(shift_choices) < 3:
        return shift_choices[0]
    if time(6, 0) <= now < time(14, 0):
        return shift_choices[0]
    if time(14, 0) <= now < time(22, 0):
        return shift_choices[1]
    return shift_choices[2]


@bp.route("/", methods=["GET", "POST"])
def index():
    shift_choices, machine_choices, model_choices = _get_choices()
    form = EntryForm(
        machine_choices=machine_choices,
        model_choices=model_choices,
        shift_choices=shift_choices,
    )

    preselected_machine = _resolve_machine(machine_choices)
    if preselected_machine is None:
        return redirect(url_for("main.select_machine"))

    if request.method == "GET":
        form.machine_no.data = str(preselected_machine)
        if not form.shift.data:
            form.shift.data = _guess_shift(shift_choices)

    if form.validate_on_submit():
        with session_scope() as db_session:
            entry = Entry(
                work_date=form.work_date.data,
                shift=form.shift.data,
                machine_no=int(form.machine_no.data),
                model_name=form.model_name.data,
                inj_time=float(form.inj_time.data),
                metering_time=float(form.metering_time.data),
                vp_position=float(form.vp_position.data),
                vp_pressure=float(form.vp_pressure.data),
                min_cushion=float(form.min_cushion.data),
                peak_pressure=float(form.peak_pressure.data),
                cycle_time=float(form.cycle_time.data),
                shot_count=form.shot_count.data,
                material=form.material.data or None,
                melt_temp=float(form.melt_temp.data) if form.melt_temp.data is not None else None,
                mold_temp=float(form.mold_temp.data) if form.mold_temp.data is not None else None,
                inj_pressure=float(form.inj_pressure.data) if form.inj_pressure.data is not None else None,
                hold_pressure=float(form.hold_pressure.data) if form.hold_pressure.data is not None else None,
                note=form.note.data or None,
            )
            db_session.add(entry)
        flash("保存しました。", "success")
        return redirect(url_for("main.index", machine=form.machine_no.data))

    return render_template(
        "index.html",
        form=form,
        shift_choices=shift_choices,
        machine_choices=machine_choices,
        model_choices=model_choices,
        selected_machine=preselected_machine,
    )


@bp.route("/select-machine")
def select_machine():
    _, machine_choices, _ = _get_choices()
    return render_template("select_machine.html", machine_choices=machine_choices)


def _apply_filters(query, form):
    if form.machine_no.data:
        query = query.filter(Entry.machine_no == int(form.machine_no.data))
    if form.shift.data:
        query = query.filter(Entry.shift == form.shift.data)
    if form.date_from.data:
        query = query.filter(Entry.work_date >= form.date_from.data)
    if form.date_to.data:
        query = query.filter(Entry.work_date <= form.date_to.data)
    return query


@bp.route("/records")
def records():
    shift_choices, machine_choices, _ = _get_choices()
    form = RecordsFilterForm(
        machine_choices=machine_choices,
        shift_choices=shift_choices,
        formdata=request.args,
    )
    form.validate()

    with session_scope() as db_session:
        query = db_session.query(Entry).order_by(Entry.work_date.desc(), Entry.id.desc())
        query = _apply_filters(query, form)
        rows = query.limit(current_app.config.get("RECORDS_LIMIT", 250)).all()

    limit = current_app.config.get("RECORDS_LIMIT", 250)
    return render_template("records.html", rows=rows, form=form, records_limit=limit)


def _stream_csv(rows, filename):
    header = [
        "id",
        "work_date",
        "shift",
        "machine_no",
        "model_name",
        "inj_time",
        "metering_time",
        "vp_position",
        "vp_pressure",
        "min_cushion",
        "peak_pressure",
        "cycle_time",
        "shot_count",
        "material",
        "melt_temp",
        "mold_temp",
        "inj_pressure",
        "hold_pressure",
        "note",
        "created_at",
        "updated_at",
    ]

    def generate():
        buffer = StringIO()
        writer = csv.writer(buffer)
        writer.writerow(header)
        yield buffer.getvalue()
        buffer.seek(0)
        buffer.truncate(0)

        for row in rows:
            data = row.as_dict()
            writer.writerow([data.get(column, "") for column in header])
            yield buffer.getvalue()
            buffer.seek(0)
            buffer.truncate(0)

    response = Response(stream_with_context(generate()), mimetype="text/csv; charset=utf-8")
    response.headers["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


@bp.route("/export")
def export():
    shift_choices, machine_choices, _ = _get_choices()
    form = RecordsFilterForm(
        machine_choices=machine_choices,
        shift_choices=shift_choices,
        formdata=request.args,
    )
    form.validate()
    with session_scope() as db_session:
        query = db_session.query(Entry).order_by(Entry.work_date.desc(), Entry.id.desc())
        query = _apply_filters(query, form)
        rows = query.all()
    filename = current_app.config.get("EXPORT_FILENAME", "production-log-export.csv")
    return _stream_csv(rows, filename)


@bp.route("/ping")
def ping():
    return "pong"
