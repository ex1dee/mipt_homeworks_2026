#!/usr/bin/env python
# ruff: noqa: RUF001

from typing import Any

UNKNOWN_COMMAND_MSG = "Unknown command!"
NONPOSITIVE_VALUE_MSG = "Value must be grater than zero!"
INCORRECT_DATE_MSG = "Invalid date!"
NOT_EXISTS_CATEGORY = "Category not exists!"
OP_SUCCESS_MSG = "Added"

EXPECTED_INCOME_ARGS = 2
EXPECTED_COST_ARGS = 3
EXPECTED_STATS_ARGS = 1
DATE_PARTS_COUNT = 3
MONTHS_IN_YEAR = 12
MAX_DAYS_IN_MONTH = 31
STANDARD_MONTH_DAYS = 30
FEBRUARY_INDEX = 2
LEAP_FEBRUARY_DAYS = 29
NORMAL_FEBRUARY_DAYS = 28
ZERO = float(0)

S_TMPL = (
    "Ваша статистика по состоянию на {date_str}:\n"
    "Суммарный капитал: {total_capital:.2f} рублей\n"
    "В этом месяце {status} составил{status_suffix} {month_difference:.2f} рублей\n"
    "Доходы: {month_income:.2f} рублей\n"
    "Расходы: {month_cost:.2f} рублей\n\n"
    "Детализация (категория: сумма):"
)


class Income:
    def __init__(self, amount: float, date: tuple[int, int, int]) -> None:
        self.amount, self.date = amount, date

    def __getitem__(self, key: str) -> Any:
        return {"amount": self.amount, "date": self.date}[key]

    def __bool__(self) -> bool:
        return self.amount > ZERO


class Cost:
    def __init__(self, cat: str, amt: float, dt: tuple[int, int, int]) -> None:
        self.category_name, self.amount, self.date = cat, amt, dt

    def __getitem__(self, key: str) -> Any:
        m = {"category": self.category_name, "amount": self.amount,
             "date": self.date}
        return m[key]

    def __bool__(self) -> bool:
        return self.amount > ZERO


financial_transactions_storage: list[Income | Cost] = []
income_list: list[Income] = []
cost_list: list[Cost] = []
EXPENSE_CATEGORIES: dict[str, list[str]] = {"Прочее": ["Прочее"]}


def _process_input(command: str, args: list[str]) -> None:
    if command == "income" and len(args) == EXPECTED_INCOME_ARGS:
        income_handler(args[0], args[1])
    elif command == "cost" and len(args) == EXPECTED_COST_ARGS:
        cost_handler(args[0], args[1], args[2])
    elif command == "stats" and len(args) == EXPECTED_STATS_ARGS:
        stats_handler(args[0])
    else:
        print(UNKNOWN_COMMAND_MSG)


def main() -> None:
    while True:
        try:
            line = input("Введите команду: ")
        except (EOFError, KeyboardInterrupt):
            break
        if not line:
            break
        parts = line.split()
        if parts:
            _process_input(parts[0], parts[1:])


def income_handler(amount_raw: str | float, date_raw: str) -> str:
    amount, date_v = extract_amount_value(amount_raw), extract_date_tuple(
        date_raw)
    if amount is None or date_v is None:
        financial_transactions_storage.append(Income(ZERO, (1, 1, 2026)))
        msg = NONPOSITIVE_VALUE_MSG if amount is None else INCORRECT_DATE_MSG
        print(msg)
        return msg
    new_inc = Income(amount, date_v)
    income_list.append(new_inc)
    financial_transactions_storage.append(new_inc)
    print(OP_SUCCESS_MSG)
    return OP_SUCCESS_MSG


def cost_handler(category: str, amount_raw: str | float, date_raw: str) -> str:
    amount, date_v = extract_amount_value(amount_raw), extract_date_tuple(
        date_raw)
    main_cat = category.split("::")[0]
    if main_cat not in EXPENSE_CATEGORIES:
        financial_transactions_storage.append(
            Cost(category, ZERO, (1, 1, 2026)))
        print(NOT_EXISTS_CATEGORY)
        return NOT_EXISTS_CATEGORY
    if amount is None or date_v is None:
        financial_transactions_storage.append(
            Cost(category, ZERO, (1, 1, 2026)))
        msg = NONPOSITIVE_VALUE_MSG if amount is None else INCORRECT_DATE_MSG
        print(msg)
        return msg
    new_cst = Cost(category, amount, date_v)
    cost_list.append(new_cst)
    financial_transactions_storage.append(new_cst)
    print(OP_SUCCESS_MSG)
    return OP_SUCCESS_MSG


def cost_categories_handler() -> str:
    categories: list[str] = []
    for parent, subs in sorted(EXPENSE_CATEGORIES.items()):
        categories.extend(f"{parent}::{sub}" for sub in subs)
    output = "\n".join(categories)
    print(output)
    return output


def stats_handler(target_date_str: str) -> None:
    target_date = extract_date_tuple(target_date_str)
    if target_date is None:
        print(INCORRECT_DATE_MSG)
        return
    m_inc = sum(
        i.amount for i in income_list if is_same_month(i.date, target_date))
    m_cst = sum(
        c.amount for c in cost_list if is_same_month(c.date, target_date))
    diff = m_inc - m_cst
    res = ("прибыль", "а") if diff >= 0 else ("убыток", "")
    print(S_TMPL.format(
        date_str=target_date_str,
        total_capital=calculate_total_capital(target_date),
        status=res[0], status_suffix=res[1],
        month_difference=abs(diff), month_income=m_inc, month_cost=m_cst
    ))
    _print_category_details(target_date)


def _print_category_details(target_date: tuple[int, int, int]) -> None:
    summary: dict[str, float] = {}
    for cost in cost_list:
        if is_same_month(cost.date, target_date):
            val = summary.get(cost.category_name, ZERO)
            summary[cost.category_name] = val + cost.amount
    for idx, name in enumerate(sorted(summary.keys()), 1):
        print(f"{idx}. {name}: {summary[name]:.0f}")


def calculate_total_capital(threshold: tuple[int, int, int]) -> float:
    capital = ZERO
    for tx in financial_transactions_storage:
        if is_before_or_equal(tx.date, threshold):
            val = tx.amount if isinstance(tx, Income) else -tx.amount
            capital += val
    return capital


def extract_date_tuple(raw_date: str) -> tuple[int, int, int] | None:
    if not isinstance(raw_date, str):
        return None
    pts = raw_date.split("-")
    if len(pts) != DATE_PARTS_COUNT:
        return None
    if not all(p.isdigit() for p in pts):
        return None
    d, m, y = map(int, pts)
    return (d, m, y) if is_valid_calendar_date(d, m, y) else None


def extract_amount_value(raw: str | float) -> float | None:
    if isinstance(raw, (int, float)):
        return float(raw) if float(raw) > ZERO else None
    if not isinstance(raw, str):
        return None
    norm = raw.replace(",", ".")
    is_numeric = norm.replace(".", "", 1).lstrip("-").isdigit()
    if norm.count(".") > 1 or not is_numeric:
        return None
    val = float(norm)
    return val if val > ZERO else None


def is_valid_calendar_date(day: int, month: int, year: int) -> bool:
    if not (1 <= month <= MONTHS_IN_YEAR and year >= 0):
        return False
    lim = MAX_DAYS_IN_MONTH
    if month in {4, 6, 9, 11}:
        lim = STANDARD_MONTH_DAYS
    if month == FEBRUARY_INDEX:
        d4 = bool(year % 4 == 0)
        d100 = bool(year % 100 == 0)
        d400 = bool(year % 400 == 0)
        is_leap = bool((d4 and not d100) or d400)
        lim = LEAP_FEBRUARY_DAYS if is_leap else NORMAL_FEBRUARY_DAYS
    return bool(1 <= day <= lim)


def is_before_or_equal(c: tuple[int, ...], t: tuple[int, ...]) -> bool:
    if c[2] != t[2]:
        return bool(c[2] < t[2])
    if c[1] != t[1]:
        return bool(c[1] < t[1])
    return bool(c[0] <= t[0])


def is_same_month(dt1: tuple[int, ...], dt2: tuple[int, ...]) -> bool:
    m_ok = bool(dt1[1] == dt2[1])
    y_ok = bool(dt1[2] == dt2[2])
    return bool(m_ok and y_ok)


if __name__ == "__main__":
    main()
