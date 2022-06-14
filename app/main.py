from fastapi import FastAPI
from . import models
from .database import engine
from .routers import projects, users, auth, access, transactions, costs, accounts
from fastapi.middleware.cors import CORSMiddleware


# models.Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(projects.router)
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(access.router)
app.include_router(transactions.router)
app.include_router(costs.router)
app.include_router(accounts.router)


@app.get("/")
def root():
    return 1
