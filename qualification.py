from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
import re


MIN_BUDGET_QUALIFIED = Decimal("500")
HOT_LEAD_BUDGET = Decimal("2000")


@dataclass(frozen=True)
class Qualification:
    score: int
    status: str


def parse_budget(value: str) -> Decimal:
    normalized = value.strip().lower().replace(",", "")
    normalized = re.sub(r"^(?:usd|gbp|eur|[$£€])\s*", "", normalized)
    normalized = re.sub(r"\s*(?:usd|gbp|eur|[$£€])$", "", normalized)
    try:
        budget = Decimal(normalized)
    except InvalidOperation as error:
        raise ValueError("Enter a single budget amount, for example 1500 or $2,000.") from error

    if not budget.is_finite() or budget < 0:
        raise ValueError("Budget must be a non-negative amount.")
    return budget


def qualify_lead(
    budget: Decimal,
    timeline: str,
    project_type: str,
    company: str,
    name: str,
) -> Qualification:
    if budget >= HOT_LEAD_BUDGET:
        budget_points = 50
        status = "Hot lead"
    elif budget >= MIN_BUDGET_QUALIFIED:
        budget_points = 30
        status = "Qualified"
    else:
        budget_points = 0
        status = "Not qualified"

    timeline_text = timeline.lower()
    if re.search(r"\b(asap|urgent|immediate|within\s+(?:a\s+)?month|1\s+month)\b", timeline_text):
        timeline_points = 25
    elif re.search(r"\b(1\s*[-–to]+\s*3|one\s+to\s+three|next\s+quarter)\b", timeline_text):
        timeline_points = 20
    elif re.search(r"\b(3\s*[-–to]+\s*6|three\s+to\s+six)\b", timeline_text):
        timeline_points = 15
    else:
        timeline_points = 10

    score = (
        budget_points
        + timeline_points
        + (15 if len(project_type.strip()) >= 10 else 5)
        + (5 if company.strip() else 0)
        + (5 if name.strip() else 0)
    )
    return Qualification(score=score, status=status)
