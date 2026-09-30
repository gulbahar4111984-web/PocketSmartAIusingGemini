from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Response,
    status,
)

from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import User
from app.dependencies import get_current_user
from app.schemas import (
    LoginRequest,
    RegisterRequest,
)
from app.security import create_access_token
from app.services.auth_service import (
    authenticate,
    create_user,
)


router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"],
)


COOKIE_NAME = "access_token"


def set_auth_cookie(
    response: Response,
    token: str,
):
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=60 * 60 * 24,
    )


@router.post("/register")
def register(
    payload: RegisterRequest,
    response: Response,
    db: Session = Depends(get_db),
):
    try:
        user = create_user(
            db=db,
            email=payload.email,
            full_name=payload.full_name,
            password=payload.password,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc),
        ) from exc

    token = create_access_token(
        str(user.id)
    )

    set_auth_cookie(
        response,
        token,
    )

    return {
        "message": "Registration successful",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
        },
    }


@router.post("/login")
def login(
    payload: LoginRequest,
    response: Response,
    db: Session = Depends(get_db),
):
    user = authenticate(
        db=db,
        email=payload.email,
        password=payload.password,
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    token = create_access_token(
        str(user.id)
    )

    set_auth_cookie(
        response,
        token,
    )

    return {
        "message": "Login successful",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
        },
    }


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(
        COOKIE_NAME
    )

    return {
        "message": "Logged out"
    }


@router.get("/session-info")
def session_info(
    user: User = Depends(get_current_user),
):
    return {
        "logged_in": True,
        "user_id": user.id,
        "email": user.email,
        "full_name": user.full_name,
    }


@router.get("/session-data")
def session_data(
    user: User = Depends(get_current_user),
):
    return {
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
        },
        "preferences": {},
        "message": "Session is active.",
    }