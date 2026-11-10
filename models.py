from sqlalchemy import Boolean, Date, Float, ForeignKey, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from database import Base
from datetime import date,datetime

class Specialization(Base):
    __tablename__ = "specializations"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100),nullable=False)
    description: Mapped[str | None] = mapped_column(nullable=True)

class Doctor(Base):
    __tablename__ = "doctors"
    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    specialization_id: Mapped[int] = mapped_column(ForeignKey("specializations.id"),nullable=False)
    experience_years: Mapped[int] = mapped_column(nullable=False)
    consultation_price: Mapped[float] = mapped_column(Float,nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean,default=True,nullable=False)

class Patient(Base):
    __tablename__ = "patients"
    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str | None] = mapped_column(String, nullable=True)
    birth_date: Mapped[date | None] = mapped_column(Date, nullable=True)

class Appointment(Base):
    __tablename__ = "appointments"
    id: Mapped[int] = mapped_column(primary_key=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"),nullable=False)
    doctor_id: Mapped[int] = mapped_column(ForeignKey("doctors.id"),nullable=False)
    start_at: Mapped[datetime] = mapped_column(DateTime,nullable=False)
    duration_minutes: Mapped[int] = mapped_column(nullable=False)
    status: Mapped[str] = mapped_column(String(20),default="scheduled",nullable=False)
    reason: Mapped[str | None] = mapped_column(nullable=True)
