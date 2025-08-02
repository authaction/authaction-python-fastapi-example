from fastapi import APIRouter, Request, Response
from fastapi.responses import RedirectResponse
import os, secrets, httpx
from urllib.parse import urlencode
from app.utils import url
from fastapi.templating import Jinja2Templates
from app.auth import decode_id_token, fetch_userinfo

router = APIRouter()

templates = Jinja2Templates(directory="templates")

@router.get("/login")
async def login(request: Request):
    state = secrets.token_urlsafe(16)
    request.session["auth_state"] = state
    params = {
        "response_type": "code",
        "client_id": os.getenv("AUTHACTION_CLIENT_ID"),
        "redirect_uri": os.getenv("AUTHACTION_REDIRECT_URI"),
        "scope": "openid email",
        "state": state,
    }
    base = url("/oauth2/authorize")
    auth_url = f"{base}?{urlencode(params)}"
    return RedirectResponse(auth_url)

@router.get("/callback")
async def callback(request: Request):
    code = request.query_params.get("code")
    state = request.query_params.get("state")

    if state != request.session.get("auth_state"):
        return Response("Invalid state", status_code=400)

    token_res = httpx.post(
        url("/oauth2/token"),
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": os.getenv("AUTHACTION_REDIRECT_URI"),
            "client_id": os.getenv("AUTHACTION_CLIENT_ID"),
            "client_secret": os.getenv("AUTHACTION_CLIENT_SECRET"),
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    token_res.raise_for_status()
    tokens = token_res.json()
    id_token = tokens["id_token"]

    user_info = await decode_id_token(id_token)

    request.session["user"] = user_info
    return RedirectResponse("/auth/user")

@router.get("/user")
async def get_user(request: Request):
    user = request.session.get("user")
    if not user:
        return RedirectResponse("/")
    return templates.TemplateResponse("dashboard.html", {"request": request, "user": user})