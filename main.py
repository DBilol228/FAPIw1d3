from fastapi import FastAPI

from routers import appointments, doctors, patients, specializations

app = FastAPI(title="MedBook API")

app.include_router(specializations.router, prefix="/api/v1")
app.include_router(doctors.router, prefix="/api/v1")
app.include_router(patients.router, prefix="/api/v1")
app.include_router(appointments.router, prefix="/api/v1")
