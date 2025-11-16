from sqlalchemy import Column, Date, DateTime, Float, Integer, String, Text, func

from .database import Base


class Entry(Base):
    __tablename__ = "entries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    work_date = Column(Date, nullable=False)
    shift = Column(String(1), nullable=False)
    machine_no = Column(Integer, nullable=False, index=True)
    model_name = Column(String(50), nullable=False)
    environment_temp = Column(Float, nullable=True)
    environment_humidity = Column(Float, nullable=True)
    material_lot = Column(String(120), nullable=True)

    inj_time = Column(Float, nullable=False)
    metering_time = Column(Float, nullable=False)
    vp_position = Column(Float, nullable=False)
    vp_pressure = Column(Float, nullable=False)
    min_cushion = Column(Float, nullable=False)
    peak_pressure = Column(Float, nullable=False)
    cycle_time = Column(Float, nullable=False)
    shot_count = Column(Integer, nullable=False)
    mold_temp_fixed = Column(Float, nullable=True)
    mold_temp_moving = Column(Float, nullable=True)
    nozzle_temp = Column(Float, nullable=True)
    cylinder_front_temp = Column(Float, nullable=True)
    cylinder_mid1_temp = Column(Float, nullable=True)
    cylinder_mid2_temp = Column(Float, nullable=True)
    cylinder_rear_temp = Column(Float, nullable=True)

    injection_speed_1 = Column(Float, nullable=True)
    injection_speed_2 = Column(Float, nullable=True)
    injection_switch_position = Column(Float, nullable=True)
    injection_pressure_setting = Column(Float, nullable=True)
    injection_time_setting = Column(Float, nullable=True)

    hold_pressure_1 = Column(Float, nullable=True)
    hold_pressure_2 = Column(Float, nullable=True)
    hold_time_1 = Column(Float, nullable=True)
    hold_time_2 = Column(Float, nullable=True)
    hold_pressure_total = Column(Float, nullable=True)

    metering_position = Column(Float, nullable=True)
    back_pressure = Column(Float, nullable=True)
    screw_rotation_speed = Column(Float, nullable=True)
    cooling_time = Column(Float, nullable=True)

    change_note = Column(Text, nullable=True)

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
            "environment_temp": self.environment_temp if self.environment_temp is not None else "",
            "environment_humidity": self.environment_humidity if self.environment_humidity is not None else "",
            "material_lot": self.material_lot or "",
            "inj_time": self.inj_time,
            "metering_time": self.metering_time,
            "vp_position": self.vp_position,
            "vp_pressure": self.vp_pressure,
            "min_cushion": self.min_cushion,
            "peak_pressure": self.peak_pressure,
            "cycle_time": self.cycle_time,
            "shot_count": self.shot_count,
            "mold_temp_fixed": self.mold_temp_fixed if self.mold_temp_fixed is not None else "",
            "mold_temp_moving": self.mold_temp_moving if self.mold_temp_moving is not None else "",
            "nozzle_temp": self.nozzle_temp if self.nozzle_temp is not None else "",
            "cylinder_front_temp": self.cylinder_front_temp if self.cylinder_front_temp is not None else "",
            "cylinder_mid1_temp": self.cylinder_mid1_temp if self.cylinder_mid1_temp is not None else "",
            "cylinder_mid2_temp": self.cylinder_mid2_temp if self.cylinder_mid2_temp is not None else "",
            "cylinder_rear_temp": self.cylinder_rear_temp if self.cylinder_rear_temp is not None else "",
            "injection_speed_1": self.injection_speed_1 if self.injection_speed_1 is not None else "",
            "injection_speed_2": self.injection_speed_2 if self.injection_speed_2 is not None else "",
            "injection_switch_position": self.injection_switch_position if self.injection_switch_position is not None else "",
            "injection_pressure_setting": self.injection_pressure_setting if self.injection_pressure_setting is not None else "",
            "injection_time_setting": self.injection_time_setting if self.injection_time_setting is not None else "",
            "hold_pressure_1": self.hold_pressure_1 if self.hold_pressure_1 is not None else "",
            "hold_pressure_2": self.hold_pressure_2 if self.hold_pressure_2 is not None else "",
            "hold_time_1": self.hold_time_1 if self.hold_time_1 is not None else "",
            "hold_time_2": self.hold_time_2 if self.hold_time_2 is not None else "",
            "hold_pressure_total": self.hold_pressure_total if self.hold_pressure_total is not None else "",
            "metering_position": self.metering_position if self.metering_position is not None else "",
            "back_pressure": self.back_pressure if self.back_pressure is not None else "",
            "screw_rotation_speed": self.screw_rotation_speed if self.screw_rotation_speed is not None else "",
            "cooling_time": self.cooling_time if self.cooling_time is not None else "",
            "change_note": self.change_note or "",
            "created_at": self.created_at.isoformat() if self.created_at else "",
            "updated_at": self.updated_at.isoformat() if self.updated_at else "",
        }


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, autoincrement=True)
    category = Column(String(50), nullable=False)
    details = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
