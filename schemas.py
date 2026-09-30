import re
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


# ============================================================
# Authentication
# ============================================================

class RegisterRequest(BaseModel):
    email: str
    full_name: str = Field(
        min_length=2,
        max_length=120,
    )
    password: str = Field(
        min_length=8,
        max_length=128,
    )

    @field_validator("email")
    @classmethod
    def check_email(cls, value: str) -> str:
        return valid_email(value)


class LoginRequest(BaseModel):
    email: str
    password: str = Field(
        min_length=1,
        max_length=128,
    )

    @field_validator("email")
    @classmethod
    def check_email(cls, value: str) -> str:
        return valid_email(value)


def valid_email(value: str) -> str:
    value = value.strip().lower()

    if not re.fullmatch(
        r"[^\s@]+@[^\s@]+\.[^\s@]+",
        value,
    ):
        raise ValueError("Enter a valid email address")

    return value


# ============================================================
# Home Planner
# ============================================================

class HomeRequest(BaseModel):
    budget: float = Field(
        gt=0,
        le=10_000_000,
    )

    currency: str = Field(
        default="INR",
        min_length=3,
        max_length=3,
    )

    rooms: list[str] = Field(
        min_length=1,
        max_length=10,
    )

    style: str = Field(
        default="modern",
        min_length=2,
        max_length=80,
    )

    priorities: list[str] = Field(
        default_factory=list,
        max_length=10,
    )

    notes: str = Field(
        default="",
        max_length=1000,
    )

    @field_validator("rooms")
    @classmethod
    def clean_rooms(cls, value: list[str]) -> list[str]:
        cleaned = [
            room.strip()
            for room in value
            if room.strip()
        ]

        if not cleaned:
            raise ValueError(
                "Select at least one room"
            )

        return cleaned


# ============================================================
# Party Planner
# ============================================================

class PartyRequest(BaseModel):
    budget: float = Field(
        gt=0,
        le=10_000_000,
    )

    currency: str = Field(
        default="INR",
        min_length=3,
        max_length=3,
    )

    guests: int = Field(
        gt=0,
        le=10_000,
    )

    event_type: str = Field(
        min_length=2,
        max_length=80,
    )

    venue: str = Field(
        default="Not decided",
        max_length=120,
    )

    food_preference: str = Field(
        default="Mixed",
        max_length=120,
    )

    city: str = Field(
        default="",
        max_length=120,
    )

    notes: str = Field(
        default="",
        max_length=1000,
    )


# ============================================================
# Jewelry Planner
# ============================================================

class JewelryRequest(BaseModel):
    budget: float = Field(
        gt=0,
        le=10_000_000,
    )

    currency: str = Field(
        default="INR",
        min_length=3,
        max_length=3,
    )

    occasion: str = Field(
        min_length=2,
        max_length=100,
    )

    style: str = Field(
        default="elegant",
        min_length=2,
        max_length=100,
    )

    metal: str = Field(
        default="Any",
        max_length=80,
    )

    outfit_color: str = Field(
        default="Unknown",
        max_length=80,
    )

    notes: str = Field(
        default="",
        max_length=1000,
    )


# ============================================================
# Recommendation Response
# ============================================================

class RecommendationItem(BaseModel):
    category: str

    name: str

    estimated_price: float

    currency: str

    provider: str

    search_url: str

    why_it_fits: str

    budget_share: float = Field(
        ge=0,
        le=100,
    )


class RecommendationResponse(BaseModel):
    planner_type: Literal[
        "home",
        "party",
        "jewelry",
    ]

    title: str

    summary: str

    total_budget: float

    currency: str

    estimated_total: float

    remaining_budget: float

    allocation: dict[str, float]

    items: list[RecommendationItem]

    tips: list[str]

    disclaimer: str

    source: Literal[
        "gemini",
        "demo-fallback",
    ]

    image_analyzed: bool = False

    metadata: dict[str, Any] = Field(
        default_factory=dict
    )