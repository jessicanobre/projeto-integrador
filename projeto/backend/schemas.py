from pydantic import BaseModel, EmailStr
from typing import List, Optional

# User
class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    profile_photo: Optional[str] = None

    class Config:
        orm_mode = True

# Token
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# Pet
class PetBase(BaseModel):
    name: str
    age: Optional[str] = None
    breed: Optional[str] = None
    photo_base64: Optional[str] = None

class PetCreate(PetBase):
    pass

class PetUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[str] = None
    breed: Optional[str] = None
    photo_base64: Optional[str] = None

class Pet(PetBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True

# Vaccine
class VaccineBase(BaseModel):
    name: str
    date: str
    time: str
    pet_id: int

class VaccineCreate(VaccineBase):
    pass

class VaccineUpdate(BaseModel):
    name: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None
    pet_id: Optional[int] = None

class Vaccine(VaccineBase):
    id: int

    class Config:
        orm_mode = True

# Appointment
class AppointmentBase(BaseModel):
    type: str
    date: str
    time: str
    repetition: str
    pet_id: int

class AppointmentCreate(AppointmentBase):
    pass

class AppointmentUpdate(BaseModel):
    type: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None
    repetition: Optional[str] = None
    pet_id: Optional[int] = None

class Appointment(AppointmentBase):
    id: int

    class Config:
        orm_mode = True

# MedicalRecord
class MedicalRecordBase(BaseModel):
    type: str
    date: str
    description: str
    pet_id: int

class MedicalRecordCreate(MedicalRecordBase):
    pass

class MedicalRecordUpdate(BaseModel):
    type: Optional[str] = None
    date: Optional[str] = None
    description: Optional[str] = None
    pet_id: Optional[int] = None

class MedicalRecord(MedicalRecordBase):
    id: int

    class Config:
        orm_mode = True
