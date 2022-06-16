from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date, datetime


class Users(BaseModel):
    name: str
    date_of_birth: date
    is_admin: bool = False
    position: str
    experience: float
    is_allowed: bool = False
    current_projects: tuple
    salary: float
    info: Optional[str] = None
    level_of_user: str


class ProjectBase(BaseModel):
    name: str
    client: str
    is_active: bool
    # project_manager: str
    # contact_person_client: str
    # contract_number: int
    # start_date: date
    # deadline: date
    # finish_date: date
    # contract_link: str
    # status: str
    # current_result_link: str

    class Config:
        orm_mode = True


class ProjetCreate(ProjectBase):
    pass


class ProjetUpdate(ProjectBase):
    pass


class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    created_at: datetime

    class Config:
        orm_mode = True


class ProjectResponce(BaseModel):
    name: str
    client: str
    created_at: datetime
    owner_id: int
    owner: UserOut
    id: int

    pass

    class Config:
        orm_mode = True


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str
    role: str

    class Config:
        orm_mode = True


class UserGet(UserCreate):
    id: int
    name: str
    date_of_birth: datetime
    is_admin: bool
    position: str
    created_at: datetime
    role: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str

    class Config:
        orm_mode = True


class TokenData(BaseModel):
    id: Optional[str] = None


class AccessCreate(BaseModel):
    project_id: int
    user_id: int

    class Config:
        orm_mode = True


class Accounts(BaseModel):
    name: str
    balance: Optional[float] = 0.0

    class Config:
        orm_mode = True


class Costs(BaseModel):

    project_id: int
    type: Optional[str] = "Name of the cost"
    is_addon: Optional[bool] = "False"
    supplier: Optional[str] = "Name of the supplier"
    amount_of_money: float
    in_archive: bool
    id: int

    class Config:
        orm_mode = True


class CostsResponce(BaseModel):
    type: Optional[str] = "Name of the cost"
    is_addon: Optional[bool] = "False"
    supplier: Optional[str] = "Name of the supplier"
    creator_id: int
    amount_of_money: float
    in_archive: bool
    project: ProjectResponce
    id: int

    class Config:
        orm_mode = True


class Costs_for_project_Responce(CostsResponce):
    total_costs: float

    class Config:
        orm_mode = True


class Transactions(BaseModel):
    account_from: str
    to_who: str
    amount_of_money: float
    cost_id: int

    class Config:
        orm_mode = True


class TransactionResponce(BaseModel):
    id: int
    created_at: datetime
    creator_id: int
    cost_info: CostsResponce
    account_from: str
    to_who: str
    amount_of_money: float
    cost_id: int

    class Config:
        orm_mode = True
