from typing import List, Optional
from fastapi import status, HTTPException, Depends, APIRouter
from .. import models, schemas, oauth2
from ..database import get_db
from sqlalchemy.orm import Session
from ..utils import role_checker

router = APIRouter(prefix="/transactions", tags=["transactions"])

# get all tranactions for all projects - who?
# get costs for particular project - allowed managers
# delete cost - who?
# modify cost - who?


@router.post("/",
             status_code=status.HTTP_201_CREATED,
             response_model=schemas.TransactionResponce)
def create_transaction(transactions: schemas.Transactions,
                       db: Session = Depends(get_db),
                       current_user: int = Depends(oauth2.get_current_user)):
    cost_id_found = db.query(models.Costs).filter(
        models.Costs.id == transactions.cost_id
    ).first()
    if not cost_id_found:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Can not find cost with id {transactions.cost_id}")

    new_transaction = models.Transactions(
        creator_id=current_user.id,
        **transactions.dict())
    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)
    return new_transaction
# если есть доступ к проекту


@router.get("/",
            response_model=List[schemas.Transactions])
# чтобы нормально показывало, должны быть заполнены все поля в schemas
def get_all_transactions(db: Session = Depends(get_db),
                         current_user: int = Depends(oauth2.get_current_user),
                         search: Optional[str] = "",
                         skip: int = 0):
    if (role_checker(db, current_user) != "superuser"
       and role_checker(db, current_user) != "admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Only superusers and admins are allowed")

    transaction = db.query(models.Transactions).filter(
        models.Transactions.to_who.contains(search)).offset(skip).all()
    return transaction
