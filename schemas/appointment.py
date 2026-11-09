from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field, field_validator

class AppointmentCreate(BaseModel):
    model_config = {"extra": "forbid"}
    patient_id: int = Field(gt=0)
    doctor_id: int = Field(gt=0)
    start_at: datetime
    duration_minutes: Literal[15, 30, 45, 60]
    reason: str | None = None
    @field_validator("start_at")
    @classmethod
    def check_start_at(cls, value):
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("Include a timezone in start_at")
        value = value.astimezone(timezone.utc)
        if value <= datetime.now(timezone.utc):
            raise ValueError("Appointment must start in the future")
        return value

class AppointmentUpdate(BaseModel):
    model_config = {"extra": "forbid"}
    doctor_id: int | None = Field(default=None, gt=0)
    start_at: datetime | None = None
    duration_minutes: Literal[15, 30, 45, 60] | None = None
    reason: str | None = None
    @field_validator("doctor_id", "start_at", "duration_minutes")
    @classmethod
    def reject_null(cls, value):
        if value is None:
            raise ValueError("This field cannot be null")
        return value
    @field_validator("start_at")
    @classmethod
    def check_start_at(cls, value):
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("Include a timezone in start_at")
        value = value.astimezone(timezone.utc)
        if value <= datetime.now(timezone.utc):
            raise ValueError("Appointment must start in the future")
        return value

class AppointmentResponse(BaseModel):
    id: int
    patient_id: int
    doctor_id: int
    start_at: datetime
    duration_minutes: Literal[15, 30, 45, 60]
    status: Literal["scheduled", "completed", "cancelled"]
    reason: str | None = None