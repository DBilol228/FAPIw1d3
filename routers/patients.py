from fastapi import APIRouter, HTTPException
from data import storage
from schemas.patient import PatientCreate, PatientResponse, PatientReplace, PatientUpdate

router = APIRouter(prefix="/patients", tags=["Patients"])

@router.post("", response_model=PatientResponse, status_code=201)
async def create_patient(data: PatientCreate):
    patient = data.model_dump()
    patient["id"] = storage.next_patient_id
    storage.patients.append(patient)
    storage.next_patient_id += 1 
    return patient

@router.get("", response_model=list[PatientResponse])
async def get_patients(search: str | None = None):
    result = []
    for patient in storage.patients:
        if search is not None:
            if search.lower() not in patient['full_name'].lower():
                continue
        result.append(patient)
    return result

@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient(patient_id: int):
    for patient in storage.patients:
        if patient["id"] == patient_id:
            return patient
    raise HTTPException(status_code=404,detail="Patient not found")

@router.put("/{patient_id}", response_model=PatientResponse)
async def replace_patient(patient_id: int, data: PatientReplace):
    patient = await get_patient(patient_id)
    patient.clear()
    patient.update(data.model_dump())
    patient["id"] = patient_id
    return patient

@router.patch("/{patient_id}", response_model=PatientResponse)
async def update_patient(patient_id: int, data: PatientUpdate):
    patient = await get_patient(patient_id)
    changes = data.model_dump(exclude_unset=True)
    patient.update(changes)
    return patient

@router.delete('/{patient_id}', status_code=204)
async def delete_patient(patient_id: int):
    patient = await get_patient(patient_id)
    for appointment in storage.appointments:
        if appointment['patient_id'] == patient_id:
            raise HTTPException(status_code=409,detail="This patient has appointments")
    storage.patients.remove(patient)