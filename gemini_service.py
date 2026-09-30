import json
from typing import Any

from PIL import Image

from app.config import get_settings
from app.services.recommendation_utils import (
    demo_recommendation,
    ensure_budget,
    provider_url,
)


try:
    from google import genai
    from google.genai import types

except ImportError:  # pragma: no cover
    genai = None
    types = None


class GeminiService:

    def __init__(self):

        self.settings = get_settings()

        self.client = None

        if (
            genai is not None
            and self.settings.gemini_api_key
        ):
            self.client = genai.Client(
                api_key=self.settings.gemini_api_key
            )

    def _build_prompt(
        self,
        planner: str,
        request: dict,
        image_analyzed: bool,
    ) -> str:

        output_schema = {
            "title": "string",
            "summary": "string",
            "allocation": {
                "category": 0
            },
            "items": [
                {
                    "category": "string",
                    "name": "string",
                    "estimated_price": 0,
                    "currency": "INR",
                    "provider": (
                        "Amazon|Flipkart|IKEA|"
                        "Swiggy|Zomato|OYO"
                    ),
                    "why_it_fits": "string",
                    "budget_share": 0,
                }
            ],
            "tips": [
                "string"
            ],
        }

        return f"""
You are PocketSmart AI,
a budget planning and recommendation assistant.

Planner:
{planner}

User request:
{json.dumps(request, ensure_ascii=False)}

Image analyzed:
{image_analyzed}

Return ONLY valid JSON.

Your JSON must follow this structure:

{json.dumps(output_schema, ensure_ascii=False)}

Important rules:

1. Never exceed the user's stated total budget.

2. Estimated prices are planning estimates only.

3. Do not claim live inventory.

4. Do not claim exact current prices.

5. Do not claim real-time availability.

6. Do not invent reviews or seller ratings.

7. Provider names are search destinations only.

8. Prefer 3-8 useful recommendation items.

9. Explain why each recommendation fits.

10. Allocation percentages should be sensible.

11. Allocation percentages should not exceed 100.

12. For jewelry image analysis, only use broad visual
    observations such as visible colors or style.
    Do not infer identity, health, ethnicity,
    religion, personality, or other sensitive traits.

13. Keep recommendations practical for the user's budget.

14. Return valid JSON and nothing else.
"""

    def generate(
        self,
        planner: str,
        request: dict,
        image: Image.Image | None = None,
    ) -> dict:

        image_analyzed = image is not None

        # ----------------------------------------------------
        # No Gemini key -> demo fallback
        # ----------------------------------------------------

        if self.client is None:

            result = demo_recommendation(
                planner,
                request,
            )

            result["source"] = (
                "demo-fallback"
            )

            result["image_analyzed"] = (
                image_analyzed
            )

            result["metadata"] = {
                "mode": "fallback",
                "message": (
                    "Gemini API key is not configured."
                ),
            }

            return ensure_budget(
                result,
                float(request["budget"]),
            )

        # ----------------------------------------------------
        # Gemini request
        # ----------------------------------------------------

        contents: list[Any] = [
            self._build_prompt(
                planner,
                request,
                image_analyzed,
            )
        ]

        if image is not None:
            contents.append(image)

        try:

            response = (
                self.client.models.generate_content(
                    model=self.settings.gemini_model,
                    contents=contents,
                    config=types.GenerateContentConfig(
                        temperature=0.3,
                        response_mime_type="application/json",
                        max_output_tokens=5000,
                    ),
                )
            )

            if not response.text:
                raise ValueError(
                    "Gemini returned an empty response"
                )

            data = json.loads(
                response.text
            )

            data["planner_type"] = planner

            data["total_budget"] = float(
                request["budget"]
            )

            data["currency"] = request.get(
                "currency",
                "INR",
            )

            data["source"] = "gemini"

            data["image_analyzed"] = (
                image_analyzed
            )

            data["disclaimer"] = (
                "AI-generated planning guidance. "
                "Verify prices, product details, "
                "seller/vendor information, and "
                "availability before purchase or booking."
            )

            data = ensure_budget(
                data,
                float(request["budget"]),
            )

            # ------------------------------------------------
            # Generate provider search URLs
            # ------------------------------------------------

            for item in data.get(
                "items",
                [],
            ):

                provider = item.get(
                    "provider",
                    "Amazon",
                )

                item["search_url"] = provider_url(
                    provider,
                    item.get(
                        "name",
                        "product",
                    ),
                )

            return data

        except Exception as exc:

            # ------------------------------------------------
            # Safe fallback
            # ------------------------------------------------

            result = demo_recommendation(
                planner,
                request,
            )

            result["source"] = (
                "demo-fallback"
            )

            result["image_analyzed"] = (
                image_analyzed
            )

            result["metadata"] = {
                "fallback_reason": (
                    "Gemini response was unavailable "
                    "or invalid."
                ),
                "error_type": type(
                    exc
                ).__name__,
            }

            return ensure_budget(
                result,
                float(request["budget"]),
            )


service = GeminiService()