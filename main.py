from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
from fastapi import Request

import os

load_dotenv()

app = FastAPI(title="FastAPI + AuthAction")
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET"),
    session_cookie=os.getenv("JWT_COOKIE_NAME", "access_token")
)
templates = Jinja2Templates(directory="templates")

from app.routes.login import router as login_router
from app.routes.m2m import router as m2m_router
app.include_router(login_router, prefix="/auth", tags=["auth"])
app.include_router(m2m_router, prefix="/auth", tags=["auth"])

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})