import json

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import (
    RecommendationHistory,
    User,
)
from app.dependencies import get_current_user
from app.services.history_service import list_history


router = APIRouter(
    prefix="/api/history",
    tags=["History"],
)


@router.get("")
def history(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    rows = list_history(
        db,
        user,
    )

    return [
        {
            "id": row.id,
            "planner_type": row.planner_type,
            "created_at": row.created_at.isoformat(),
            "request": json.loads(
                row.request_json
            ),
            "response": json.loads(
                row.response_json
            ),
        }
        for row in rows
    ]


@router.get("/{history_id}")
def history_detail(
    history_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    row = db.get(
        RecommendationHistory,
        history_id,
    )

    if not row or row.user_id != user.id:
        raise HTTPException(
            status_code=404,
            detail="History entry not found",
        )

    return {
        "id": row.id,
        "planner_type": row.planner_type,
        "created_at": row.created_at.isoformat(),
        "request": json.loads(
            row.request_json
        ),
        "response": json.loads(
            row.response_json
        ),
    }