#!/usr/bin/env python3
import sys
from typing import Any, Final

# Константы сообщений
UNKNOWN_COMMAND_MSG: Final = "Unknown command!"
NONPOSITIVE_VALUE_MSG: Final = "Value must be grater than zero!"
INCORRECT_DATE_MSG: Final = "Invalid date!"
NOT_EXISTS_CATEGORY: Final = "Category not exists!"
OP_SUCCESS_MSG: Final = "Added"

# Параметры команд
INCOME_CMD_PARTS: Final = 3
COST_CMD_PARTS: Final = 4
STATS_CMD_PARTS: Final = 2
COST_CATEGORIES_CMD_PARTS: Final = 2

# Параметры даты и валидации
MIN_VAL: Final = 0
MIN_DAY: Final = 1
MIN_MONTH: Final = 1
MAX_MONTH: Final = 12
DATE_PARTS_COUNT: Final = 3
DAY_TEXT_LEN: Final = 2
MONTH_TEXT_LEN: Final = 2
YEAR_TEXT_LEN: Final = 4
FEBRUARY: Final = 2
MONTHS_WITH_THIRTY_DAYS: Final = (4, 6, 9, 11)
CATEGORY_PARTS_COUNT: Final = 2

# Ключи хранилища
KIND_KEY: Final = "kind"
AMOUNT_KEY: Final = "amount"
DATE_KEY: Final = "date"
CATEGORY_KEY: Final = "category"

DateTuple = tuple[int, int, int]
StorageRecord = dict[str, Any]
StatsData = tuple[float, float, float, dict[str, float]]

EXPENSE_CATEGORIES: Final = {
    "Food": ("Supermarket", "Restaurants", "FastFood", "Coffee", "Delivery"),
    "Transport": ("Taxi", "Public transport", "Gas", "Car service"),
    "Housing": ("Rent", "Utilities", "Repairs", "Furniture"),
    "Health": ("Pharmacy", "Doctors", "Dentist", "Lab tests"),
    "Entertainment": ("Movies", "Concerts", "Games", "Subscriptions"),
    "Clothing": ("Outerwear", "Casual", "Shoes", "Accessories"),
    "Education": ("Courses", "Books", "Tutors"),
    "Communications": ("Mobile", "Internet", "Subscriptions"),
    "Other": ("Other",),
}

financial_transactions_storage: list[StorageRecord] = []


def is_leap_year(year: int) -> bool:
    """Определяет, является ли год високосным."""
    if year % 400 == 0:
        return True
    if year % 100 == 0:
        return False
    return year % 4 == 0


def get_days_in_month(month: int, year: int) -> int:
    """Возвращает количество дней в месяце."""
    if month in MONTHS_WITH_THIRTY_DAYS:
        return 30
    if month == FEBRUARY:
        return 29 if is_leap_year(year) else 28
    return 31


def extract_date(maybe_dt: str) -> DateTuple | None:
    """Парсит DD-MM-YYYY в кортеж (день, месяц, год)."""
    parts = maybe_dt.split("-")
    if len(parts) != DATE_PARTS_COUNT:
        return None

    d_txt, m_txt, y_txt = parts, parts, parts

    if not (len(d_txt) == DAY_TEXT_LEN and len(m_txt) == MONTH_TEXT_LEN and len(y_txt) == YEAR_TEXT_LEN):
        return None
    if not (d_txt.isdigit() and m_txt.isdigit() and y_txt.isdigit()):
        return None

    day, month, year = int(d_txt), int(m_txt), int(y_txt)

    if month < MIN_MONTH or month > MAX_MONTH or day < MIN_DAY:
        return None
    if day > get_days_in_month(month, year):
        return None

    return day, month, year


def parse_amount(raw_amount: str) -> float | None:
    """Преобразует строку в положительное число float."""
    normalized = raw_amount.replace(",", ".")
    try:
        amt = float(normalized)
    except ValueError:
        return None
    else:
        return amt if amt > MIN_VAL else None


def add_invalid_transaction() -> None:
    """Добавляет пустую запись для сохранения индексов (нужно для тестов)."""
    financial_transactions_storage.append({})


def is_valid_category(category_name: str) -> bool:
    """Проверяет существование категории."""
    if "::" not in category_name:
        return False
    parts = category_name.split("::")
    if len(parts) != CATEGORY_PARTS_COUNT:
        return False
    parent, sub = parts, parts
    return parent in EXPENSE_CATEGORIES and sub in EXPENSE_CATEGORIES[parent]


def income_handler(amount: float, income_date: str) -> str:
    """Регистрирует доход."""
    parsed_date = extract_date(income_date)
    if amount <= MIN_VAL:
        add_invalid_transaction()
        return NONPOSITIVE_VALUE_MSG
    if parsed_date is None:
        add_invalid_transaction()
        return INCORRECT_DATE_MSG

    financial_transactions_storage.append({
        KIND_KEY: "income",
        AMOUNT_KEY: amount,
        DATE_KEY: parsed_date,
    })
    return OP_SUCCESS_MSG


def cost_handler(category_name: str, amount: float, cost_date: str) -> str:
    """Регистрирует расход."""
    parsed_date = extract_date(cost_date)
    if amount <= MIN_VAL:
        add_invalid_transaction()
        return NONPOSITIVE_VALUE_MSG
    if parsed_date is None:
        add_invalid_transaction()
        return INCORRECT_DATE_MSG
    if not is_valid_category(category_name):
        add_invalid_transaction()
        return NOT_EXISTS_CATEGORY

    financial_transactions_storage.append({
        KIND_KEY: "cost",
        CATEGORY_KEY: category_name,
        AMOUNT_KEY: amount,
        DATE_KEY: parsed_date,
    })
    return OP_SUCCESS_MSG


def cost_categories_handler() -> str:
    """Формирует список всех категорий."""
    lines: list[str] = []
    for parent, subs in EXPENSE_CATEGORIES.items():
        lines.extend(f"{parent}::{sub}" for sub in subs)
    return "\n".join(lines)


def _is_relevant(tx_date: DateTuple, report_date: DateTuple) -> bool:
    """Проверяет, что транзакция не позже даты отчета."""
    return (tx_date, tx_date, tx_date) <= (report_date, report_date, report_date)


def _is_current_month(tx_date: DateTuple, report_date: DateTuple) -> bool:
    """Проверяет, относится ли транзакция к месяцу отчета."""
    return tx_date == report_date and tx_date == report_date and tx_date <= report_date


def stats_handler(report_date: str) -> str:
    """Обработка команды stats."""
    rep_dt = extract_date(report_date)
    if rep_dt is None:
        return INCORRECT_DATE_MSG

    total_cap = 0.0
    m_inc = 0.0
    m_exp = 0.0
    m_cats: dict[str, float] = {}

    for tx in financial_transactions_storage:
        if not tx or DATE_KEY not in tx:
            continue
        t_dt = tx[DATE_KEY]
        if not _is_relevant(t_dt, rep_dt):
            continue

        amt = tx[AMOUNT_KEY]
        is_cost = tx.get(KIND_KEY) == "cost"
        total_cap += -amt if is_cost else amt

        if _is_current_month(t_dt, rep_dt):
            if is_cost:
                m_exp += amt
                cat_sub = tx[CATEGORY_KEY].split("::")
                m_cats[cat_sub] = m_cats.get(cat_sub, 0.0) + amt
            else:
                m_inc += amt

    return _format_report(report_date, (total_cap, m_inc, m_exp, m_cats))


def _format_report(report_date: str, data: StatsData) -> str:
    """Вспомогательная функция для сборки текста отчета."""
    cap, inc, exp, cats = data
    diff = inc - exp
    res_type = "profit" if diff >= 0 else "loss"
    
    # Исправление -0.00
    diff_text = f"{abs(diff):.2f}"
    cap_text = f"{cap:.2f}"
    if cap_text == "-0.00":
        cap_text = "0.00"

    lines = [
        f"Your statistics as of {report_date}:",
        f"Total capital: {cap_text} rubles",
        f"This month, the {res_type} amounted to {diff_text} rubles.",
        f"Income: {inc:.2f} rubles",
        f"Expenses: {exp:.2f} rubles",
        "",
        "Details (category: amount):",
    ]
    for idx, name in enumerate(sorted(cats.keys()), 1):
        val = cats[name]
        val_str = f"{int(val)}" if val.is_integer() else f"{val:.2f}"
        lines.append(f"{idx}. {name}: {val_str}")
    return "\n".join(lines)


def process_command(raw_line: str) -> str:
    """Роутер команд."""
    parts = raw_line.strip().split()
    if not parts:
        return ""
    
    cmd = parts
    if cmd == "income" and len(parts) == INCOME_CMD_PARTS:
        amt = parse_amount(parts)
        return income_handler(amt, parts) if amt else NONPOSITIVE_VALUE_MSG
    
    if cmd == "cost":
        if len(parts) == COST_CATEGORIES_CMD_PARTS and parts == "categories":
            return cost_categories_handler()
        if len(parts) == COST_CMD_PARTS:
            amt = parse_amount(parts)
            if not amt:
                return NONPOSITIVE_VALUE_MSG
            res = cost_handler(parts, amt, parts)
            return f"{res}\n{cost_categories_handler()}" if res == NOT_EXISTS_CATEGORY else res

    if cmd == "stats" and len(parts) == STATS_CMD_PARTS:
        return stats_handler(parts)

    return UNKNOWN_COMMAND_MSG


def main() -> None:
    """Точка входа."""
    for line in sys.stdin:
        result = process_command(line)
        if result:
            print(result)


if __name__ == "__main__":
    main()
