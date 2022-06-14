from fastapi import FastAPI
# from .database import engine
from .routers import projects, users, auth, access, transactions, costs, accounts
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

# models.Base.metadata.create_all(bind=engine)

app = FastAPI()

templates = Jinja2Templates(directory="templates")

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
async def home(request: Request):
    return templates.TemplateResponse(
        "index.html", {"request": request})
