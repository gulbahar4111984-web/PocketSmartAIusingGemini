import io

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
)

from PIL import Image, UnidentifiedImageError

from sqlalchemy.orm import Session

from app.config import get_settings
from app.db.database import get_db
from app.db.models import User
from app.dependencies import get_current_user

from app.schemas import (
    HomeRequest,
    JewelryRequest,
    PartyRequest,
    RecommendationResponse,
)

from app.services.gemini_service import service
from app.services.history_service import save_history


router = APIRouter(
    prefix="/api/planners",
    tags=["Planners"],
)


settings = get_settings()


def run_and_save(
    planner: str,
    payload: dict,
    user: User,
    db: Session,
    image=None,
):
    result = service.generate(
        planner=planner,
        request=payload,
        image=image,
    )

    response = RecommendationResponse.model_validate(
        result
    )

    save_history(
        db=db,
        user=user,
        planner=planner,
        request_data=payload,
        response_data=response.model_dump(),
    )

    return response


@router.post(
    "/home",
    response_model=RecommendationResponse,
)
def home(
    payload: HomeRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return run_and_save(
        planner="home",
        payload=payload.model_dump(),
        user=user,
        db=db,
    )


@router.post(
    "/party",
    response_model=RecommendationResponse,
)
def party(
    payload: PartyRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return run_and_save(
        planner="party",
        payload=payload.model_dump(),
        user=user,
        db=db,
    )


@router.post(
    "/jewelry",
    response_model=RecommendationResponse,
)
async def jewelry(
    budget: float = Form(...),
    currency: str = Form("INR"),
    occasion: str = Form(...),
    style: str = Form("elegant"),
    metal: str = Form("Any"),
    outfit_color: str = Form("Unknown"),
    notes: str = Form(""),
    outfit_image: UploadFile | None = File(
        default=None
    ),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    payload = JewelryRequest(
        budget=budget,
        currency=currency,
        occasion=occasion,
        style=style,
        metal=metal,
        outfit_color=outfit_color,
        notes=notes,
    )

    image = None

    if outfit_image and outfit_image.filename:

        allowed_types = {
            "image/jpeg",
            "image/png",
            "image/webp",
        }

        if outfit_image.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Only JPEG, PNG, and WebP "
                    "images are supported"
                ),
            )

        raw = await outfit_image.read(
            settings.max_upload_bytes + 1
        )

        if len(raw) > settings.max_upload_bytes:
            raise HTTPException(
                status_code=413,
                detail=(
                    f"Image must be "
                    f"{settings.max_upload_mb} MB "
                    "or smaller"
                ),
            )

        try:
            image = Image.open(
                io.BytesIO(raw)
            ).convert("RGB")

        except UnidentifiedImageError as exc:
            raise HTTPException(
                status_code=400,
                detail="Invalid image file",
            ) from exc

    return run_and_save(
        planner="jewelry",
        payload=payload.model_dump(),
        user=user,
        db=db,
        image=image,
    )