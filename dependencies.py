from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import User
from app.security import decode_access_token


def get_current_user(
    access_token: str | None = Cookie(default=None),
    db: Session = Depends(get_db),
) -> User:
    """
    Get the currently authenticated user from the JWT cookie.
    """

    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Login required",
        )

    user_id = decode_access_token(access_token)

    try:
        user_id_int = int(user_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid session",
        ) from exc

    user = db.get(User, user_id_int)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user