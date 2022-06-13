from typing import List, Optional
from fastapi import status, HTTPException, Depends, APIRouter
from .. import models, schemas, oauth2
from ..database import get_db
from sqlalchemy.orm import Session
from ..utils import role_checker

router = APIRouter(prefix="/accounts", tags=["Bank accounts"])


# only superuser
@router.post("/",
             status_code=status.HTTP_201_CREATED)
def add_account(accounts: schemas.Accounts,
                db: Session = Depends(get_db),
                current_user: int = Depends(oauth2.get_current_user)):
    if role_checker(db, current_user) != "superuser":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Only superusers are allowed")
    new_account = models.Accounts(**accounts.dict())
    db.add(new_account)
    db.commit()
    db.refresh(new_account)
    return new_account


# only superuser
@router.get("/",
            response_model=List[schemas.Accounts])
def get_all_accounts(db: Session = Depends(get_db),
                     current_user: int = Depends(oauth2.get_current_user),
                     # limit: int = 10,
                     skip: int = 0,
                     search: Optional[str] = ""):
    if (role_checker(db, current_user) != "superuser"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Only superusers and admins are allowed")

    accounts = db.query(models.Accounts).filter(
        models.Accounts.name.contains(search)).offset(skip).all()
    return accounts
