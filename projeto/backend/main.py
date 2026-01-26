from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import shutil
import os

from fastapi.staticfiles import StaticFiles
from . import models, schemas, auth, database
from .database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="PetCare+ API")

# Criar pasta de uploads se não existir
if not os.path.exists("uploads"):
    os.makedirs("uploads")

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

@app.post("/login", response_model=schemas.Token)
def login(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == user_data.email).first()
    if not user or not auth.verify_password(user_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Email ou senha incorretos")
    access_token = auth.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

# Pets
@app.post("/pets", response_model=schemas.Pet)
def create_pet(pet: schemas.PetCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    new_pet = models.Pet(**pet.dict(), owner_id=current_user.id)
    db.add(new_pet)
    db.commit()
    db.refresh(new_pet)
    return new_pet

@app.get("/pets", response_model=List[schemas.Pet])
def get_pets(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    return db.query(models.Pet).filter(models.Pet.owner_id == current_user.id).all()

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
def get_vaccines(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    return db.query(models.Vaccine).join(models.Pet).filter(models.Pet.owner_id == current_user.id).all()

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
def get_appointments(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    return db.query(models.Appointment).join(models.Pet).filter(models.Pet.owner_id == current_user.id).all()

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
def get_medical_records(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    return db.query(models.MedicalRecord).join(models.Pet).filter(models.Pet.owner_id == current_user.id).all()
