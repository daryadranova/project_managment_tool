from fastapi import status, HTTPException, Depends, APIRouter
from .. import models, schemas, utils, oauth2
from ..database import get_db
from sqlalchemy.orm import Session
from ..utils import role_checker

router = APIRouter(prefix="/users", tags=["Users"])


# only superuser allowed
@router.post("/",
             status_code=status.HTTP_201_CREATED,
             response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate,
                db: Session = Depends(get_db),
                current_user: int = Depends(oauth2.get_current_user)):
    if role_checker(db, current_user) != "superuser":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"You, {current_user.name}, are not\
                            superuser. Only superusers can create new users")
    hashed_password = utils.hash(user.password)
    user.password = hashed_password
    new_user = models.Users(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


# only superuser and admin allowed
@router.get("/{id}", response_model=schemas.UserOut)
def get_user(id: int,
             db: Session = Depends(get_db),
             current_user: int = Depends(oauth2.get_current_user)):

    if (role_checker(db, current_user) != "superuser"
       and role_checker(db, current_user) != "admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Only superusers and admins are allowed")

    user = db.query(models.Users).filter(models.Users.id == id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with id: {id} not found")
    return user
