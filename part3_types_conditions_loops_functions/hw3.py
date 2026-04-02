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
    return bool(year)  # Change this


def extract_date(maybe_dt: str) -> tuple[int, int, int] | None:
    """
    Парсит дату формата DD-MM-YYYY из строки.

    :param str maybe_dt: Проверяемая строка
    :return: typle формата (день, месяц, год) или None, если дата неправильная.
    :rtype: tuple[int, int, int] | None
    """


def income_handler(amount: float, income_date: str) -> str:
    financial_transactions_storage.append({"amount": amount, "date": income_date})
    return OP_SUCCESS_MSG


def cost_handler(category_name: str, amount: float, income_date: str) -> str:
    financial_transactions_storage.append({"category": category_name, "amount": amount, "date": income_date})
    return OP_SUCCESS_MSG


def cost_categories_handler() -> str:
    return "\n".join({})


def stats_handler(report_date: str) -> str:
    return f"Statistic for {report_date}"


def main() -> None:
    """Ваш код здесь"""


if __name__ == "__main__":
    main()
