import json

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import (
    RecommendationHistory,
    User,
)


def save_history(
    db: Session,
    user: User,
    planner: str,
    request_data: dict,
    response_data: dict,
) -> RecommendationHistory:

    row = RecommendationHistory(
        user_id=user.id,
        planner_type=planner,
        request_json=json.dumps(
            request_data,
            ensure_ascii=False,
        ),
        response_json=json.dumps(
            response_data,
            ensure_ascii=False,
        ),
    )

    db.add(row)
    db.commit()
    db.refresh(row)

    return row


def list_history(
    db: Session,
    user: User,
    limit: int = 50,
):
    statement = (
        select(RecommendationHistory)
        .where(
            RecommendationHistory.user_id
            == user.id
        )
        .order_by(
            RecommendationHistory.created_at.desc()
        )
        .limit(limit)
    )

    return db.scalars(
        statement
    ).all()