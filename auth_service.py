from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import User
from app.security import (
    hash_password,
    verify_password,
)


def create_user(
    db: Session,
    email: str,
    full_name: str,
    password: str,
) -> User:
    normalized_email = (
        email.strip().lower()
    )

    existing_user = db.scalar(
        select(User).where(
            User.email == normalized_email
        )
    )

    if existing_user:
        raise ValueError(
            "Email is already registered"
        )

    user = User(
        email=normalized_email,
        full_name=full_name.strip(),
        password_hash=hash_password(password),
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def authenticate(
    db: Session,
    email: str,
    password: str,
) -> User | None:

    normalized_email = (
        email.strip().lower()
    )

    user = db.scalar(
        select(User).where(
            User.email == normalized_email
        )
    )

    if not user:
        return None

    if not verify_password(
        password,
        user.password_hash,
    ):
        return None

    return user