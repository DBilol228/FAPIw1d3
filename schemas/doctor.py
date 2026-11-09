from pydantic import BaseModel, Field, field_validator

class DoctorCreate(BaseModel):
    full_name: str = Field(min_length=3, max_length=100)
    specialization_id: int = Field(gt=0)
    experience_years: int = Field(ge=0)
    consultation_price: float = Field(gt=0)
    is_active: bool = True

class DoctorResponse(BaseModel):
    id: int
    full_name: str
    specialization_id: int
    experience_years: int
    consultation_price: float
    is_active: bool

class DoctorReplace(DoctorCreate):
    pass

class DoctorUpdate(BaseModel):
    model_config = {"extra": "forbid"}
    full_name: str | None = Field(default=None, min_length=3, max_length=100)
    specialization_id: int | None = Field(default=None, gt=0)
    experience_years: int | None = Field(default=None, ge=0)
    consultation_price: float | None = Field(default=None, gt=0)
    is_active: bool | None = None
    @field_validator(
        "full_name",
        "specialization_id",
        "experience_years",
        "consultation_price",
        "is_active"
    )
    @classmethod
    def reject_null(cls, value):
        if value is None:
            raise ValueError("This field cannot be null")
        return value
