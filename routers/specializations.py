from fastapi import APIRouter, HTTPException, status
from data import storage
from schemas.specialization import SpecializationCreate, SpecializationResponse, SpecializationUpdate
from fastapi import Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Specialization, Doctor

router = APIRouter(prefix="/specializations",tags=["Specializations"])

@router.post("", response_model=SpecializationResponse, status_code=201)
def create_specialization(data: SpecializationCreate,db: Session = Depends(get_db),):
    specializations = db.query(Specialization).all()
    for specialization in specializations:
        if specialization.name.lower() == data.name.lower():
            raise HTTPException(status_code=409,detail="Specialization already exists",)
    specialization = Specialization(name=data.name,description=data.description,)
    db.add(specialization)
    db.commit()
    db.refresh(specialization)
    return specialization

@router.get("", response_model=list[SpecializationResponse])
def get_specializations(db: Session = Depends(get_db)):
    return db.query(Specialization).all()

@router.get("/{specialization_id}", response_model=SpecializationResponse)
def get_specialization(specialization_id: int,db: Session = Depends(get_db),):
    specialization = db.get(Specialization, specialization_id)
    if specialization is None:
        raise HTTPException(status_code=404,detail="Specialization not found",)
    return specialization

@router.patch("/{specialization_id}", response_model=SpecializationResponse)
def update_specialization(
    specialization_id: int,
    data: SpecializationUpdate,
    db: Session = Depends(get_db),
):
    specialization = db.get(Specialization, specialization_id)
    if specialization is None:
        raise HTTPException(status_code=404,detail="Specialization not found",)
    changes = data.model_dump(exclude_unset=True)
    if "name" in changes:
        specializations = db.query(Specialization).all()
        for item in specializations:
            if item.id != specialization_id:
                if item.name.lower() == changes["name"].lower():
                    raise HTTPException(status_code=409,detail="Specialization already exists",)
        specialization.name = changes["name"]
    if "description" in changes:
        specialization.description = changes["description"]
    db.commit()
    db.refresh(specialization)
    return specialization

@router.delete("/{specialization_id}", status_code=204)
def delete_specialization(specialization_id: int,db: Session = Depends(get_db),):
    specialization = db.get(Specialization, specialization_id)
    if specialization is None:
        raise HTTPException(status_code=404,detail="Specialization not found")
    doctor = db.query(Doctor).filter(Doctor.specialization_id == specialization_id).first()
    if doctor is not None:
        raise HTTPException(status_code=409,detail="This specialization has doctors")
    db.delete(specialization)
    db.commit()
