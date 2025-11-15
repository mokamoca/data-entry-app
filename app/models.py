from sqlalchemy import Column, Date, DateTime, Float, Integer, String, Text, func

from .database import Base


class Entry(Base):
    __tablename__ = "entries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    work_date = Column(Date, nullable=False)
    shift = Column(String(1), nullable=False)
    machine_no = Column(Integer, nullable=False, index=True)
    model_name = Column(String(50), nullable=False)

    inj_time = Column(Float, nullable=False)
    metering_time = Column(Float, nullable=False)
    vp_position = Column(Float, nullable=False)
    vp_pressure = Column(Float, nullable=False)
    min_cushion = Column(Float, nullable=False)
    peak_pressure = Column(Float, nullable=False)
    cycle_time = Column(Float, nullable=False)
    shot_count = Column(Integer, nullable=False)

    material = Column(String(50), nullable=True)
    melt_temp = Column(Float, nullable=True)
    mold_temp = Column(Float, nullable=True)
    inj_pressure = Column(Float, nullable=True)
    hold_pressure = Column(Float, nullable=True)
    note = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    def as_dict(self):
        return {
            "id": self.id,
            "work_date": self.work_date.isoformat() if self.work_date else "",
            "shift": self.shift,
            "machine_no": self.machine_no,
            "model_name": self.model_name,
            "inj_time": self.inj_time,
            "metering_time": self.metering_time,
            "vp_position": self.vp_position,
            "vp_pressure": self.vp_pressure,
            "min_cushion": self.min_cushion,
            "peak_pressure": self.peak_pressure,
            "cycle_time": self.cycle_time,
            "shot_count": self.shot_count,
            "material": self.material or "",
            "melt_temp": self.melt_temp if self.melt_temp is not None else "",
            "mold_temp": self.mold_temp if self.mold_temp is not None else "",
            "inj_pressure": self.inj_pressure if self.inj_pressure is not None else "",
            "hold_pressure": self.hold_pressure if self.hold_pressure is not None else "",
            "note": self.note or "",
            "created_at": self.created_at.isoformat() if self.created_at else "",
            "updated_at": self.updated_at.isoformat() if self.updated_at else "",
        }


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, autoincrement=True)
    category = Column(String(50), nullable=False)
    details = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
