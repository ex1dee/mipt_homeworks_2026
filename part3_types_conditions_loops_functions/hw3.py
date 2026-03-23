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
    def __init__(self, category: str, amount: float,
                 date: tuple[int, int, int]) -> None:
        self.category_name, self.amount, self.date = category, amount, date

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


def main() -> None:
    while True:
        line = input("Введите команду: ")
        if not line:
            break

        parts = line.split()
        if parts:
            _process_input(parts[0], parts[1:])


def _process_input(command: str, args: list[str]) -> None:
    if command == "income" and len(args) == EXPECTED_INCOME_ARGS:
        income_handler(args[0], args[1])
    elif command == "cost" and len(args) == EXPECTED_COST_ARGS:
        cost_handler(args[0], args[1], args[2])
    elif command == "stats" and len(args) == EXPECTED_STATS_ARGS:
        stats_handler(args[0])
    else:
        print(UNKNOWN_COMMAND_MSG)


def income_handler(amount_raw: str | float, date_raw: str) -> str:
    amount, date = _extract_amount_value(amount_raw), _extract_date_tuple(
        date_raw)

    if amount is None or date is None:
        financial_transactions_storage.append(Income(ZERO, (1, 1, 2026)))
        msg = NONPOSITIVE_VALUE_MSG if amount is None else INCORRECT_DATE_MSG
        print(msg)
        return msg

    new_income = Income(amount, date)
    income_list.append(new_income)
    financial_transactions_storage.append(new_income)

    print(OP_SUCCESS_MSG)
    return OP_SUCCESS_MSG


def cost_handler(category: str, amount_raw: str | float, date_raw: str) -> str:
    amount, date = _extract_amount_value(amount_raw), _extract_date_tuple(
        date_raw)

    main_category = category.split("::")[0]
    if main_category not in EXPENSE_CATEGORIES:
        financial_transactions_storage.append(
            Cost(category, ZERO, (1, 1, 2026)))
        print(NOT_EXISTS_CATEGORY)
        return NOT_EXISTS_CATEGORY

    if amount is None or date is None:
        financial_transactions_storage.append(
            Cost(category, ZERO, (1, 1, 2026)))
        msg = NONPOSITIVE_VALUE_MSG if amount is None else INCORRECT_DATE_MSG
        print(msg)
        return msg

    new_cost = Cost(category, amount, date)
    cost_list.append(new_cost)
    financial_transactions_storage.append(new_cost)

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
    target_date = _extract_date_tuple(target_date_str)

    if target_date is None:
        print(INCORRECT_DATE_MSG)
        return

    month_income = sum(
        i.amount for i in income_list if _is_same_month(i.date, target_date))
    month_cost = sum(
        c.amount for c in cost_list if _is_same_month(c.date, target_date))
    month_diff = month_income - month_cost
    status_res = ("прибыль", "а") if month_diff >= 0 else ("убыток", "")

    print(S_TMPL.format(
        date_str=target_date_str,
        total_capital=_calculate_total_capital(target_date),
        status=status_res[0], status_suffix=status_res[1],
        month_difference=abs(month_diff), month_income=month_income,
        month_cost=month_cost
    ))

    _print_category_details(target_date)


def _print_category_details(target_date: tuple[int, int, int]) -> None:
    summary: dict[str, float] = {}

    for cost in cost_list:
        if _is_same_month(cost.date, target_date):
            value = summary.get(cost.category_name, ZERO)
            summary[cost.category_name] = value + cost.amount

    for index, name in enumerate(sorted(summary.keys()), 1):
        print(f"{index}. {name}: {summary[name]:.0f}")


def _calculate_total_capital(threshold: tuple[int, int, int]) -> float:
    capital = ZERO

    for transaction in financial_transactions_storage:
        if _is_before_or_equal(transaction.date, threshold):
            value = transaction.amount if isinstance(transaction,
                                                     Income) else -transaction.amount
            capital += value

    return capital


def _extract_date_tuple(raw_date: str) -> tuple[int, int, int] | None:
    if not isinstance(raw_date, str):
        return None

    parts = raw_date.split("-")

    if len(parts) != DATE_PARTS_COUNT:
        return None
    if not all(p.isdigit() for p in parts):
        return None

    date, month, year = map(int, parts)
    return (date, month, year) if _is_valid_calendar_date(date, month,
                                                          year) else None


def _extract_amount_value(raw_amount: str | float) -> float | None:
    if isinstance(raw_amount, (int, float)):
        return float(raw_amount) if float(raw_amount) > ZERO else None
    if not isinstance(raw_amount, str):
        return None

    normalized = raw_amount.replace(",", ".")
    is_numeric = normalized.replace(".", "", 1).lstrip("-").isdigit()

    if normalized.count(".") > 1 or not is_numeric:
        return None

    value = float(normalized)
    return value if value > ZERO else None


def _is_valid_calendar_date(day: int, month: int, year: int) -> bool:
    if not (1 <= month <= MONTHS_IN_YEAR and year >= 0):
        return False

    limit = MAX_DAYS_IN_MONTH

    if month in {4, 6, 9, 11}:
        limit = STANDARD_MONTH_DAYS

    if month == FEBRUARY_INDEX:
        d4 = bool(year % 4 == 0)
        d100 = bool(year % 100 == 0)
        d400 = bool(year % 400 == 0)
        is_leap = bool((d4 and not d100) or d400)
        limit = LEAP_FEBRUARY_DAYS if is_leap else NORMAL_FEBRUARY_DAYS

    return bool(1 <= day <= limit)


def _is_before_or_equal(fst_date: tuple[int, ...],
                        snd_date: tuple[int, ...]) -> bool:
    if fst_date[2] != snd_date[2]:
        return bool(fst_date[2] < snd_date[2])
    if fst_date[1] != snd_date[1]:
        return bool(fst_date[1] < snd_date[1])
    return bool(fst_date[0] <= snd_date[0])


def _is_same_month(fst_date: tuple[int, ...], snd_date: tuple[int, ...]) -> bool:
    m_ok = bool(fst_date[1] == snd_date[1])
    y_ok = bool(fst_date[2] == snd_date[2])
    return bool(m_ok and y_ok)


if __name__ == "__main__":
    main()
