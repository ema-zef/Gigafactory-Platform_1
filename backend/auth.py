"""Database-backed users; no demo credentials or hard-coded JWT secret."""
import hashlib
import hmac
import os
import secrets
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy import text
from database import engine

ALGORITHM = 'HS256'
BEARER = HTTPBearer(auto_error=False)


def secret_key():
    value = os.getenv('APP_JWT_SECRET', '')
    if len(value) < 32:
        raise RuntimeError('APP_JWT_SECRET must be at least 32 characters')
    return value


def hash_password(password: str) -> str:
    if len(password) < 12:
        raise ValueError('Password must be at least 12 characters')
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 600_000)
    return 'pbkdf2_sha256$600000$' + salt.hex() + '$' + digest.hex()


def check_password(password: str, encoded: str) -> bool:
    try:
        algorithm, count, salt, expected = encoded.split('$')
        if algorithm != 'pbkdf2_sha256' or int(count) < 300_000:
            return False
        actual = hashlib.pbkdf2_hmac('sha256', password.encode(), bytes.fromhex(salt), int(count))
        return hmac.compare_digest(actual, bytes.fromhex(expected))
    except (ValueError, TypeError):
        return False


@dataclass(frozen=True)
class User:
    id: str
    username: str
    role: str

    @property
    def is_admin(self):
        return self.role == 'admin'


def token_for(user: User):
    now = datetime.now(timezone.utc)
    return jwt.encode({'sub': user.id, 'iat': now, 'exp': now + timedelta(hours=8)}, secret_key(), algorithm=ALGORITHM)


def current_user(credentials: HTTPAuthorizationCredentials | None = Depends(BEARER)) -> User:
    if credentials is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, 'Sign in required', headers={'WWW-Authenticate': 'Bearer'})
    try:
        payload = jwt.decode(credentials.credentials, secret_key(), algorithms=[ALGORITHM])
        user_id = str(uuid.UUID(payload['sub']))
    except (JWTError, ValueError, KeyError):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, 'Invalid or expired session')
    with engine.connect() as conn:
        row = conn.execute(text('SELECT user_id, username, role FROM public.app_user WHERE user_id = :id AND is_active'), {'id': user_id}).mappings().first()
    if row is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, 'Account disabled or unavailable')
    return User(str(row['user_id']), row['username'], row['role'])


def admin_only(user: User = Depends(current_user)) -> User:
    if not user.is_admin:
        raise HTTPException(status.HTTP_403_FORBIDDEN, 'Administrator access required')
    return user
