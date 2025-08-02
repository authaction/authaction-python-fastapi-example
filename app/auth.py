import os, time
from typing import Dict
import httpx
from jose import jwt, JWTError
from app.utils import url

DOMAIN = os.getenv("AUTHACTION_DOMAIN")
JWKS_URL = url("/.well-known/jwks.json")
ISSUER = f"https://{DOMAIN}/"
AUDIENCE = os.getenv("AUTHACTION_CLIENT_ID")

_jwks: Dict[str, Dict] = {}
_jwks_expires = 0

async def get_jwks() -> Dict[str, Dict]:
    """
    Fetch and cache JWKS public keys.
    """
    global _jwks, _jwks_expires
    if time.time() > _jwks_expires:
        async with httpx.AsyncClient() as client:
            res = await client.get(JWKS_URL)
            res.raise_for_status()
            keys = res.json().get("keys", [])
        _jwks = {k["kid"]: k for k in keys}
        _jwks_expires = time.time() + 3600
    return _jwks

async def decode_id_token(id_token: str) -> dict:
    """
    Verify and decode an ID token using JWKS.
    """
    header = jwt.get_unverified_header(id_token)
    jwks = await get_jwks()
    key = jwks.get(header.get("kid"))
    if not key:
        raise JWTError("Appropriate key not found")
    payload = jwt.decode(
        id_token,
        key,
        algorithms=[header.get("alg")],
        audience=AUDIENCE,
        issuer=ISSUER,
    )
    return payload

async def fetch_userinfo(access_token: str) -> dict:
    """
    Retrieve user details from AuthAction's UserInfo endpoint.
    """
    async with httpx.AsyncClient() as client:
        res = await client.get(
            url("/userinfo"),
            headers={"Authorization": f"Bearer {access_token}"}
        )
        res.raise_for_status()
        return res.json()

async def get_m2m_token() -> str:
    """
    Fetch machine-to-machine token via Client Credentials flow.
    """
    data = {
        "grant_type": "client_credentials",
        "client_id": os.getenv("AUTHACTION_CLIENT_ID"),
        "client_secret": os.getenv("AUTHACTION_CLIENT_SECRET"),
        "audience": os.getenv("AUTHACTION_AUDIENCE"),
    }
    async with httpx.AsyncClient() as client:
        res = await client.post(
            url("/oauth2/token"),
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        res.raise_for_status()
        return res.json().get("access_token")