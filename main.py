from fastapi import FastAPI

from routers import appointments, doctors, patients, specializations
from contextlib import asynccontextmanager
from database import Base, engine
import models

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(title="MedBook API", lifespan=lifespan)

app.include_router(specializations.router, prefix="/api/v1")
app.include_router(doctors.router, prefix="/api/v1")
app.include_router(patients.router, prefix="/api/v1")
app.include_router(appointments.router, prefix="/api/v1")
