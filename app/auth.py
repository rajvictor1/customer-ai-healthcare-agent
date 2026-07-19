"""Authentication stub.

Production: replace with real OAuth2/OIDC integration (Auth0, Keycloak, patient portal SSO).
For now, this module provides:
- A dependency to verify bearer tokens
- A fake verify function for local development
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

security = HTTPBearer(auto_error=False)

async def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    """Verify bearer token. Stub: accepts any non-empty token as 'demo_user'."""
    if not credentials:
        return {"id": "anon", "role": "guest"}
    token = credentials.credentials
    if token in ("demo", "test", "local"):
        return {"id": "demo_user", "role": "customer"}
    # Production: call identity provider introspection endpoint
    return {"id": "user_from_token", "role": "customer"}

async def require_customer(user: dict = Depends(get_current_user)):
    if user.get("role") == "guest":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    return user
