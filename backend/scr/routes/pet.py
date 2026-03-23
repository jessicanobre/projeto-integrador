from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Pet
from ..schemas import PetCreate
from ..auth import get_current_user

router = APIRouter()


@router.post("/")
def create_pet(
    pet: PetCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):

    new_pet = Pet(
        name=pet.name,
        type=pet.type,
        age=pet.age,
        owner_id=user.id
    )

    db.add(new_pet)
    db.commit()

    return {"msg": "Pet criado"}


@router.get("/")
def list_pets(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):

    return db.query(Pet).filter(Pet.owner_id == user.id).all()