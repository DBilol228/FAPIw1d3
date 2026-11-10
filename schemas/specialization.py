from pydantic import BaseModel, Field, field_validator

class SpecializationCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    description: str | None = None

class SpecializationResponse(BaseModel):
    model_config = {"from_attributes": True}
    id: int
    name: str
    description: str | None = None

class SpecializationUpdate(BaseModel):
    model_config = {"extra": "forbid"}
    name: str | None = Field(default=None, min_length=2, max_length=100)
    description: str | None = None
    @field_validator("name")
    @classmethod
    def validate_name(cls, value):
        if value is None:
            raise ValueError("Name cannot be null")
        return value

