import os

import httpx
from fastapi import HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from jose.exceptions import ExpiredSignatureError

AUTHACTION_DOMAIN = os.getenv("AUTHACTION_DOMAIN")
AUTHACTION_AUDIENCE = os.getenv("AUTHACTION_AUDIENCE")

_jwks_cache: dict | None = None


def _get_jwks() -> dict:
    global _jwks_cache
    if _jwks_cache is None:
        jwks_uri = f"https://{AUTHACTION_DOMAIN}/.well-known/jwks.json"
        response = httpx.get(jwks_uri)
        response.raise_for_status()
        _jwks_cache = response.json()
    return _jwks_cache


def _find_rsa_key(token: str) -> dict:
    jwks = _get_jwks()
    unverified_header = jwt.get_unverified_header(token)
    kid = unverified_header.get("kid")

    for key in jwks.get("keys", []):
        if key.get("kid") == kid:
            return {
                "kty": key["kty"],
                "kid": key["kid"],
                "use": key["use"],
                "n": key["n"],
                "e": key["e"],
            }

    # Key not found — could be a rotation; bust cache and retry once
    global _jwks_cache
    _jwks_cache = None
    jwks = _get_jwks()
    for key in jwks.get("keys", []):
        if key.get("kid") == kid:
            return {
                "kty": key["kty"],
                "kid": key["kid"],
                "use": key["use"],
                "n": key["n"],
                "e": key["e"],
            }

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Unable to find matching public key",
    )


def verify_token(token: str) -> dict:
    try:
        rsa_key = _find_rsa_key(token)
        payload = jwt.decode(
            token,
            rsa_key,
            algorithms=["RS256"],
            audience=AUTHACTION_AUDIENCE,
            issuer=f"https://{AUTHACTION_DOMAIN}",
        )
        return payload
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        )


class JWTBearer(HTTPBearer):
    """FastAPI dependency that validates an AuthAction JWT from the Bearer header."""

    async def __call__(self, request: Request) -> dict:
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        if credentials.scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication scheme",
            )
        return verify_token(credentials.credentials)
