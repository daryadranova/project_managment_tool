from typing import List, Optional
from fastapi import Response, status, HTTPException, Depends, APIRouter
from .. import models, schemas, oauth2
from ..database import get_db
from sqlalchemy.orm import Session
from ..utils import role_checker, admin_super_manager_allowed
from fastapi.templating import Jinja2Templates
from sqlalchemy import func

router = APIRouter(prefix="/projects", tags=["Projects"])

templates = Jinja2Templates(directory="templates")


@router.post("/",
             status_code=status.HTTP_201_CREATED)
def create_project(projects: schemas.ProjetCreate,
                   db: Session = Depends(get_db),
                   current_user: int = Depends(oauth2.get_current_user)):
    # cursor.execute("""INSERT INTO praxis_projects (name, client,
    # project_manager) VALUES (%s, %s, %s) RETURNING * """,
    #                (project.name, project.client, project.project_manager))
    # new_project = cursor.fetchone()
    # connection.commit()
    new_project = models.Projects(owner_id=current_user.id, **projects.dict())
    db.add(new_project) 
    db.commit()
    db.refresh(new_project)
    return new_project


# only admins and superusers are allowed
@router.get("/",
            response_model=List[schemas.ProjectResponce])
# чтобы нормально показывало, должны быть заполнены все поля в schemas
def get_latest_project(db: Session = Depends(get_db),
                       current_user: int = Depends(oauth2.get_current_user),
                       # limit: int = 10,
                       skip: int = 0,
                       search: Optional[str] = ""):
    if (role_checker(db, current_user) != "superuser"
       and role_checker(db, current_user) != "admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Only superusers and admins are allowed")

    projects = db.query(models.Projects).filter(
        models.Projects.name.contains(search)).offset(skip).all()
    return projects


# allowed managers, SU, admins
@router.get("/{client}/{id}")
def get_project(id: int, client: str,
                db: Session = Depends(get_db),
                current_user: int = Depends(oauth2.get_current_user)):
    # cursor.execute("""SELECT * FROM praxis_projects WHERE name = %s AND
    # client = %s """, (name, client))
    # project = cursor.fetchall()
    # print(project)

    if admin_super_manager_allowed(db, current_user, id) is not True:
        pass

    project = db.query(models.Projects).filter(
        models.Projects.id == id,
        models.Projects.client == client).first()

    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Project with id: {id} not found")

    costs = db.query(models.Costs, func.sum(
        models.Transactions.amount_of_money).label("paid")).join(
        models.Transactions,
        models.Transactions.cost_id == models.Costs.id,
        isouter=True).group_by(models.Costs.id).filter(
            models.Costs.project_id == id).all()
    return project, costs


@router.delete("/{name}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(name: str,
                   db: Session = Depends(get_db),
                   current_user: int = Depends(oauth2.get_current_user)):
    # cursor.execute(""" DELETE FROM praxis_projects WHERE name = %s RETURNING
    # *""", [name])
    # deleted_project = cursor.fetchone()
    # connection.commit()
    project_query = db.query(models.Projects).filter(
        models.Projects.name == name)
    project = project_query.first()

    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Project with name: {name} not found")

    if project.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized")
    project_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{name}", response_model=schemas.ProjectResponce)
def update_project(name: str, updated_project: schemas.ProjetUpdate,
                   db: Session = Depends(get_db),
                   current_user: int = Depends(oauth2.get_current_user)):
    # cursor.execute(""" UPDATE praxis_projects SET name = %s, client = %s
    # WHERE id = %s RETURNING * """,
    #                (project.client, project.name, str(id)))
    # updated_project = cursor.fetchone()
    # connection.commit()
    project_query = db.query(models.Projects).filter(
        models.Projects.name == name)
    project = project_query.first()

    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Project with name: {name} not found")

    if project.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized")

    project_query.update(updated_project.dict(), synchronize_session=False)
    db.commit()
    return project_query.first()
