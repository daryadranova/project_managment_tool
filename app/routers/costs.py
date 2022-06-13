from typing import List, Optional
from fastapi import status, HTTPException, Depends, APIRouter
from .. import models, schemas, oauth2
from ..database import get_db
from sqlalchemy.orm import Session
from ..utils import role_checker, admin_super_manager_allowed
from sqlalchemy import func
router = APIRouter(prefix="/costs", tags=["Costs"])


@router.post("/",
             status_code=status.HTTP_201_CREATED,
             response_model=schemas.CostsResponce)
def create_cost(costs: schemas.Costs,
                db: Session = Depends(get_db),
                current_user: int = Depends(oauth2.get_current_user)):

    project_id = db.query(models.Projects).filter(
        models.Projects.id == costs.project_id).first()
    if not project_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id: {costs.project_id} not found")

    new_cost = models.Costs(creator_id=current_user.id, **costs.dict())

    db.add(new_cost)
    db.commit()
    db.refresh(new_cost)
    return new_cost


# get costs for the project
# allowed managers, SU and admins
@router.get("/{id}")
def get_costs_for_project(id: int,
                          db: Session = Depends(get_db),
                          current_user: int = Depends(oauth2.get_current_user),
                          # limit: int = 10,
                          search: Optional[str] = ""):
    project = db.query(models.Projects).filter(
        models.Projects.id == id).first()

    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Project with id: {id} not found")

    costs_for_project = db.query(models.Costs).filter(
        models.Costs.project_id == id).first()

    if not costs_for_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Costs for project with id: {id} not found")

    # for c, i in db.query(
    #     models.Transactions, models.Costs).filter(
    #         models.Transactions.cost_id == models.Costs.id):
    #     print("ID: {} Project: {}".format(c.cost_id, i.project_id))

    #     if admin_super_manager_allowed(db, current_user.id, i)

    if admin_super_manager_allowed(db, current_user, id) is not True:
        pass

    costs = db.query(models.Costs, func.sum(
        models.Transactions.amount_of_money).label("paid")).join(
        models.Transactions,
        models.Transactions.cost_id == models.Costs.id,
        isouter=True).group_by(models.Costs.id).filter(
            models.Costs.project_id == id).all()

    # cколько уже заплатили по этому косту

    costs_summ = db.query(func.sum(models.Costs.amount_of_money).label(
        "Total costs")).filter(models.Costs.project_id == id,
                               models.Costs.in_archive is not True).first()

    return costs, costs_summ


# get all costs for all the projects
# admin and superuser allowed
@router.get("/", response_model=List[schemas.Costs])
def get_all_costs(db: Session = Depends(get_db),
                  current_user: int = Depends(oauth2.get_current_user)):

    if (role_checker(db, current_user) != "superuser"
       and role_checker(db, current_user) != "admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Only superusers and admins are allowed")

    costs_list = db.query(models.Costs).all()
    return costs_list


@router.put("/{id}", response_model=schemas.CostsResponce)
def update_cost(id: int, updated_cost: schemas.Costs,
                db: Session = Depends(get_db),
                current_user: int = Depends(oauth2.get_current_user)):
    cost_query = db.query(models.Costs).filter(models.Costs.id == id)
    cost = cost_query.first()

    if cost is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Cost with id: {id} not found")

    if admin_super_manager_allowed(
     db, current_user, models.Costs.project_id) is not True:
        pass

    cost_query.update(updated_cost.dict(), synchronize_session=False)
    db.commit()

    return cost_query.first()
