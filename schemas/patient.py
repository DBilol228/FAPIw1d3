from datetime import date

from pydantic import BaseModel, EmailStr, Field, field_validator

class PatientCreate(BaseModel):
    full_name: str = Field(min_length=3, max_length=100)
    phone: str = Field(min_length=1)
    email: EmailStr | None = None
    birth_date: date | None = None

    @field_validator("birth_date")
    @classmethod
    def check_birth_date(cls, value):
        if value is not None and value > date.today():
            raise ValueError('Birth date cannot be in the future')
        return value

class PatientResponse(BaseModel):
    id: int
    full_name: str
    phone: str
    email: EmailStr | None = None
    birth_date: date | None = None

class PatientReplace(PatientCreate):
    pass

class PatientUpdate(BaseModel):
    model_config = {"extra":"forbid"}
    full_name: str | None = Field(default=None, min_length=3, max_length=100)
    phone: str | None = Field(default=None, min_length=1)
    email: EmailStr | None = None
    birth_date: date | None = None
    @field_validator("full_name","phone")
    @classmethod
    def reject_null(cls, value):
        if value is None:
            raise ValueError("This field cannot be null")
        return value
    @field_validator("birth_date")
    @classmethod
    def check_birth_date(cls, value):
        if value is not None and value > date.today():
            raise ValueError("Birth date cannot be in the future")
        return value
    