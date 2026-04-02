#!/usr/bin/env python

from typing import Any

UNKNOWN_COMMAND_MSG = "Unknown command!"
NONPOSITIVE_VALUE_MSG = "Value must be grater than zero!"
INCORRECT_DATE_MSG = "Invalid date!"
NOT_EXISTS_CATEGORY = "Category not exists!"
OP_SUCCESS_MSG = "Added"

NUM_IN_DATA = 3
MONTH_CNT = 12
FEB_NUM = 2
LEN_OTHER_OF_YEAR = 2
LEN_YEAR = 4
LEN_CATEGORY = 2
COST_CMD_LEN = 4
THIRTY_DAY_MONTHS = (4, 6, 9, 11)
DATE_PART_LENGTHS = (LEN_OTHER_OF_YEAR, LEN_OTHER_OF_YEAR, LEN_YEAR)
CATEGORY_SEPARATOR = "::"
MINUS_SIGN = "-"
DECIMAL_POINT = "."
AMOUNT_KEY = "amount"
DATE_KEY = "date"
CATEGORY_KEY = "category"
CAPITAL_KEY = "capital"
INCOME_KEY = "income"
EXPENSES_KEY = "expenses"
CATEGORIES_KEY = "categories"

EXPENSE_CATEGORIES = {
    "Food": ("Supermarket", "Restaurants", "FastFood", "Coffee", "Delivery"),
    "Transport": ("Taxi", "Public transport", "Gas", "Car service"),
    "Housing": ("Rent", "Utilities", "Repairs", "Furniture"),
    "Health": ("Pharmacy", "Doctors", "Dentist", "Lab tests"),
    "Entertainment": ("Movies", "Concerts", "Games", "Subscriptions"),
    "Clothing": ("Outerwear", "Casual", "Shoes", "Accessories"),
    "Education": ("Courses", "Books", "Tutors"),
    "Communications": ("Mobile", "Internet", "Subscriptions"),
    "Other": ("SomeCategory", "SomeOtherCategory"),
}

Date = tuple[int, int, int]
AmountParts = tuple[str, str, int]

financial_transactions_storage: list[dict[str, Any]] = []


def is_leap_year(year: int) -> bool:
    """
    Для заданного года определяет: високосный (True) или невисокосный (False).

    :param int year: Проверяемый год
    :return: Значение високосности.
    :rtype: bool
    """
    if year % 400 == 0:
        return True
    if year % 100 == 0:
        return False
    return year % 4 == 0


def has_valid_date_lengths(parts: list[str]) -> bool:
    return (
        len(parts[0]) == DATE_PART_LENGTHS[0]
        and len(parts[1]) == DATE_PART_LENGTHS[1]
        and len(parts[2]) == DATE_PART_LENGTHS[2]
    )


def get_max_day(month: int, year: int) -> int:
    if month == FEB_NUM:
        return 29 if is_leap_year(year) else 28
    if month in THIRTY_DAY_MONTHS:
        return 30
    return 31


def extract_date(maybe_dt: str) -> Date | None:
    """
    Парсит дату формата DD-MM-YYYY из строки.

    :param str maybe_dt: Проверяемая строка
    :return: typle формата (день, месяц, год) или None, если дата неправильная.
    :rtype: Date | None
    """
    parts = maybe_dt.split(MINUS_SIGN)
    if len(parts) != NUM_IN_DATA or not has_valid_date_lengths(parts):
        return None
    if not all(part and part.isdigit() for part in parts):
        return None

    day = int(parts[0])
    month = int(parts[1])
    year = int(parts[2])
    if month < 1 or month > MONTH_CNT or day < 1:
        return None
    if day > get_max_day(month, year):
        return None
    return day, month, year


def income_handler(amount: float, income_date: str) -> str:
    date = extract_date(income_date)
    if amount <= 0:
        financial_transactions_storage.append({})
        return NONPOSITIVE_VALUE_MSG
    if date is None:
        financial_transactions_storage.append({})
        return INCORRECT_DATE_MSG
    financial_transactions_storage.append({AMOUNT_KEY: amount, DATE_KEY: date})
    return OP_SUCCESS_MSG


def get_expense_categories() -> dict[str, tuple[str, ...]]:
    return dict(EXPENSE_CATEGORIES)


def is_category_exist(category: str) -> bool:
    parts = category.split(CATEGORY_SEPARATOR)
    categories = get_expense_categories()
    if len(parts) != LEN_CATEGORY:
        return False
    main_category, sub_category = parts
    return main_category in categories and sub_category in categories[main_category]


def cost_handler(category_name: str, amount: float, income_date: str) -> str:
    date = extract_date(income_date)
    status = OP_SUCCESS_MSG

    if not is_category_exist(category_name):
        status = NOT_EXISTS_CATEGORY
    elif amount <= 0:
        status = NONPOSITIVE_VALUE_MSG
    elif date is None:
        status = INCORRECT_DATE_MSG

    if status == OP_SUCCESS_MSG:
        financial_transactions_storage.append(
            {CATEGORY_KEY: category_name, AMOUNT_KEY: amount, DATE_KEY: date},
        )
    else:
        financial_transactions_storage.append({})
    return status


def cost_categories_handler() -> str:
    categories: list[str] = []
    for main_category, sub_categories in EXPENSE_CATEGORIES.items():
        categories.extend(
            f"{main_category}{CATEGORY_SEPARATOR}{sub_category}"
            for sub_category in sub_categories
        )
    return "\n".join(categories)


def stats_handler(report_date: str) -> str:
    return f"Statistic for {report_date}"


def main() -> None:
    """Ваш код здесь"""


if __name__ == "__main__":
    main()
