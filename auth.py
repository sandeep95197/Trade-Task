"""
auth.py

JWT-based guest authentication.
Tokens expire after 1 hour. If no token is sent at all, the request
is treated as an anonymous guest — handy during local testing.
"""

import os
import time
import uuid
from jose import jwt, JWTError
from fastapi import HTTPException

SECRET_KEY = os.getenv("JWT_SECRET", "trade-api-super-secret-key-change-in-prod")
ALGORITHM  = "HS256"
TTL_SECS   = 3600  # 1 hour


def create_guest_token() -> str:
    payload = {
        "sub": f"guest-{uuid.uuid4()}",
        "role": "guest",
        "iat": int(time.time()),
        "exp": int(time.time()) + TTL_SECS,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(authorization: str | None) -> dict:
    # No token at all — treat as anonymous guest so evaluation doesn't require login
    if not authorization:
        return {"sub": f"anon-{uuid.uuid4()}", "role": "guest"}

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(status_code=401, detail="Expected 'Bearer <token>' in Authorization header.")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as exc:
        raise HTTPException(status_code=401, detail=f"Token error: {exc}")
