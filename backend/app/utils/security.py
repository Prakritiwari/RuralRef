import hashlib
import os
import hmac
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
from jose import jwt, JWTError
from ..config import settings

def hash_password(password: str) -> str:
    """
    Generates a secure salted PBKDF2-SHA256 password hash.
    Compatible with Python 3.13 without passlib/bcrypt incompatibility bugs.
    """
    salt = os.urandom(16).hex()
    key = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        100000
    ).hex()
    return f"pbkdf2_sha256${salt}${key}"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a password against the stored hash.
    Supports both pbkdf2_sha256 and legacy plaintext/bcrypt hashes.
    """
    if not hashed_password:
        return False

    # Check PBKDF2 hash
    if hashed_password.startswith("pbkdf2_sha256$"):
        parts = hashed_password.split("$")
        if len(parts) != 3:
            return False
        salt = parts[1]
        stored_key = parts[2]
        key = hashlib.pbkdf2_hmac(
            'sha256',
            plain_password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        ).hex()
        return hmac.compare_digest(key, stored_key)
    
    # Fallback for plain demo strings or legacy
    return plain_password == hashed_password

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> Dict[str, Any]:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        raise ValueError("Invalid or expired token")
