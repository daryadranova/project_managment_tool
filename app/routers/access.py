from typing import List
from fastapi import status, HTTPException, Depends, APIRouter
from .. import models, schemas, oauth2
from ..database import get_db
from sqlalchemy.orm import Session
from ..utils import role_checker


router = APIRouter(prefix="/access",
                   tags=["Give managers access to the projects"])


@router.post("/", status_code=status.HTTP_201_CREATED)
def access(access: schemas.AccessCreate,
           db: Session = Depends(get_db),
           current_user: int = Depends(oauth2.get_current_user)):

    project = db.query(models.Projects).filter(
        models.Projects.id == access.project_id).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id: {access.project_id} does not exist")

    user = db.query(models.Users).filter(
        models.Users.id == access.user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id: {access.user_id} does not exist")

    access_query = db.query(models.Access).filter(
        models.Access.project_id == access.project_id,
        models.Access.user_id == access.user_id)

    found_access = access_query.first()
    if found_access:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"user {access.user_id} alredy\
            has access to the project {access.project_id}")
    new_access = models.Access(project_id=access.project_id,
                               user_id=access.user_id)
    db.add(new_access)
    db.commit()
    return {"message": "successfully added access"}


# get all accesses
@router.get("/",
            response_model=List[schemas.AccessCreate])
# чтобы нормально показывало, должны быть заполнены все поля в schemas
def get_all_accesses(db: Session = Depends(get_db),
                     current_user: int = Depends(oauth2.get_current_user)):
    if (role_checker(db, current_user) != "superuser"
       and role_checker(db, current_user) != "admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Only superusers and admins are allowed")

    access = db.query(models.Access).all()
    return access


# get accesses to the particular project
@router.get("/{id}",
            response_model=List[schemas.AccessCreate])
# чтобы нормально показывало, должны быть заполнены все поля в schemas
def get_assess_for_project(id: int,
                           db: Session = Depends(get_db),
                           current_user: int = Depends(
                               oauth2.get_current_user)):
    if (role_checker(db, current_user) != "superuser"
       and role_checker(db, current_user) != "admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Only superusers and admins are allowed")

    access = db.query(models.Access).filter(
        models.Access.project_id == id).all()

    if not access:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Access to the project with id: {id} not found")
    return access
