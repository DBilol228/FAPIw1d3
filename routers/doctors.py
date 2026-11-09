from fastapi import APIRouter, HTTPException
from data import storage
from schemas.doctor import DoctorCreate, DoctorResponse, DoctorReplace, DoctorUpdate

router = APIRouter(prefix="/doctors", tags=["Doctors"])

@router.post("", response_model=DoctorResponse, status_code=201)
async def create_doctor(data: DoctorCreate):
    specialization_exists = False
    for specialization in storage.specializations:
        if specialization["id"] == data.specialization_id:
            specialization_exists = True
            break
    if specialization_exists == False:
        raise HTTPException(
            status_code=404,
            detail="Specialization not found",
        )
    doctor = data.model_dump()
    doctor["id"] = storage.next_doctor_id
    storage.doctors.append(doctor)
    storage.next_doctor_id += 1
    return doctor

@router.get("",response_model=list[DoctorResponse])
async def get_doctors(specialization_id: int | None = None,
    is_active: bool | None = None,
    min_experience: int | None = None,
    max_price: float | None = None,
    search: str | None = None,
):
    result = []
    for doctor in storage.doctors:
        if specialization_id is not None:
            if doctor['specialization_id'] != specialization_id:
                continue
        if is_active is not None:
            if doctor['is_active'] != is_active:
                continue
        if min_experience is not None:
            if doctor['experience_years'] < min_experience:
                continue
        if max_price is not None:
            if doctor['consultation_price'] > max_price:
                continue
        if search is not None:
            if search.lower() not in doctor['full_name'].lower():
                continue
        result.append(doctor)
    return result

@router.get('/{doctor_id}', response_model=DoctorResponse)
async def get_doctor(doctor_id: int):
    for doctor in storage.doctors:
        if doctor['id'] == doctor_id:
            return doctor
    raise HTTPException(status_code=404, detail="Doctor not found")

@router.put("/{doctor_id}", response_model=DoctorResponse)
async def replace_doctor(doctor_id: int, data: DoctorReplace):
    doctor = await get_doctor(doctor_id)
    specialization_exists = False
    for specialization in storage.specializations:
        if specialization["id"] == data.specialization_id:
            specialization_exists = True
            break
    if specialization_exists == False:
        raise HTTPException(
            status_code=404,
            detail="Specialization not found",
        )
    doctor.clear()
    doctor.update(data.model_dump())
    doctor["id"] = doctor_id
    return doctor

@router.patch("/{doctor_id}", response_model=DoctorResponse)
async def update_doctor(doctor_id: int, data: DoctorUpdate):
    doctor = await get_doctor(doctor_id)
    changes = data.model_dump(exclude_unset=True)
    if "specialization_id" in changes:
        specialization_exists = False
        for specialization in storage.specializations:
            if specialization['id'] == changes['specialization_id']:
                specialization_exists = True
                break
        if specialization_exists == False:
            raise HTTPException(status_code=404,detail="Specialization not found")
    doctor.update(changes)
    return doctor

@router.delete("/{doctor_id}", status_code=204)
async def delete_doctor(doctor_id: int):
    doctor = await get_doctor(doctor_id)
    for appointment in storage.appointments:
        if appointment["doctor_id"] == doctor_id:
            raise HTTPException(status_code=409,detail="This doctor has appointments")
    storage.doctors.remove(doctor)
