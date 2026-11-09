from fastapi import APIRouter, HTTPException, status
from data import storage
from schemas.specialization import SpecializationCreate, SpecializationResponse, SpecializationUpdate

router = APIRouter(prefix="/specializations",tags=["Specializations"])

@router.post("", response_model=SpecializationResponse, status_code=201)
async def create_specialization(data: SpecializationCreate):
    for specialization in storage.specializations:
        if specialization["name"].lower() == data.name.lower():
            raise HTTPException(
                status_code=409,
                detail="Specialization already exists",
            )
    specialization = data.model_dump()
    specialization["id"] = storage.next_specialization_id
    storage.specializations.append(specialization)
    storage.next_specialization_id += 1
    return specialization

@router.get("", response_model=list[SpecializationResponse])
async def get_specializations():
    return storage.specializations

@router.get("/{specialization_id}", response_model=SpecializationResponse)
async def get_specialization(specialization_id: int):
    for specialization in storage.specializations:
        if specialization["id"] == specialization_id:
            return specialization
    raise HTTPException(status_code=404, detail="Specialization not found")

@router.patch("/{specialization_id}", response_model=SpecializationResponse)
async def update_specialization(specialization_id: int, data: SpecializationUpdate):
    specialization = await get_specialization(specialization_id)
    changes = data.model_dump(exclude_unset=True)
    if "name" in changes:
        for item in storage.specializations:
            if item["id"] != specialization_id:
                if item["name"].lower() == changes["name"].lower():
                    raise HTTPException(status_code=409,detail="Specialization already exists",)
    specialization.update(changes)
    return specialization

@router.delete("/{specialization_id}", status_code=204)
async def delete_specialization(specialization_id: int):
    specialization = await get_specialization(specialization_id)
    for doctor in storage.doctors:
        if doctor["specialization_id"] == specialization_id:
            raise HTTPException(status_code=409,detail="This specialization has doctors",)
    storage.specializations.remove(specialization)