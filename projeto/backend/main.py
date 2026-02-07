from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import shutil
import os
import uuid
from contextlib import asynccontextmanager

from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
import models, schemas, auth, database
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        with engine.begin() as conn:
            result = conn.execute(text("PRAGMA table_info('pets')"))
            cols = [row[1] for row in result.fetchall()]
            if 'photo_base64' not in cols:
                conn.execute(text("ALTER TABLE pets ADD COLUMN photo_base64 TEXT"))
    except Exception:
        pass
    yield

app = FastAPI(title="PetCare+ API", lifespan=lifespan)

# Criar pasta de uploads se não existir
if not os.path.exists("uploads"):
    os.makedirs("uploads")

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


# CORS: allow frontend served from localhost:5500 (and common dev origins)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# (startup logic moved to lifespan handler)

# Auth
@app.post("/register", response_model=schemas.User)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email já cadastrado")
    hashed_password = auth.get_password_hash(user.password)
    new_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/login", response_model=schemas.TokenWithUser)
def login(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    # autentica usuário
    user = auth.authenticate_user(db, user_data.email, user_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Email ou senha incorretos")
    access_token = auth.create_access_token(data={"sub": user.email})
    # retornar token e dados do usuário para o frontend
    return {"access_token": access_token, "token_type": "bearer", "user": user}

# Pets
@app.post("/pets", response_model=schemas.Pet)
def create_pet(pet: schemas.PetCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    new_pet = models.Pet(**pet.dict(), owner_id=current_user.id)
    db.add(new_pet)
    db.commit()
    db.refresh(new_pet)
    return new_pet

@app.get("/pets", response_model=List[schemas.Pet])
def get_pets(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    return db.query(models.Pet).filter(models.Pet.owner_id == current_user.id).offset(skip).limit(limit).all()

@app.get("/pets/{pet_id}", response_model=schemas.Pet)
def get_pet(pet_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    pet = db.query(models.Pet).filter(models.Pet.id == pet_id, models.Pet.owner_id == current_user.id).first()
    if not pet:
        raise HTTPException(status_code=404, detail="Pet não encontrado")
    return pet

@app.put("/pets/{pet_id}", response_model=schemas.Pet)
def update_pet(pet_id: int, pet_update: schemas.PetUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    pet = db.query(models.Pet).filter(models.Pet.id == pet_id, models.Pet.owner_id == current_user.id).first()
    if not pet:
        raise HTTPException(status_code=404, detail="Pet não encontrado")
    update_data = pet_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(pet, key, value)
    db.commit()
    db.refresh(pet)
    return pet

@app.delete("/pets/{pet_id}")
def delete_pet(pet_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    pet = db.query(models.Pet).filter(models.Pet.id == pet_id, models.Pet.owner_id == current_user.id).first()
    if not pet:
        raise HTTPException(status_code=404, detail="Pet não encontrado")
    db.delete(pet)
    db.commit()
    return {"detail": "Pet excluído"}

# Vaccines
@app.post("/vaccines", response_model=schemas.Vaccine)
def create_vaccine(vaccine: schemas.VaccineCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    # Verify if pet belongs to user
    pet = db.query(models.Pet).filter(models.Pet.id == vaccine.pet_id, models.Pet.owner_id == current_user.id).first()
    if not pet:
        raise HTTPException(status_code=404, detail="Pet não encontrado")
    new_vaccine = models.Vaccine(**vaccine.dict())
    db.add(new_vaccine)
    db.commit()
    db.refresh(new_vaccine)
    return new_vaccine

@app.get("/vaccines", response_model=List[schemas.Vaccine])
def get_vaccines(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    return db.query(models.Vaccine).join(models.Pet).filter(models.Pet.owner_id == current_user.id).offset(skip).limit(limit).all()

@app.get("/vaccines/{vaccine_id}", response_model=schemas.Vaccine)
def get_vaccine(vaccine_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    vaccine = db.query(models.Vaccine).join(models.Pet).filter(models.Vaccine.id == vaccine_id, models.Pet.owner_id == current_user.id).first()
    if not vaccine:
        raise HTTPException(status_code=404, detail="Vacina não encontrada")
    return vaccine

@app.put("/vaccines/{vaccine_id}", response_model=schemas.Vaccine)
def update_vaccine(vaccine_id: int, vaccine_update: schemas.VaccineUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    vaccine = db.query(models.Vaccine).join(models.Pet).filter(models.Vaccine.id == vaccine_id, models.Pet.owner_id == current_user.id).first()
    if not vaccine:
        raise HTTPException(status_code=404, detail="Vacina não encontrada")
    update_data = vaccine_update.dict(exclude_unset=True)
    if "pet_id" in update_data:
        # verify new pet ownership
        pet = db.query(models.Pet).filter(models.Pet.id == update_data["pet_id"], models.Pet.owner_id == current_user.id).first()
        if not pet:
            raise HTTPException(status_code=400, detail="Pet inválido para essa vacina")
    for key, value in update_data.items():
        setattr(vaccine, key, value)
    db.commit()
    db.refresh(vaccine)
    return vaccine

@app.delete("/vaccines/{vaccine_id}")
def delete_vaccine(vaccine_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    vaccine = db.query(models.Vaccine).join(models.Pet).filter(models.Vaccine.id == vaccine_id, models.Pet.owner_id == current_user.id).first()
    if not vaccine:
        raise HTTPException(status_code=404, detail="Vacina não encontrada")
    db.delete(vaccine)
    db.commit()
    return {"detail": "Vacina excluída"}

# Appointments (Agenda)
@app.post("/appointments", response_model=schemas.Appointment)
def create_appointment(appointment: schemas.AppointmentCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    pet = db.query(models.Pet).filter(models.Pet.id == appointment.pet_id, models.Pet.owner_id == current_user.id).first()
    if not pet:
        raise HTTPException(status_code=404, detail="Pet não encontrado")
    new_app = models.Appointment(**appointment.dict())
    db.add(new_app)
    db.commit()
    db.refresh(new_app)
    return new_app

@app.get("/appointments", response_model=List[schemas.Appointment])
def get_appointments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    return db.query(models.Appointment).join(models.Pet).filter(models.Pet.owner_id == current_user.id).offset(skip).limit(limit).all()

@app.get("/appointments/{appointment_id}", response_model=schemas.Appointment)
def get_appointment(appointment_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    appointment = db.query(models.Appointment).join(models.Pet).filter(models.Appointment.id == appointment_id, models.Pet.owner_id == current_user.id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Agendamento não encontrado")
    return appointment

@app.put("/appointments/{appointment_id}", response_model=schemas.Appointment)
def update_appointment(appointment_id: int, appointment_update: schemas.AppointmentUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    appointment = db.query(models.Appointment).join(models.Pet).filter(models.Appointment.id == appointment_id, models.Pet.owner_id == current_user.id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Agendamento não encontrado")
    update_data = appointment_update.dict(exclude_unset=True)
    if "pet_id" in update_data:
        pet = db.query(models.Pet).filter(models.Pet.id == update_data["pet_id"], models.Pet.owner_id == current_user.id).first()
        if not pet:
            raise HTTPException(status_code=400, detail="Pet inválido para esse agendamento")
    for key, value in update_data.items():
        setattr(appointment, key, value)
    db.commit()
    db.refresh(appointment)
    return appointment

@app.delete("/appointments/{appointment_id}")
def delete_appointment(appointment_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    appointment = db.query(models.Appointment).join(models.Pet).filter(models.Appointment.id == appointment_id, models.Pet.owner_id == current_user.id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Agendamento não encontrado")
    db.delete(appointment)
    db.commit()
    return {"detail": "Agendamento excluído"}

    # Calendar endpoints: return appointments/events between dates
@app.get("/calendar")
def get_calendar(start: str, end: str, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    """Return appointments for current user between `start` and `end` (inclusive).
    Dates must be in YYYY-MM-DD format."""
    # simple validation
    try:
        _ = datetime.fromisoformat(start)
        _ = datetime.fromisoformat(end)
    except Exception:
        raise HTTPException(status_code=400, detail="Parâmetros de data inválidos. Use YYYY-MM-DD")

    events = db.query(models.Appointment).join(models.Pet).filter(
        models.Pet.owner_id == current_user.id,
        models.Appointment.date >= start,
        models.Appointment.date <= end,
    ).all()

    result = []
    for ev in events:
        result.append({
            "id": ev.id,
            "type": ev.type,
            "date": ev.date,
            "time": ev.time,
            "repetition": ev.repetition,
            "pet_id": ev.pet_id,
            "pet_name": ev.pet.name if ev.pet else None,
        })
    return {"events": result}

@app.get("/calendar/day")
def get_calendar_day(date: str, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    """Return events for a single day (date in YYYY-MM-DD)."""
    try:
        _ = datetime.fromisoformat(date)
    except Exception:
        raise HTTPException(status_code=400, detail="Parâmetro de data inválido. Use YYYY-MM-DD")

    events = db.query(models.Appointment).join(models.Pet).filter(
        models.Pet.owner_id == current_user.id,
        models.Appointment.date == date,
    ).all()

    result = []
    for ev in events:
        result.append({
            "id": ev.id,
            "type": ev.type,
            "date": ev.date,
            "time": ev.time,
            "repetition": ev.repetition,
            "pet_id": ev.pet_id,
            "pet_name": ev.pet.name if ev.pet else None,
        })
    return {"events": result}
# Medical Records (Historico)
@app.post("/medical-records", response_model=schemas.MedicalRecord)
def create_medical_record(record: schemas.MedicalRecordCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    pet = db.query(models.Pet).filter(models.Pet.id == record.pet_id, models.Pet.owner_id == current_user.id).first()
    if not pet:
        raise HTTPException(status_code=404, detail="Pet não encontrado")
    new_rec = models.MedicalRecord(**record.dict())
    db.add(new_rec)
    db.commit()
    db.refresh(new_rec)
    return new_rec

@app.get("/medical-records", response_model=List[schemas.MedicalRecord])
def get_medical_records(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    return db.query(models.MedicalRecord).join(models.Pet).filter(models.Pet.owner_id == current_user.id).offset(skip).limit(limit).all()

@app.get("/medical-records/{record_id}", response_model=schemas.MedicalRecord)
def get_medical_record(record_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    record = db.query(models.MedicalRecord).join(models.Pet).filter(models.MedicalRecord.id == record_id, models.Pet.owner_id == current_user.id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Registro não encontrado")
    return record

@app.put("/medical-records/{record_id}", response_model=schemas.MedicalRecord)
def update_medical_record(record_id: int, record_update: schemas.MedicalRecordUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    record = db.query(models.MedicalRecord).join(models.Pet).filter(models.MedicalRecord.id == record_id, models.Pet.owner_id == current_user.id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Registro não encontrado")
    update_data = record_update.dict(exclude_unset=True)
    if "pet_id" in update_data:
        pet = db.query(models.Pet).filter(models.Pet.id == update_data["pet_id"], models.Pet.owner_id == current_user.id).first()
        if not pet:
            raise HTTPException(status_code=400, detail="Pet inválido para esse registro")
    for key, value in update_data.items():
        setattr(record, key, value)
    db.commit()
    db.refresh(record)
    return record

@app.delete("/medical-records/{record_id}")
def delete_medical_record(record_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    record = db.query(models.MedicalRecord).join(models.Pet).filter(models.MedicalRecord.id == record_id, models.Pet.owner_id == current_user.id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Registro não encontrado")
    db.delete(record)
    db.commit()
    return {"detail": "Registro excluído"}

# Current user
@app.get("/users/me", response_model=schemas.User)
def read_current_user(current_user: models.User = Depends(auth.get_current_user)):
    return current_user

# Upload profile photo
@app.post("/users/me/photo", response_model=schemas.User)
def upload_profile_photo(file: UploadFile = File(...), db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    filename = f"user_{current_user.id}_{uuid.uuid4().hex}_{file.filename}"
    filepath = os.path.join("uploads", filename)
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    # store relative path
    current_user.profile_photo = f"/uploads/{filename}"
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user


# Stats endpoint - aggregated data for dashboard
@app.get("/stats")
def get_stats(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    # totals
    pets_count = db.query(models.Pet).filter(models.Pet.owner_id == current_user.id).count()
    vaccines_count = db.query(models.Vaccine).join(models.Pet).filter(models.Pet.owner_id == current_user.id).count()
    appointments_count = db.query(models.Appointment).join(models.Pet).filter(models.Pet.owner_id == current_user.id).count()
    records_count = db.query(models.MedicalRecord).join(models.Pet).filter(models.Pet.owner_id == current_user.id).count()

    # recent records
    recent = db.query(models.MedicalRecord).join(models.Pet).filter(models.Pet.owner_id == current_user.id).order_by(models.MedicalRecord.id.desc()).limit(5).all()
    recent_list = [ {"id": r.id, "type": r.type, "date": r.date, "description": r.description[:200]} for r in recent ]

    return {
        "pets_count": pets_count,
        "vaccines_count": vaccines_count,
        "appointments_count": appointments_count,
        "records_count": records_count,
        "recent_records": recent_list
    }


# Seed endpoint for local testing: creates up to 3 pets with related data for the authenticated user
@app.post("/seed")
def seed_sample_data(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    """Create sample pets, vaccines, appointments and medical records for testing.
    If the user already has 3 or more pets, no new data is created.
    """
    existing_pets = db.query(models.Pet).filter(models.Pet.owner_id == current_user.id).all()
    if len(existing_pets) >= 3:
        return {"detail": "Já existem 3 ou mais pets cadastrados para este usuário.", "pets_count": len(existing_pets)}

    sample_pets = [
        {"name": "Rex", "age": "2", "breed": "SRD"},
        {"name": "Luna", "age": "1", "breed": "Poodle"},
        {"name": "Milo", "age": "3", "breed": "Vira-lata"},
    ]

    created = []
    today = datetime.utcnow().date()

    for p in sample_pets:
        if len(existing_pets) + len(created) >= 3:
            break
        pet = models.Pet(name=p["name"], age=p["age"], breed=p["breed"], owner_id=current_user.id)
        db.add(pet)
        db.commit()
        db.refresh(pet)

        # add a vaccine in 7 days
        vac_date = (today + timedelta(days=7)).isoformat()
        vaccine = models.Vaccine(name="V8", date=vac_date, time="09:00", pet_id=pet.id)
        db.add(vaccine)

        # add an appointment in 10 days
        app_date = (today + timedelta(days=10)).isoformat()
        appointment = models.Appointment(type="Vacinação", date=app_date, time="09:00", repetition="Não repetir", pet_id=pet.id)
        db.add(appointment)

        # add a medical record today
        record = models.MedicalRecord(type="Consulta", date=today.isoformat(), description="Check-up inicial e vacinação programada.", pet_id=pet.id)
        db.add(record)

        db.commit()

        created.append({
            "pet": {"id": pet.id, "name": pet.name},
            "vaccine": {"name": vaccine.name, "date": vaccine.date},
            "appointment": {"date": appointment.date, "time": appointment.time},
            "record": {"date": record.date, "type": record.type}
        })

    total = db.query(models.Pet).filter(models.Pet.owner_id == current_user.id).count()
    return {"detail": "Seed concluído", "created": created, "pets_total": total}
