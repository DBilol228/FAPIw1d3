from fastapi import APIRouter, HTTPException
from data import storage
from schemas.patient import PatientCreate, PatientResponse, PatientReplace, PatientUpdate
from fastapi import Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Patient, Appointment
from schemas.appointment import AppointmentResponse

router = APIRouter(prefix="/patients", tags=["Patients"])

@router.post("", response_model=PatientResponse, status_code=201)
def create_patient(data: PatientCreate,db: Session = Depends(get_db)):
    patient = Patient(full_name=data.full_name,phone=data.phone,email=data.email,birth_date=data.birth_date)
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient

@router.get("", response_model=list[PatientResponse])
def get_patients(db: Session = Depends(get_db),search: str | None = None,):
    patients = db.query(Patient).all()
    if search is not None:
        result = []
        for patient in patients:
            if search.lower() in patient.full_name.lower():
                result.append(patient)
        return result
    return patients

@router.get("/{patient_id}", response_model=PatientResponse)
def get_patient(patient_id: int,db: Session = Depends(get_db)):
    patient = db.get(Patient, patient_id)
    if patient is None:
        raise HTTPException(status_code=404,detail="Patient not found")
    return patient

@router.put("/{patient_id}", response_model=PatientResponse)
def replace_patient(patient_id: int,data: PatientReplace,db: Session = Depends(get_db)):
    patient = db.get(Patient, patient_id)
    if patient is None:
        raise HTTPException(status_code=404,detail="Patient not found")
    patient.full_name = data.full_name
    patient.phone = data.phone
    patient.email = data.email
    patient.birth_date = data.birth_date
    db.commit()
    db.refresh(patient)
    return patient

@router.patch("/{patient_id}", response_model=PatientResponse)
def update_patient(patient_id: int,data: PatientUpdate,db: Session = Depends(get_db)):
    patient = db.get(Patient, patient_id)
    if patient is None:
        raise HTTPException(status_code=404,detail="Patient not found")
    changes = data.model_dump(exclude_unset=True)
    if "full_name" in changes:
        patient.full_name = changes["full_name"]
    if "phone" in changes:
        patient.phone = changes["phone"]
    if "email" in changes:
        patient.email = changes["email"]
    if "birth_date" in changes:
        patient.birth_date = changes["birth_date"]
    db.commit()
    db.refresh(patient)
    return patient

@router.delete("/{patient_id}", status_code=204)
def delete_patient(patient_id: int,db: Session = Depends(get_db)):
    patient = db.get(Patient, patient_id)
    if patient is None:
        raise HTTPException(status_code=404,detail="Patient not found")
    for appointment in storage.appointments:
        if appointment["patient_id"] == patient_id:
            raise HTTPException(status_code=409,detail="This patient has appointments")
    db.delete(patient)
    db.commit()

@router.get("/{patient_id}/appointments",response_model=list[AppointmentResponse])
def get_patient_appointments(patient_id: int,db: Session = Depends(get_db)):
    patient = db.get(Patient, patient_id)
    if patient is None:
        raise HTTPException(status_code=404,detail="Patient not found")
    appointments = db.query(Appointment).filter(Appointment.patient_id == patient_id).all()
    return appointments
