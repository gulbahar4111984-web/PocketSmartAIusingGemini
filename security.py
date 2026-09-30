from datetime import datetime, timedelta, timezone
import base64
import hashlib
import hmac
import os

import jwt
from fastapi import HTTPException, status

from app.config import get_settings


ALGORITHM = "HS256"

PASSWORD_ITERATIONS = 310_000


def hash_password(password: str) -> str:
    """
    Hash a password using PBKDF2-HMAC-SHA256.
    """

    salt = os.urandom(16)

    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        PASSWORD_ITERATIONS,
    )

    encoded_salt = base64.urlsafe_b64encode(
        salt
    ).decode("utf-8")

    encoded_digest = base64.urlsafe_b64encode(
        digest
    ).decode("utf-8")

    return (
        f"pbkdf2_sha256$"
        f"{PASSWORD_ITERATIONS}$"
        f"{encoded_salt}$"
        f"{encoded_digest}"
    )


def verify_password(
    password: str,
    encoded: str,
) -> bool:
    """
    Verify a PBKDF2 password hash.
    """

    try:
        scheme, iterations, salt_b64, digest_b64 = (
            encoded.split("$", 3)
        )

        if scheme != "pbkdf2_sha256":
            return False

        salt = base64.urlsafe_b64decode(
            salt_b64.encode("utf-8")
        )

        expected = base64.urlsafe_b64decode(
            digest_b64.encode("utf-8")
        )

        actual = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            int(iterations),
        )

        return hmac.compare_digest(
            actual,
            expected,
        )

    except (
        ValueError,
        TypeError,
        base64.binascii.Error,
    ):
        return False


def create_access_token(subject: str) -> str:
    settings = get_settings()

    expires = (
        datetime.now(timezone.utc)
        + timedelta(
            minutes=settings.access_token_expire_minutes
        )
    )

    payload = {
        "sub": subject,
        "exp": expires,
    }

    return jwt.encode(
        payload,
        settings.secret_key,
        algorithm=ALGORITHM,
    )


def decode_access_token(token: str) -> str:
    try:
        payload = jwt.decode(
            token,
            get_settings().secret_key,
            algorithms=[ALGORITHM],
        )

        subject = payload.get("sub")

        if not subject:
            raise ValueError("Missing subject")

        return str(subject)

    except (
        jwt.PyJWTError,
        ValueError,
    ) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session",
        ) from exc