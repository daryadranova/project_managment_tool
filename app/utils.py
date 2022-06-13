from passlib.context import CryptContext
from .schemas import UserCreate
from fastapi import Depends, HTTPException, status
from .oauth2 import get_current_user
from . import models

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash(password: str):
    return pwd_context.hash(password)


def verify(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def role_checker(db, user):
    if user.role == "manager":
        return "manager"
    elif user.role == "admin":
        return "admin"
    elif user.role == "superuser":
        return "superuser"


def is_allowed_manager(db, user_id, project_id):
    access_found = db.query(models.Access).filter(
            models.Access.user_id == user_id,
            models.Access.project_id == project_id).first()

    if not access_found:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"You do not have access to the project with id {project_id}")
    return True


def admin_super_manager_allowed(db, user, project_id):
    if (role_checker(db, user) != "superuser" and role_checker(db, user) != "admin"):

        if is_allowed_manager(db, user.id, project_id) is not True:
            pass
    return True


def project_exists(db, id):
    project = db.query(models.Projects).filter(
        models.Projects.id == id)

    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Project with id: {id} not found")
    return True
