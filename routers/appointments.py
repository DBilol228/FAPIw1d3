from datetime import timedelta,date
from fastapi import APIRouter, HTTPException
from data import storage
from typing import Literal
from schemas.appointment import AppointmentCreate, AppointmentResponse, AppointmentUpdate
from datetime import datetime, timedelta, timezone
from fastapi import Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from database import get_db
from models import Appointment, Doctor, Patient
from datetime import date
from fastapi import Query

router = APIRouter(prefix="/appointments", tags=["Appointments"])

@router.post("", response_model=AppointmentResponse, status_code=201)
def create_appointment(data: AppointmentCreate,db: Session = Depends(get_db)):
    db.execute(text("BEGIN IMMEDIATE"))
    patient = db.get(Patient, data.patient_id)
    if patient is None:
        raise HTTPException(status_code=404,detail="Patient not found")
    doctor = db.get(Doctor, data.doctor_id)
    if doctor is None:
        raise HTTPException(status_code=404,detail="Doctor not found")
    if doctor.is_active == False:
        raise HTTPException(status_code=409,detail="Doctor is not active")
    new_start = data.start_at.astimezone(timezone.utc)
    new_start = new_start.replace(tzinfo=None)
    if new_start <= datetime.now(timezone.utc).replace(tzinfo=None):
        raise HTTPException(status_code=422,detail="Appointment must start in the future")
    new_end = new_start + timedelta(minutes=data.duration_minutes)
    appointments = db.query(Appointment).filter(
        Appointment.doctor_id == data.doctor_id,
        Appointment.status == "scheduled").all()
    for appointment in appointments:
        existing_start = appointment.start_at
        existing_end = existing_start + timedelta(
            minutes=appointment.duration_minutes
        )
        if new_start < existing_end and existing_start < new_end:
            raise HTTPException(status_code=409,detail="Doctor already has an appointment at this time")
    appointment = Appointment(
        patient_id=data.patient_id,
        doctor_id=data.doctor_id,
        start_at=new_start,
        duration_minutes=data.duration_minutes,
        status="scheduled",
        reason=data.reason
    )
    db.add(appointment)
    db.commit()
    db.refresh(appointment)
    return appointment

@router.get("", response_model=list[AppointmentResponse])
def get_appointments(
    db: Session = Depends(get_db),
    doctor_id: int | None = None,
    patient_id: int | None = None,
    status: Literal["scheduled", "completed", "cancelled"] | None = None,
    appointment_date: date | None = Query(default=None, alias="date")
):
    query = db.query(Appointment)
    if doctor_id is not None:
        query = query.filter(Appointment.doctor_id == doctor_id)
    if patient_id is not None:
        query = query.filter(Appointment.patient_id == patient_id)
    if status is not None:
        query = query.filter(Appointment.status == status)
    appointments = query.all()
    if appointment_date is not None:
        result = []
        for appointment in appointments:
            if appointment.start_at.date() == appointment_date:
                result.append(appointment)
        return result
    return appointments

@router.get("/{appointment_id}", response_model=AppointmentResponse)
def get_appointment(appointment_id: int,db: Session = Depends(get_db)):
    appointment = db.get(Appointment, appointment_id)
    if appointment is None:
        raise HTTPException(status_code=404,detail="Appointment not found")
    return appointment

@router.patch("/{appointment_id}", response_model=AppointmentResponse)
def update_appointment(
    appointment_id: int,
    data: AppointmentUpdate,
    db: Session = Depends(get_db)
):
    db.execute(text("BEGIN IMMEDIATE"))
    appointment = db.get(Appointment, appointment_id)
    if appointment is None:
        raise HTTPException(status_code=404,detail="Appointment not found")
    if appointment.status != "scheduled":
        raise HTTPException(status_code=409,detail="Only scheduled appointments can be changed")
    changes = data.model_dump(exclude_unset=True)
    doctor_id = appointment.doctor_id
    start_at = appointment.start_at
    duration_minutes = appointment.duraion_minutes
    if "doctor_id" in changes:
        doctor_id = changes["doctor_id"]
    if "start_at" in changes:
        start_at = changes["start_at"].astimezone(timezone.utc)
        start_at = start_at.replace(tzinfo=None)
    if "duration_minutes" in changes:
        duration_minutes = changes["duration_minutes"]
    doctor = db.get(Doctor, doctor_id)
    if doctor is None:
        raise HTTPException(status_code=404,detail="Doctor not found")
    if doctor.is_active == False:
        raise HTTPException(status_code=409,detail="Doctor is not active")
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    if start_at <= now:
        raise HTTPException(status_code=422,detail="Appointment must start in the future")
    new_end = start_at + timedelta(minutes=duration_minutes)
    appointments = db.query(Appointment).filter(
        Appointment.doctor_id == doctor_id,
        Appointment.status == "scheduled",
        Appointment.id != appointment_id).all()
    for item in appointments:
        existing_start = item.start_at
        existing_end = existing_start + timedelta(
            minutes=item.duration_minutes
        )
        if start_at < existing_end and existing_start < new_end:
            raise HTTPException(status_code=409,detail="Doctor already has an appointment at this time")
    appointment.doctor_id = doctor_id
    appointment.start_at = start_at
    appointment.duration_minutes = duration_minutes
    if "reason" in changes:
        appointment.reason = changes["reason"]
    db.commit()
    db.refresh(appointment)
    return appointment

@router.patch("/{appointment_id}/cancel",response_model=AppointmentResponse)
def cancel_appointment(appointment_id: int,db: Session = Depends(get_db),):
    db.execute(text("BEGIN IMMEDIATE"))
    appointment = db.get(Appointment, appointment_id)
    if appointment is None:
        raise HTTPException(status_code=404,detail="Appointment not found")
    if appointment.status != "scheduled":
        raise HTTPException(status_code=409,detail="Only scheduled appointments can be cancelled")
    appointment.status = "cancelled"
    db.commit()
    db.refresh(appointment)
    return appointment

@router.patch("/{appointment_id}/complete",response_model=AppointmentResponse)
def complete_appointment(appointment_id: int,db: Session = Depends(get_db)):
    db.execute(text("BEGIN IMMEDIATE"))
    appointment = db.get(Appointment, appointment_id)
    if appointment is None:
        raise HTTPException(status_code=404,detail="Appointment not found")
    if appointment.status != "scheduled":
        raise HTTPException(status_code=409,detail="Only scheduled appointments can be completed")
    end_at = appointment.start_at + timedelta(minutes=appointment.duration_minutes)
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    if now < end_at:
        raise HTTPException(status_code=409,detail="Appointment has not ended yet")
    appointment.status = "completed"
    db.commit()
    db.refresh(appointment)
    return appointment
