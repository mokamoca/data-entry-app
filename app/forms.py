from datetime import date
from typing import Iterable, Sequence

from flask_wtf import FlaskForm
from wtforms import (
    DateField,
    DecimalField,
    IntegerField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms import validators

REQUIRED_MESSAGE = "この項目は必須です。"


def _build_choice_tuples(values: Sequence, include_blank=False):
    choices = []
    if include_blank:
        choices.append(("", "すべて"))
    for value in values:
        choices.append((str(value), str(value)))
    return choices


class EntryForm(FlaskForm):
    work_date = DateField(
        "日付",
        default=date.today,
        validators=[validators.DataRequired(message=REQUIRED_MESSAGE)],
        render_kw={"inputmode": "numeric"},
    )
    shift = SelectField("勤務帯", validators=[validators.DataRequired(message=REQUIRED_MESSAGE)])
    machine_no = SelectField("号機", validators=[validators.DataRequired(message=REQUIRED_MESSAGE)])
    model_name = SelectField("機種名", validators=[validators.DataRequired(message=REQUIRED_MESSAGE)])
    environment_temp = DecimalField(
        "環境温度 (℃)",
        places=1,
        rounding=None,
        validators=[
            validators.InputRequired(message=REQUIRED_MESSAGE),
            validators.NumberRange(min=-50, max=80),
        ],
        render_kw={"step": "0.1", "inputmode": "decimal"},
    )
    environment_humidity = DecimalField(
        "環境湿度 (%)",
        places=1,
        rounding=None,
        validators=[
            validators.InputRequired(message=REQUIRED_MESSAGE),
            validators.NumberRange(min=0, max=100),
        ],
        render_kw={"step": "0.1", "inputmode": "decimal"},
    )
    material_lot = StringField(
        "材料ロット",
        validators=[validators.DataRequired(message=REQUIRED_MESSAGE), validators.Length(max=120)],
        render_kw={"placeholder": "例: LOT-20251115-A"},
    )
    inj_time = DecimalField(
        "射出時間 (s)",
        places=3,
        rounding=None,
        validators=[
            validators.InputRequired(message=REQUIRED_MESSAGE),
            validators.NumberRange(min=0),
        ],
        render_kw={"step": "0.001", "placeholder": "0.350", "inputmode": "decimal"},
    )
    metering_time = DecimalField(
        "計量時間 (s)",
        places=2,
        rounding=None,
        validators=[
            validators.InputRequired(message=REQUIRED_MESSAGE),
            validators.NumberRange(min=0),
        ],
        render_kw={"step": "0.01", "placeholder": "1.25", "inputmode": "decimal"},
    )
    vp_position = DecimalField(
        "V-P位置 (mm)",
        places=3,
        rounding=None,
        validators=[
            validators.InputRequired(message=REQUIRED_MESSAGE),
            validators.NumberRange(min=0),
        ],
        render_kw={"step": "0.001", "placeholder": "12.345", "inputmode": "decimal"},
    )
    vp_pressure = DecimalField(
        "V-P圧力 (MPa)",
        places=1,
        rounding=None,
        validators=[
            validators.InputRequired(message=REQUIRED_MESSAGE),
            validators.NumberRange(min=0),
        ],
        render_kw={"step": "0.1", "placeholder": "85.4", "inputmode": "decimal"},
    )
    min_cushion = DecimalField(
        "最小クッション (mm)",
        places=2,
        rounding=None,
        validators=[
            validators.InputRequired(message=REQUIRED_MESSAGE),
            validators.NumberRange(min=0),
        ],
        render_kw={"step": "0.01", "placeholder": "0.30", "inputmode": "decimal"},
    )
    peak_pressure = DecimalField(
        "ピーク圧 (MPa)",
        places=1,
        rounding=None,
        validators=[
            validators.InputRequired(message=REQUIRED_MESSAGE),
            validators.NumberRange(min=0),
        ],
        render_kw={"step": "0.1", "placeholder": "120.5", "inputmode": "decimal"},
    )
    cycle_time = DecimalField(
        "サイクル時間 (s)",
        places=2,
        rounding=None,
        validators=[
            validators.InputRequired(message=REQUIRED_MESSAGE),
            validators.NumberRange(min=0),
        ],
        render_kw={"step": "0.01", "placeholder": "32.50", "inputmode": "decimal"},
    )
    shot_count = IntegerField(
        "現在ショット数",
        validators=[
            validators.InputRequired(message=REQUIRED_MESSAGE),
            validators.NumberRange(min=0),
        ],
        render_kw={"step": "1", "placeholder": "50", "inputmode": "numeric"},
    )
    melt_temp = DecimalField(
        "樹脂温度 (℃)",
        places=1,
        rounding=None,
        validators=[validators.Optional(), validators.NumberRange(min=0)],
        render_kw={"step": "0.1", "inputmode": "decimal"},
    )
    mold_temp = DecimalField(
        "金型温度 (℃)",
        places=1,
        rounding=None,
        validators=[validators.Optional(), validators.NumberRange(min=0)],
        render_kw={"step": "0.1", "inputmode": "decimal"},
    )
    inj_pressure = DecimalField(
        "射出圧 (MPa)",
        places=1,
        rounding=None,
        validators=[validators.Optional(), validators.NumberRange(min=0)],
        render_kw={"step": "0.1", "inputmode": "decimal"},
    )
    hold_pressure = DecimalField(
        "保圧 (MPa)",
        places=1,
        rounding=None,
        validators=[validators.Optional(), validators.NumberRange(min=0)],
        render_kw={"step": "0.1", "inputmode": "decimal"},
    )
    note = TextAreaField(
        "メモ",
        validators=[validators.Optional(), validators.Length(max=500)],
        render_kw={"placeholder": "特記事項や異常内容を記載"},
    )

    submit = SubmitField("保存")

    def __init__(self, *, machine_choices: Iterable, model_choices: Iterable, shift_choices: Iterable, **kwargs):
        super().__init__(**kwargs)
        self.machine_no.choices = _build_choice_tuples(machine_choices)
        self.model_name.choices = _build_choice_tuples(model_choices)
        self.shift.choices = _build_choice_tuples(shift_choices)


class RecordsFilterForm(FlaskForm):
    machine_no = SelectField("号機", validators=[validators.Optional()])
    shift = SelectField("勤務帯", validators=[validators.Optional()])
    date_from = DateField(
        "開始日",
        validators=[validators.Optional()],
        render_kw={"type": "date"},
    )
    date_to = DateField(
        "終了日",
        validators=[validators.Optional()],
        render_kw={"type": "date"},
    )
    submit = SubmitField("絞り込む")

    def __init__(self, *, machine_choices: Iterable, shift_choices: Iterable, **kwargs):
        kwargs.setdefault("meta", {"csrf": False})
        super().__init__(**kwargs)
        self.machine_no.choices = _build_choice_tuples(machine_choices, include_blank=True)
        self.shift.choices = _build_choice_tuples(shift_choices, include_blank=True)


class FeedbackForm(FlaskForm):
    category = SelectField("カテゴリ", validators=[validators.DataRequired(message=REQUIRED_MESSAGE)])
    details = TextAreaField(
        "内容",
        validators=[validators.DataRequired(message=REQUIRED_MESSAGE), validators.Length(max=1000)],
        render_kw={"rows": 6, "placeholder": "気になる点・困りごと・改善案など"},
    )
    submit = SubmitField("フィードバックを送信")

    def __init__(self, *, category_choices: Iterable, **kwargs):
        super().__init__(**kwargs)
        self.category.choices = list(category_choices)
