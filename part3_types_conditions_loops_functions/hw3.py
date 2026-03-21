#!/usr/bin/env python

from typing import Any

UNKNOWN_COMMAND_MSG = "Unknown command!"
NONPOSITIVE_VALUE_MSG = "Value must be grater than zero!"
INCORRECT_DATE_MSG = "Invalid date!"
NOT_EXISTS_CATEGORY = "Category not exists!"
OP_SUCCESS_MSG = "Added"

EXPENSE_CATEGORIES = {
    "Food": ("Supermarket", "Restaurants", "FastFood", "Coffee", "Delivery"),
    "Transport": ("Taxi", "Public transport", "Gas", "Car service"),
    "Housing": ("Rent", "Utilities", "Repairs", "Furniture"),
    "Health": ("Pharmacy", "Doctors", "Dentist", "Lab tests"),
    "Entertainment": ("Movies", "Concerts", "Games", "Subscriptions"),
    "Clothing": ("Outerwear", "Casual", "Shoes", "Accessories"),
    "Education": ("Courses", "Books", "Tutors"),
    "Communications": ("Mobile", "Internet", "Subscriptions"),
    "Other": (),
}

financial_transactions_storage: list[dict[str, Any]] = []


def is_leap_year(year: int) -> bool:
    """
    Для заданного года определяет: високосный (True) или невисокосный (False).

    :param int year: Проверяемый год
    :return: Значение високосности.
    :rtype: bool
    """
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def _get_days_in_month(month: int, year: int) -> int:
    """Возвращает количество дней в месяце с учетом високосного года."""
    if month in (1, 3, 5, 7, 8, 10, 12):
        return 31
    if month in (4, 6, 9, 11):
        return 30
    if month == 2:
        return 29 if is_leap_year(year) else 28
    return 0


def extract_date(maybe_dt: str) -> tuple[int, int, int] | None:
    """
    Парсит дату формата DD-MM-YYYY из строки.

    :param str maybe_dt: Проверяемая строка
    :return: tuple формата (день, месяц, год) или None, если дата неправильная.
    :rtype: tuple[int, int, int] | None
    """
    parts = maybe_dt.split("-")
    if len(parts) != 3:
        return None

    for part in parts:
        if not part.isdigit():
            return None

    day = int(parts)
    month = int(parts)
    year = int(parts)

    if year < 1 or month < 1 or month > 12:
        return None

    if day < 1 or day > _get_days_in_month(month, year):
        return None

    return day, month, year


def _parse_amount(value: str) -> float | None:
    """Парсит сумму (целое или дробное), поддерживая точку и запятую."""
    clean_val = value.replace(",", ".")
    check_val = clean_val
    if check_val.startswith("-"):
        check_val = check_val[1:]

    if check_val.count(".") > 1:
        return None

    if not check_val.replace(".", "").isdigit():
        return None

    return float(clean_val)


def _is_valid_category(cat_str: str) -> bool:
    """Проверяет валидность переданной категории."""
    parts = cat_str.split("::")
    if len(parts) != 2:
        return False
    common, target = parts, parts
    if common not in EXPENSE_CATEGORIES:
        return False
    return target in EXPENSE_CATEGORIES[common]


def income_handler(amount: float, income_date: str) -> str:
    financial_transactions_storage.append(
        {"amount": amount, "date": income_date},
    )
    return OP_SUCCESS_MSG


def cost_handler(category_name: str, amount: float, income_date: str) -> str:
    financial_transactions_storage.append(
        {"category": category_name, "amount": amount, "date": income_date},
    )
    return OP_SUCCESS_MSG


def cost_categories_handler() -> str:
    return "\n".join(
        f"{main_cat}::{sub_cat}"
        for main_cat, sub_cats in EXPENSE_CATEGORIES.items()
        for sub_cat in sub_cats
    )


def _is_before_or_equal(tx_dt: tuple[int, int, int], rep_dt: tuple[int, int, int]) -> bool:
    """Сравнивает даты, чтобы учесть исторические транзакции для капитала."""
    tx_d, tx_m, tx_y = tx_dt
    rep_d, rep_m, rep_y = rep_dt
    if tx_y < rep_y:
        return True
    if tx_y == rep_y and tx_m < rep_m:
        return True
    return tx_y == rep_y and tx_m == rep_m and tx_d <= rep_d


def _is_same_month_and_before_or_equal(
    tx_dt: tuple[int, int, int],
    rep_dt: tuple[int, int, int],
) -> bool:
    """Проверяет, что транзакция была в том же месяце и до указанного дня включительно."""
    tx_d, tx_m, tx_y = tx_dt
    rep_d, rep_m, rep_y = rep_dt
    return tx_y == rep_y and tx_m == rep_m and tx_d <= rep_d


def stats_handler(report_date: str) -> str:
    rep_dt = extract_date(report_date)
    if not rep_dt:
        return INCORRECT_DATE_MSG

    total_capital = 0.0
    month_income = 0.0
    month_expenses = 0.0
    month_details: dict[str, float] = {}

    for tx in financial_transactions_storage:
        tx_dt = extract_date(str(tx.get("date", "")))
        if not tx_dt:
            continue

        amt = float(tx.get("amount", 0.0))
        is_cost = "category" in tx

        # Считаем исторический капитал
        if _is_before_or_equal(tx_dt, rep_dt):
            if is_cost:
                total_capital -= amt
            else:
                total_capital += amt

        # Считаем статистику текущего месяца
        if _is_same_month_and_before_or_equal(tx_dt, rep_dt):
            if is_cost:
                month_expenses += amt
                cat = str(tx["category"]).split("::")
                month_details[cat] = month_details.get(cat, 0.0) + amt
            else:
                month_income += amt

    return _format_stats_output(
        report_date, total_capital, month_income, month_expenses, month_details
    )


def _format_stats_output(
    report_date: str,
    total_capital: float,
    month_income: float,
    month_expenses: float,
    month_details: dict[str, float],
) -> str:
    """Форматирует вывод статистики в соответствии с требованиями."""
    lines = [
        f"Your statistics as of {report_date}:",
        f"Total capital: {total_capital:.2f} rubles",
    ]

    monthly_diff = month_income - month_expenses
    if monthly_diff >= 0:
        lines.append(f"This month, the profit amounted to {monthly_diff:.2f} rubles.")
    else:
        lines.append(f"This month, the loss amounted to {abs(monthly_diff):.2f} rubles.")

    lines.extend([
        f"Income: {month_income:.2f} rubles",
        f"Expenses: {month_expenses:.2f} rubles",
        "",
        "Details (category: amount):",
    ])

    for index, cat in enumerate(sorted(month_details.keys()), start=1):
        amt = month_details[cat]
        # Вывод целого числа без .0 (согласно примерам)
        amt_str = str(int(amt)) if amt.is_integer() else str(amt)
        lines.append(f"{index}. {cat}: {amt_str}")

    return "\n".join(lines)


def _handle_income_command(parts: list[str]) -> str:
    """Обработка команды income."""
    if len(parts) != 3:
        return UNKNOWN_COMMAND_MSG
    amt = _parse_amount(parts)
    if amt is None or amt <= 0:
        return NONPOSITIVE_VALUE_MSG
    dt = extract_date(parts)
    if dt is None:
        return INCORRECT_DATE_MSG
    return income_handler(amt, parts)


def _handle_cost_command(parts: list[str]) -> str:
    """Обработка команды cost."""
    if len(parts) == 2 and parts == "categories":
        return cost_categories_handler()
    if len(parts) != 4:
        return UNKNOWN_COMMAND_MSG

    cat_str = parts
    if not _is_valid_category(cat_str):
        return f"{NOT_EXISTS_CATEGORY}\n{cost_categories_handler()}"

    amt = _parse_amount(parts)
    if amt is None or amt <= 0:
        return NONPOSITIVE_VALUE_MSG

    dt = extract_date(parts)
    if dt is None:
        return INCORRECT_DATE_MSG

    return cost_handler(cat_str, amt, parts)


def _handle_stats_command(parts: list[str]) -> str:
    """Обработка команды stats."""
    if len(parts) != 2:
        return UNKNOWN_COMMAND_MSG
    dt = extract_date(parts)
    if dt is None:
        return INCORRECT_DATE_MSG
    return stats_handler(parts)


def _process_command(command: str) -> str:
    """Основной маршрутизатор команд."""
    parts = command.strip().split()
    if not parts:
        return UNKNOWN_COMMAND_MSG

    cmd = parts
    if cmd == "income":
        return _handle_income_command(parts)
    if cmd == "cost":
        return _handle_cost_command(parts)
    if cmd == "stats":
        return _handle_stats_command(parts)

    return UNKNOWN_COMMAND_MSG


def main() -> None:
    """
    Ваш код здесь.
    Читаем из стандартного потока ввода без вызова исключений и импорта sys.
    """
    with open(0) as stdin_stream:
        for line in stdin_stream:
            clean_line = line.strip()
            if clean_line:
                print(_process_command(clean_line))


if __name__ == "__main__":
    main()