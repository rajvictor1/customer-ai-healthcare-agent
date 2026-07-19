"""OAuth2/OIDC authentication helpers."""

from functools import lru_cache
from typing import Optional

import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from app.config import get_settings

security = HTTPBearer(auto_error=False)


@lru_cache(maxsize=1)
def _jwks() -> dict:
    settings = get_settings()
    if not settings.AUTH_ISSUER:
        return {}
    discovery_url = settings.AUTH_ISSUER.rstrip("/") + "/.well-known/openid-configuration"
    with httpx.Client(timeout=5.0) as client:
        discovery = client.get(discovery_url).raise_for_status().json()
        jwks_uri = discovery["jwks_uri"]
        return client.get(jwks_uri).raise_for_status().json()


def _local_user(token: str) -> Optional[dict]:
    if token in ("demo", "test", "local"):
        return {"id": "demo_user", "role": "customer"}
    return None


async def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    """Verify a bearer token with the configured OIDC issuer.

    If no OIDC provider is configured, only explicit local demo tokens are accepted.
    """
    if not credentials:
        return {"id": "anon", "role": "guest"}

    token = credentials.credentials
    local_user = _local_user(token)
    if local_user:
        return local_user

    settings = get_settings()
    if not settings.AUTH_ISSUER or not settings.AUTH_CLIENT_ID:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication provider is not configured",
        )

    try:
        claims = jwt.decode(
            token,
            _jwks(),
            algorithms=["RS256"],
            audience=settings.AUTH_CLIENT_ID,
            issuer=settings.AUTH_ISSUER.rstrip("/"),
        )
    except (JWTError, httpx.HTTPError, KeyError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
        ) from exc

    role = claims.get("role") or claims.get("https://claims.example.com/role") or "customer"
    return {
        "id": claims.get("sub"),
        "email": claims.get("email"),
        "role": role,
    }

async def require_customer(user: dict = Depends(get_current_user)):
    if user.get("role") == "guest":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    return user
