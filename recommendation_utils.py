from urllib.parse import quote_plus


PROVIDER_DOMAINS = {
    "Amazon": (
        "https://www.amazon.in/s?k={q}"
    ),
    "Flipkart": (
        "https://www.flipkart.com/search?q={q}"
    ),
    "IKEA": (
        "https://www.ikea.com/in/en/search/?q={q}"
    ),
    "Swiggy": (
        "https://www.swiggy.com/search?query={q}"
    ),
    "Zomato": (
        "https://www.zomato.com/search?q={q}"
    ),
    "OYO": (
        "https://www.oyorooms.com/search?location={q}"
    ),
}


def provider_url(
    provider: str,
    query: str,
) -> str:

    template = PROVIDER_DOMAINS.get(
        provider,
        "https://www.google.com/search?q={q}",
    )

    return template.format(
        q=quote_plus(query)
    )


def ensure_budget(
    data: dict,
    budget: float,
) -> dict:

    items = data.get("items") or []

    total = sum(
        float(
            item.get(
                "estimated_price",
                0,
            )
            or 0
        )
        for item in items
    )

    # Scale items down if the AI exceeded
    # the user's budget.
    if total > budget and total > 0:

        ratio = budget / total

        for item in items:
            item["estimated_price"] = round(
                float(
                    item.get(
                        "estimated_price",
                        0,
                    )
                    or 0
                )
                * ratio,
                2,
            )

        total = sum(
            float(
                item.get(
                    "estimated_price",
                    0,
                )
                or 0
            )
            for item in items
        )

    data["estimated_total"] = round(
        total,
        2,
    )

    data["remaining_budget"] = round(
        max(
            0,
            budget - total,
        ),
        2,
    )

    for item in items:

        item.setdefault(
            "currency",
            data.get(
                "currency",
                "INR",
            ),
        )

        item.setdefault(
            "provider",
            "Amazon",
        )

        item.setdefault(
            "search_url",
            provider_url(
                item["provider"],
                item.get(
                    "name",
                    "product",
                ),
            ),
        )

        item.setdefault(
            "why_it_fits",
            "Fits the stated preferences and budget.",
        )

        estimated_price = float(
            item.get(
                "estimated_price",
                0,
            )
            or 0
        )

        item.setdefault(
            "budget_share",
            round(
                (
                    estimated_price
                    / budget
                    * 100
                )
                if budget
                else 0,
                2,
            ),
        )

    return data


def demo_recommendation(
    planner: str,
    request: dict,
) -> dict:

    budget = float(
        request["budget"]
    )

    currency = request.get(
        "currency",
        "INR",
    )

    # ========================================================
    # HOME
    # ========================================================

    if planner == "home":

        rooms = ", ".join(
            request.get(
                "rooms",
                [],
            )
        )

        items = [
            {
                "category": "Lighting",
                "name": (
                    "Warm LED lighting set "
                    f"for {rooms}"
                ),
                "estimated_price": round(
                    budget * 0.12,
                    2,
                ),
                "provider": "IKEA",
                "why_it_fits": (
                    "Adds layered lighting "
                    "while keeping the plan practical."
                ),
            },
            {
                "category": "Furniture",
                "name": (
                    "Compact "
                    f"{request.get('style', 'modern')} "
                    "storage unit"
                ),
                "estimated_price": round(
                    budget * 0.28,
                    2,
                ),
                "provider": "Amazon",
                "why_it_fits": (
                    "A flexible anchor piece "
                    "for a budget-conscious room plan."
                ),
            },
            {
                "category": "Decor",
                "name": (
                    "Wall art and "
                    "soft-furnishing bundle"
                ),
                "estimated_price": round(
                    budget * 0.10,
                    2,
                ),
                "provider": "Flipkart",
                "why_it_fits": (
                    "Adds visual character "
                    "without consuming the core furniture budget."
                ),
            },
            {
                "category": "Utility",
                "name": (
                    "Ceiling fan / appliance allowance"
                ),
                "estimated_price": round(
                    budget * 0.18,
                    2,
                ),
                "provider": "Amazon",
                "why_it_fits": (
                    "Reserves budget for essential "
                    "functional items."
                ),
            },
        ]

        return {
            "planner_type": "home",
            "title": "Home Interior Budget Plan",
            "summary": (
                f"A starter plan for {rooms} "
                f"using a "
                f"{request.get('style', 'modern')} "
                "style."
            ),
            "total_budget": budget,
            "currency": currency,
            "allocation": {
                "Furniture": 40,
                "Lighting": 15,
                "Decor": 15,
                "Utility": 30,
            },
            "items": items,
            "tips": [
                (
                    "Measure rooms before "
                    "purchasing large furniture."
                ),
                (
                    "Keep a contingency reserve "
                    "for delivery and installation."
                ),
            ],
            "disclaimer": (
                "Demo recommendations are illustrative; "
                "prices and availability must be verified "
                "with the provider."
            ),
        }

    # ========================================================
    # PARTY
    # ========================================================

    if planner == "party":

        items = [
            {
                "category": "Catering",
                "name": (
                    "Catering allowance for "
                    f"{request['guests']} guests"
                ),
                "estimated_price": round(
                    budget * 0.45,
                    2,
                ),
                "provider": "Swiggy",
                "why_it_fits": (
                    "Uses the largest allocation "
                    "for the guest-facing experience."
                ),
            },
            {
                "category": "Decoration",
                "name": (
                    f"{request['event_type']} "
                    "decoration package"
                ),
                "estimated_price": round(
                    budget * 0.15,
                    2,
                ),
                "provider": "Amazon",
                "why_it_fits": (
                    "Covers basic decor while "
                    "protecting the food budget."
                ),
            },
            {
                "category": "Venue",
                "name": (
                    "Venue search in "
                    f"{request.get('city') or 'your city'}"
                ),
                "estimated_price": round(
                    budget * 0.25,
                    2,
                ),
                "provider": "OYO",
                "why_it_fits": (
                    "Leaves room for a venue "
                    "or accommodation option."
                ),
            },
            {
                "category": "Entertainment",
                "name": (
                    "Music and activity allowance"
                ),
                "estimated_price": round(
                    budget * 0.10,
                    2,
                ),
                "provider": "Zomato",
                "why_it_fits": (
                    "Provides a small flexible "
                    "allowance for event extras."
                ),
            },
        ]

        return {
            "planner_type": "party",
            "title": "Party Budget Plan",
            "summary": (
                f"A {request['event_type']} plan "
                f"for {request['guests']} guests."
            ),
            "total_budget": budget,
            "currency": currency,
            "allocation": {
                "Catering": 45,
                "Venue": 25,
                "Decoration": 15,
                "Entertainment": 10,
                "Contingency": 5,
            },
            "items": items,
            "tips": [
                (
                    "Confirm per-person catering "
                    "pricing before booking."
                ),
                (
                    "Keep at least a small contingency "
                    "for last-minute guests or transport."
                ),
            ],
            "disclaimer": (
                "Demo recommendations are illustrative; "
                "vendor prices and availability must be verified."
            ),
        }

    # ========================================================
    # JEWELRY
    # ========================================================

    items = [
        {
            "category": "Earrings",
            "name": (
                f"{request.get('style', 'elegant')} "
                "statement earrings"
            ),
            "estimated_price": round(
                budget * 0.25,
                2,
            ),
            "provider": "Amazon",
            "why_it_fits": (
                "A versatile focal piece "
                "for the selected occasion."
            ),
        },
        {
            "category": "Necklace",
            "name": (
                f"{request.get('metal', 'Any')} "
                "coordinated necklace"
            ),
            "estimated_price": round(
                budget * 0.40,
                2,
            ),
            "provider": "Flipkart",
            "why_it_fits": (
                "Creates a coordinated look "
                "while respecting the main budget."
            ),
        },
        {
            "category": "Bracelet",
            "name": (
                "Minimal matching bracelet"
            ),
            "estimated_price": round(
                budget * 0.15,
                2,
            ),
            "provider": "Amazon",
            "why_it_fits": (
                "Adds detail without overloading "
                "the overall look."
            ),
        },
    ]

    return {
        "planner_type": "jewelry",
        "title": "Jewelry Budget Plan",
        "summary": (
            f"A {request['occasion']} "
            "jewelry plan in a "
            f"{request.get('style', 'elegant')} "
            "direction."
        ),
        "total_budget": budget,
        "currency": currency,
        "allocation": {
            "Earrings": 25,
            "Necklace": 40,
            "Bracelet": 15,
            "Reserve": 20,
        },
        "items": items,
        "tips": [
            (
                "Check the outfit neckline "
                "before choosing necklace length."
            ),
            (
                "For online purchases, verify "
                "metal purity, dimensions, return policy, "
                "and seller rating."
            ),
        ],
        "disclaimer": (
            "Demo recommendations are illustrative "
            "and are not product availability claims."
        ),
    }