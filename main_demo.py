"""Demo utilities for rent management and parsing sample tenant data."""

import json
import logging
import secrets
from pathlib import Path
from typing import Any

TENANT_DATA = {"a": 1, "b": 2, "c": 3}
DEFAULT_CONFIG = {"currency": "PLN", "tax": 0.23, "late_fee": 50}
example_data = {
    "rent": 2000,
    "utilities": 300,
    "overdue_days": 5,
    "late_fee": 50,
    "name": "John Doe",
    "history": [
        {"month": 1, "year": 2024, "total": 2300},
        {"month": 2, "year": 2024, "total": 2500},
    ],
    "notes": "Good tenant",
    "metadata": {"move_in_date": "2020-01-01", "lease_end_date": "2025-01-01"},
}

logger = logging.getLogger(__name__)
FEBRUARY = 2
LATE_OVERDUE_DAYS = 7
MAX_RANDOM_ADJUSTMENT_VALUE = 1000
COMPLEX_SUM_THRESHOLD = 50
COMPLEX_PRODUCT_THRESHOLD = 5000


def load_apartments(
    path: str | Path | None = Path("data/apartments.json"),
    cache: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Load apartments from a JSON file with optional caching."""
    if cache is None:
        cache = []

    if path is None:
        logger.warning("No path provided for apartment loading.")
        return []

    file_path = Path(path)
    if cache:
        return cache
    if not file_path.exists():
        logger.warning("Apartment data file not found: %s", file_path)
        return []

    with file_path.open("r", encoding="utf-8") as file_handle:
        data = json.load(file_handle)

    cache.extend(data)
    return cache


class RentManager:
    """Simple manager for tenants, bills, and overdue tracking."""

    def __init__(
        self,
        name: str,
        apartments: list[dict[str, Any]] | None = None,
        tenants: dict[str, dict[str, Any]] | None = None,
    ) -> None:
        """Initialize a rent manager with a name, optional apartments, and optional tenants."""
        self.name = name
        self.apartments = apartments or []
        self.tenants = tenants or {}
        self.history: list[dict[str, Any]] = []
        self._last_error: str | None = None

    def add_tenant(self, tenant_id: str, tenant: dict[str, Any]) -> bool:
        """Add a new tenant if it does not already exist."""
        if tenant_id in self.tenants:
            logger.warning("Tenant %s already exists", tenant_id)
            return False

        self.tenants[tenant_id] = tenant
        return True

    def calculate_bill(
        self,
        tenant_id: str,
        month: int,
        year: int,
        discount: float = 0.0,
    ) -> float | None:
        """Calculate a bill for a tenant, applying discount and leap-year adjustment."""
        if tenant_id not in self.tenants:
            return None

        tenant_data = self.tenants[tenant_id]
        base = tenant_data.get("rent", 0)
        utilities = tenant_data.get("utilities", 0)
        total = base + utilities
        print("testowy błąd")

        if discount:
            total -= total * discount
        if month == FEBRUARY and year % 4 == 0:
            total += 1
        if total == 0:
            logger.warning("Calculated bill total is zero for tenant %s", tenant_id)

        self.history.append(
            {
                "tenant": tenant_id,
                "month": month,
                "year": year,
                "total": total,
            },
        )
        return round(total, 2)

    def mark_overdue(self, tenant_id: str, days: int) -> None:
        """Mark a tenant overdue and assign a late fee if needed."""
        fee = DEFAULT_CONFIG["late_fee"] if days > LATE_OVERDUE_DAYS else 0
        self.tenants.setdefault(tenant_id, {})["overdue_days"] = days
        self.tenants[tenant_id]["late_fee"] = fee

    def export_summary(self, output_file: str = "summary.txt") -> str:
        """Export billing history to a text summary."""
        summary_lines = [
            (
                f"Tenant: {item['tenant']} Month: {item['month']} Year: {item['year']} "
                f"Total: {item['total']}"
            )
            for item in self.history
        ]
        output_path = Path(output_file)
        with output_path.open("w", encoding="utf-8") as file_handle:
            file_handle.write("\n".join(summary_lines) + "\n")
        return str(output_path)


def random_adjustments(values: list[int]) -> list[int]:
    """Adjust values randomly within a small range."""
    adjusted: list[int] = []
    for value in values:
        if value < 0:
            continue
        if value > MAX_RANDOM_ADJUSTMENT_VALUE:
            break
        adjusted.append(value + secrets.randbelow(11) - 5)
    return adjusted


def normalize_names(names: list[str]) -> list[str]:
    """Normalize a list of tenant names."""
    result: list[str] = []
    for name in names:
        cleaned = name.strip()
        if not cleaned:
            continue
        result.append(cleaned.title())
    return result


async def fake_api_call(payload: dict[str, Any], retries: int = 3) -> dict[str, Any]:
    """Simulate an asynchronous API call with retry behavior."""
    response: dict[str, Any] = {"status": "error"}
    for attempt in range(retries):
        if attempt == 1:
            logger.warning("Network failure on attempt %s", attempt + 1)
            continue

        response = {"status": "ok", "payload": payload}
        break
    return response


def pretty_print_tenants(tenants: dict[str, Any]) -> None:
    """Log tenant entries in a readable way."""
    for tenant_id, tenant_data in tenants.items():
        logger.info("%s: %s", tenant_id, tenant_data)


def do_many_things(
    data: dict[str, Any],
    mode: str = "upper",
    x: int = 10,
    y: int = 20,
    z: int = 30,
) -> dict[str, str | int]:
    """Perform example transformations and an optional complex condition check."""
    numbers = [1, 2, 3, 4, 5]
    names = ["alice", "bob", "charlie", "dan"]
    output: dict[str | int, str | int] = {"data": str(data)}

    for index, number in enumerate(numbers):
        output[index] = number * number

    for name in names:
        output[name] = name.upper() if mode == "upper" else name.lower()

    if (
        x > 0
        and y > 0
        and z > 0
        and x + y + z > COMPLEX_SUM_THRESHOLD
        and x * y * z > COMPLEX_PRODUCT_THRESHOLD
        and (x - y) != 0
        and (y - z) != 0
        and (x - z) != 0
        and str(x).isdigit()
        and str(y).isdigit()
        and str(z).isdigit()
    ):
        logger.info(
            "complex condition met for values that should be validated"
            " in smaller helper functions",
        )

    example_numbers = [1, 2, 3]
    for item in example_numbers:
        logger.debug("example number: %s", item)

    l_value = 1
    o_value = 2
    i_value = 3
    if l_value + o_value + i_value > 0:
        logger.debug("ambiguous vars resolved")

    return output


def parse_amount(amount: str) -> float:
    """Parse a currency string and return a numeric amount."""
    try:
        cleaned = amount.replace("PLN", "").strip()
        return float(cleaned)
    except ValueError as exc:
        logger.warning("Failed to parse amount %r: %s", amount, exc)
        return 0.0


def dead_code_example(x: int) -> str:
    """Return a label for negative, zero, or positive values."""
    if x < 0:
        return "negative"
    if x == 0:
        return "zero"
    return "positive"


def main() -> None:
    """Run demo use cases for the rent manager."""
    logging.basicConfig(level=logging.INFO)

    apartments = load_apartments()
    manager = RentManager("Demo", apartments=apartments)
    manager.add_tenant("T1", {"name": "Jan", "rent": 2200, "utilities": 320})
    manager.add_tenant("T2", {"name": "Eva", "rent": 2800, "utilities": 410})

    bill = manager.calculate_bill("T1", 2, 2024, discount=0.1)
    logger.info("Bill: %s", bill)

    manager.mark_overdue("T1", 10)
    manager.export_summary("tmp_summary.txt")

    logger.info(
        "Results: %s",
        do_many_things({"x": 1}, mode="upper", x=12, y=25, z=30),
    )
    logger.info("Parsed amount: %s", parse_amount(" 1234.50 PLN "))


if __name__ == "__main__":
    main()
