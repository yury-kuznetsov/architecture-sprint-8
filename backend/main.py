from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import random
import time
import os
from jose import jwt
import requests

app = FastAPI(title="Reports API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

KEYCLOAK_URL = "http://keycloak:8080"
KEYCLOAK_REALM = "reports-realm"

_jwks_cache = None


def get_jwks():
    global _jwks_cache
    if _jwks_cache is not None:
        return _jwks_cache

    well_known = f"{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}/.well-known/openid-configuration"
    resp = requests.get(well_known)
    if resp.status_code != 200:
        raise HTTPException(status_code=500, detail="Unable to fetch OpenID configuration")

    jwks_uri = resp.json().get("jwks_uri")
    jwks_resp = requests.get(jwks_uri)
    if jwks_resp.status_code != 200:
        raise HTTPException(status_code=500, detail="Unable to fetch JWKS")

    _jwks_cache = jwks_resp.json()
    return _jwks_cache


def decode_jwt(token: str):
    jwks = get_jwks()
    unverified_header = jwt.get_unverified_header(token)
    kid = unverified_header.get("kid")

    key = None
    for k in jwks.get("keys", []):
        if k.get("kid") == kid:
            key = k
            break
    if key is None:
        raise HTTPException(status_code=401, detail="Invalid token header")

    try:
        payload = jwt.decode(
            token,
            key,
            algorithms=[unverified_header.get("alg", "RS256")],
            audience=None,
            options={"verify_aud": False}
        )
        return payload
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")


def require_role(authorization: Optional[str] = Header(default=None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing token"
        )

    token = authorization.split(" ")[1]
    payload = decode_jwt(token)

    roles = []
    realm_access = payload.get("realm_access") or {}
    if isinstance(realm_access, dict):
        roles = realm_access.get("roles") or []
    if "prothetic_user" not in roles:
        raise HTTPException(status_code=403, detail="Forbidden")
    return payload

@app.get("/reports")
async def get_reports(user=Depends(require_role)):
    report = {
        "generatedAt": int(time.time()),
        "summary": {
            "users": random.randint(50, 5000),
            "sessions": random.randint(100, 20000),
            "errors": random.randint(0, 200),
        },
        "topCountries": [
            {"country": "US", "visits": random.randint(100, 10000)},
            {"country": "RU", "visits": random.randint(100, 10000)},
            {"country": "DE", "visits": random.randint(100, 10000)},
        ],
        "revenue": {
            "currency": "USD",
            "value": round(random.uniform(1000, 50000), 2)
        }
    }

    return report
