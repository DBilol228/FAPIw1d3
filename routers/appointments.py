from datetime import timedelta,date
from fastapi import APIRouter, HTTPException
from data import storage
from typing import Literal
from schemas.appointment import AppointmentCreate, AppointmentResponse, AppointmentUpdate

router = APIRouter(prefix="/appointments", tags=["Appointments"])

@router.post("", response_model=AppointmentResponse, status_code=201)
async def create_appointment(data: AppointmentCreate):
    patient_exists = False
    for patient in storage.patients:
        if patient["id"] == data.patient_id:
            patient_exists = True
            break
    if patient_exists == False:
        raise HTTPException(status_code=404,detail="Patient not found",)
    doctor = None
    for item in storage.doctors:
        if item["id"] == data.doctor_id:
            doctor = item
            break
    if doctor is None:
        raise HTTPException(status_code=404,detail="Doctor not found",)
    if doctor["is_active"] == False:
        raise HTTPException(status_code=409,detail="Doctor is not active",)
    new_start = data.start_at
    new_end = new_start + timedelta(minutes=data.duration_minutes)
    for appointment in storage.appointments:
        if appointment["doctor_id"] != data.doctor_id:
            continue
        if appointment["status"] != "scheduled":
            continue
        existing_start = appointment["start_at"]
        existing_end = existing_start + timedelta(
            minutes=appointment["duration_minutes"]
        )
        if new_start < existing_end and existing_start < new_end:
            raise HTTPException(status_code=409,detail="Doctor already has an appointment at this time",)
    appointment = data.model_dump()
    appointment["id"] = storage.next_appointment_id
    appointment["status"] = "scheduled"
    storage.appointments.append(appointment)
    storage.next_appointment_id += 1
    return appointment

@router.get("", response_model=list[AppointmentResponse])
async def get_appointments(
    doctor_id: int | None = None,
    patient_id: int | None = None,
    status: Literal["scheduled", "completed", "cancelled"] | None = None,
    date: date | None = None,
):
    result = []
    for appointment in storage.appointments:
        if doctor_id is not None:
            if appointment["doctor_id"] != doctor_id:
                continue
        if patient_id is not None:
            if appointment["patient_id"] != patient_id:
                continue
        if status is not None:
            if appointment["status"] != status:
                continue
        if date is not None:
            if appointment["start_at"].date() != date:
                continue
        result.append(appointment)
    return result

@router.get("/{appointment_id}", response_model=AppointmentResponse)
async def get_appointment(appointment_id: int):
    for appointment in storage.appointments:
        if appointment["id"] == appointment_id:
            return appointment
    raise HTTPException(status_code=404,detail="Appointment not found")