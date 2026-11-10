from fastapi import APIRouter, HTTPException
from data import storage
from schemas.doctor import DoctorCreate, DoctorResponse, DoctorReplace, DoctorUpdate
from fastapi import Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Doctor, Specialization, Appointment
from schemas.appointment import AppointmentResponse

router = APIRouter(prefix="/doctors", tags=["Doctors"])

@router.post("", response_model=DoctorResponse, status_code=201)
def create_doctor(
    data: DoctorCreate,
    db: Session = Depends(get_db),
):
    specialization = db.get(Specialization, data.specialization_id)
    if specialization is None:
        raise HTTPException(status_code=404,detail="Specialization not found",)
    doctor = Doctor(
        full_name=data.full_name,
        specialization_id=data.specialization_id,
        experience_years=data.experience_years,
        consultation_price=data.consultation_price,
        is_active=data.is_active,
    )
    db.add(doctor)
    db.commit()
    db.refresh(doctor)
    return doctor

@router.get("", response_model=list[DoctorResponse])
def get_doctors(
    db: Session = Depends(get_db),
    specialization_id: int | None = None,
    is_active: bool | None = None,
    min_experience: int | None = None,
    max_price: float | None = None,
    search: str | None = None
):
    query = db.query(Doctor)
    if specialization_id is not None:
        query = query.filter(Doctor.specialization_id == specialization_id)
    if is_active is not None:
        query = query.filter(Doctor.is_active == is_active)
    if min_experience is not None:
        query = query.filter(Doctor.experience_years >= min_experience)
    if max_price is not None:
        query = query.filter(Doctor.consultation_price <= max_price)
    doctors = query.all()
    if search is not None:
        result = []
        for doctor in doctors:
            if search.lower() in doctor.full_name.lower():
                result.append(doctor)
        return result
    return doctors

@router.get("/{doctor_id}", response_model=DoctorResponse)
def get_doctor(doctor_id: int,db: Session = Depends(get_db)):
    doctor = db.get(Doctor, doctor_id)
    if doctor is None:
        raise HTTPException(status_code=404,detail="Doctor not found")
    return doctor

@router.put("/{doctor_id}", response_model=DoctorResponse)
def replace_doctor(doctor_id: int,data: DoctorReplace,db: Session = Depends(get_db)):
    doctor = db.get(Doctor, doctor_id)
    if doctor is None:
        raise HTTPException(status_code=404,detail="Doctor not found")
    specialization = db.get(Specialization, data.specialization_id)
    if specialization is None:
        raise HTTPException(status_code=404,detail="Specialization not found")
    doctor.full_name = data.full_name
    doctor.specialization_id = data.specialization_id
    doctor.experience_years = data.experience_years
    doctor.consultation_price = data.consultation_price
    doctor.is_active = data.is_active
    db.commit()
    db.refresh(doctor)
    return doctor

@router.patch("/{doctor_id}", response_model=DoctorResponse)
def update_doctor(doctor_id: int,data: DoctorUpdate,db: Session = Depends(get_db)):
    doctor = db.get(Doctor, doctor_id)
    if doctor is None:
        raise HTTPException(status_code=404,detail="Doctor not found")
    changes = data.model_dump(exclude_unset=True)
    if "specialization_id" in changes:
        specialization = db.get(Specialization,changes["specialization_id"]) 
        if specialization is None:
            raise HTTPException(status_code=404,detail="Specialization not found")
        doctor.specialization_id = changes["specialization_id"]
    if "full_name" in changes:
        doctor.full_name = changes["full_name"]
    if "experience_years" in changes:
        doctor.experience_years = changes["experience_years"]
    if "consultation_price" in changes:
        doctor.consultation_price = changes["consultation_price"]
    if "is_active" in changes:
        doctor.is_active = changes["is_active"]
    db.commit()
    db.refresh(doctor)
    return doctor

@router.delete("/{doctor_id}", status_code=204)
def delete_doctor(doctor_id: int,db: Session = Depends(get_db)):
    doctor = db.get(Doctor, doctor_id)
    if doctor is None:
        raise HTTPException(status_code=404,detail="Doctor not found")
    for appointment in storage.appointments:
        if appointment["doctor_id"] == doctor_id:
            raise HTTPException(status_code=409,detail="This doctor has appointments")
    db.delete(doctor)
    db.commit()

@router.get("/{doctor_id}/appointments",response_model=list[AppointmentResponse])
def get_doctor_appointments(doctor_id: int,db: Session = Depends(get_db)):
    doctor = db.get(Doctor, doctor_id)
    if doctor is None:
        raise HTTPException(status_code=404,detail="Doctor not found")
    appointments = db.query(Appointment).filter(Appointment.doctor_id == doctor_id).all()
    return appointments
