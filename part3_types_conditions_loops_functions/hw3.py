import sys
from typing import Any

# Error messages
UNKNOWN_COMMAND_MSG = "Unknown command!"
NONPOSITIVE_VALUE_MSG = "Value must be grater than zero!"
INCORRECT_DATE_MSG = "Invalid date!"
NOT_EXISTS_CATEGORY = "Category not exists!"
OP_SUCCESS_MSG = "Added"

# Configuration constants
DATE_PARTS = 3
MONTHS_IN_YEAR = 12
FEBRUARY = 2
CAT_PARTS = 2
INCOME_ARGS = 3
COST_ARGS = 4
STATS_ARGS = 2
MIN_VAL = 0

EXPENSE_CATEGORIES = {
    "Food": ("Supermarket", "Restaurants", "FastFood", "Coffee", "Delivery"),
    "Transport": ("Taxi", "Public transport", "Gas", "Car service"),
    "Housing": ("Rent", "Utilities", "Repairs", "Furniture"),
    "Health": ("Pharmacy", "Doctors", "Dentist", "Lab tests"),
    "Entertainment": ("Movies", "Concerts", "Games", "Subscriptions"),
    "Clothing": ("Outerwear", "Casual", "Shoes", "Accessories"),
    "Education": ("Courses", "Books", "Tutors"),
    "Communications": ("Mobile", "Internet", "Subscriptions"),
    "Other": ("Miscellaneous",),
}

storage: list[dict[str, Any]] = []


def is_leap_year(year: int) -> bool:
    """Check if the year is a leap year (WPS221 fix)."""
    if year % 400 == 0:
        return True
    if year % 100 == 0:
        return False
    return year % 4 == 0


def _get_days_in_month(month: int, year: int) -> int:
    """Return the number of days in a given month."""
    if month in {1, 3, 5, 7, 8, 10, 12}:
        return 31
    if month in {4, 6, 9, 11}:
        return 30
    if month == FEBRUARY:
        return 29 if is_leap_year(year) else 28
    return 0


def extract_date(maybe_dt: str) -> tuple[int, int, int] | None:
    """Parse DD-MM-YYYY string (WPS221/MyPy fix)."""
    parts = maybe_dt.split("-")
    if len(parts) != DATE_PARTS:
        return None

    if not all(p.isdigit() for p in parts):
        return None

    # Fix: Indexing instead of passing list to int()
    day = int(parts)
    month = int(parts)
    year = int(parts)

    valid_y_m = year >= 1 and 1 <= month <= MONTHS_IN_YEAR
    if not valid_y_m:
        return None

    if 1 <= day <= _get_days_in_month(month, year):
        return day, month, year
    return None


def _parse_amount(value: str) -> float | None:
    """Safely parse amount from string."""
    try:
        amt = float(value.replace(",", "."))
        return amt if amt > MIN_VAL else None
    except ValueError:
        return None


def _is_valid_category(cat_str: str) -> bool:
    """Check if the category string is valid (Unhashable list fix)."""
    parts = cat_str.split("::")
    if len(parts) != CAT_PARTS:
        return False
    # Fix: Use strings as keys, not the 'parts' list
    parent, sub = parts, parts
    return parent in EXPENSE_CATEGORIES and sub in EXPENSE_CATEGORIES[parent]


def income_handler(amount: float, income_date: str) -> str:
    """Handle income addition."""
    dt_tuple = extract_date(income_date)
    if dt_tuple is None:
        return INCORRECT_DATE_MSG

    storage.append({"amount": amount, "date": dt_tuple})
    return OP_SUCCESS_MSG


def cost_handler(category_name: str, amount: float, cost_date: str) -> str:
    """Handle expense addition."""
    if not _is_valid_category(category_name):
        msg = cost_categories_handler()
        return f"{NOT_EXISTS_CATEGORY}\n{msg}"

    dt_tuple = extract_date(cost_date)
    if dt_tuple is None:
        return INCORRECT_DATE_MSG

    storage.append({
        "category": category_name,
        "amount": amount,
        "date": dt_tuple,
    })
    return OP_SUCCESS_MSG


def cost_categories_handler() -> str:
    """Return all available expense categories."""
    lines = []
    for main, subs in EXPENSE_CATEGORIES.items():
        for sub in subs:
            lines.append(f"{main}::{sub}")
    return "\n".join(lines)


def _calc_stats(rep_dt: tuple[int, int, int]) -> dict[str, Any]:
    """Helper to reduce variables in stats_handler (WPS210 fix)."""
    res = {"cap": 0, "inc": 0, "exp": 0, "det": {}}
    r_d, r_m, r_y = rep_dt

    for tx in storage:
        t_d, t_m, t_y = tx["date"]
        amt = tx["amount"]
        is_cost = "category" in tx

        # WPS408 fix: Correct chronological check
        if (t_y, t_m, t_d) <= (r_y, r_m, r_d):
            res["cap"] += -amt if is_cost else amt

        if t_y == r_y and t_m == r_m and t_d <= r_d:
            if is_cost:
                res["exp"] += amt
                cat = str(tx["category"])
                res["det"][cat] = res["det"].get(cat, 0) + amt
            else:
                res["inc"] += amt
    return res


def stats_handler(report_date: str) -> str:
    """Calculate financial statistics."""
    rep_dt = extract_date(report_date)
    if not rep_dt:
        return INCORRECT_DATE_MSG

    data = _calc_stats(rep_dt)
    return _format_stats_output(report_date, data)


def _format_stats_output(date_str: str, data: dict[str, Any]) -> str:
    """Format final output string (WPS210 fix)."""
    diff = data["inc"] - data["exp"]
    res_type = "profit" if diff >= 0 else "loss"
    lines = [
        f"Your statistics as of {date_str}:",
        f"Total capital: {data['cap']:.2f} rubles",
        f"This month, the {res_type} amounted to {abs(diff):.2f} rubles.",
        f"Income: {data['inc']:.2f} rubles",
        f"Expenses: {data['exp']:.2f} rubles",
        "",
        "Details (category: amount):",
    ]
    for idx, cat in enumerate(sorted(data["det"].keys()), 1):
        amt = data["det"][cat]
        val = f"{int(amt)}" if amt.is_integer() else f"{amt:.2f}"
        lines.append(f"{idx}. {cat}: {val}")
    return "\n".join(lines)


def _process_command(command: str) -> str:
    """Main command router (WPS212/WPS231 fix)."""
    parts = command.strip().split()
    if not parts:
        return UNKNOWN_COMMAND_MSG

    cmd = parts
    res = UNKNOWN_COMMAND_MSG

    if cmd == "income" and len(parts) == INCOME_ARGS:
        amt = _parse_amount(parts)
        res = income_handler(amt, parts) if amt else NONPOSITIVE_VALUE_MSG
    elif cmd == "cost":
        if len(parts) == 2 and parts == "categories":
            res = cost_categories_handler()
        elif len(parts) == COST_ARGS:
            amt = _parse_amount(parts)
            res = cost_handler(parts, amt, parts) if amt else NONPOSITIVE_VALUE_MSG
    elif cmd == "stats" and len(parts) == STATS_ARGS:
        res = stats_handler(parts)

    return res


def main() -> None:
    """Entry point."""
    for line in sys.stdin:
        clean = line.strip()
        if clean:
            print(_process_command(clean))


if __name__ == "__main__":
    main()
