from .database import Base
from sqlalchemy import (Column,
                        ForeignKey,
                        Integer,
                        String,
                        Date,
                        VARCHAR,
                        Boolean,
                        Float)
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import text


class Projects(Base):
    __tablename__ = 'Projects'

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False, unique=True)
    client = Column(String, nullable=True)
    revenue = Column(Float, nullable=False, server_default='0.0')
    project_manager = Column(String, nullable=True)
    contact_person_client = Column(String, nullable=True)
    contract_number = Column(Integer, nullable=True)
    start_date = Column(Date, nullable=True)
    deadline = Column(Date, nullable=True)
    finish_date = Column(Date, nullable=True)
    contract_link = Column(VARCHAR, nullable=True)
    status = Column(String, nullable=True)
    current_result_link = Column(VARCHAR, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=True,
                        server_default=text('now()'))
    owner_id = Column(Integer,
                      ForeignKey("Users.id",
                                 ondelete="CASCADE"),
                      nullable=False)
    is_active = Column(Boolean,
                       nullable=False,
                       server_default='False')

    owner = relationship("Users")


class Users(Base):

    __tablename__ = 'Users'

    id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    name = Column(String, nullable=False)
    date_of_birth = Column(Date, nullable=True)
    position = Column(String, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=True,
                        server_default=text('now()'))
    role = Column(String, nullable=False)  # manager, admin, superuser


class Access(Base):

    __tablename__ = 'Access'

    project_id = Column(Integer,
                        ForeignKey("Projects.id",
                                   ondelete="CASCADE"),
                        primary_key=True)
    user_id = Column(Integer,
                     ForeignKey("Users.id",
                                ondelete="CASCADE"),
                     primary_key=True)
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=True,
                        server_default=text('now()'))


class Accounts(Base):

    __tablename__ = 'Accounts'

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False, unique=True)
    balance = Column(Float, nullable=False, server_default="0.0")
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=True,
                        server_default=text('now()'))


class Costs(Base):

    __tablename__ = 'Costs'

    project_id = Column(Integer,
                        ForeignKey("Projects.id",
                                   ondelete="CASCADE"))
    id = Column(Integer, primary_key=True, nullable=False)
    type = Column(String, nullable=True)
    is_addon = Column(Boolean, nullable=False, server_default="False")
    supplier = Column(String, nullable=False)
    project = relationship('Projects')
    amount_of_money = Column(Float, nullable=False, server_default="0.0")
    creator_id = Column(Integer,
                        ForeignKey("Users.id",
                                   ondelete="CASCADE"))
    # paid = Column(Float, nullable=True)
    # due = Column(Float, nullable=True)
    in_archive = Column(Boolean, nullable=False, server_default="False")
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=True,
                        server_default=text('now()'))


class Transactions(Base):

    __tablename__ = 'Transactions'

    id = Column(Integer, primary_key=True, nullable=False)
    account_from = Column(String,
                          ForeignKey("Accounts.name",
                                     ondelete="CASCADE"),
                          nullable=False)
    to_who = Column(String, nullable=False)
    amount_of_money = Column(Float, nullable=False, server_default="0.0")
    cost_id = Column(Integer,
                     ForeignKey("Costs.id",
                                ondelete="CASCADE"),
                     nullable=True)
    creator_id = Column(Integer,
                        ForeignKey("Users.id",
                                   ondelete="CASCADE"),
                        nullable=False)
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=True,
                        server_default=text('now()'))
    cost_info = relationship("Costs")
