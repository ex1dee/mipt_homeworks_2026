#!/usr/bin/env python
# ruff: noqa: T201, RUF001

def main() -> None:
    while True:
        line = input("Введите команду: ")
        if not line:
            break

        inp = line.split()
        if not inp:
            continue

        match inp:
            case ["income", amount, date]:
                income_handler(amount, date)
            case ["cost", category, amount, date]:
                cost_handler(category, amount, date)
            case ["stats", date]:
                stats_handler(date)
            case _:
                print("Неизвестная команда!")


class Income:
    def __init__(self, amount: float, date: tuple[int, int, int]) -> None:
        self.amount: float = amount
        self.date: tuple[int, int, int] = date

    def __getitem__(self, item: int) -> float | tuple[int, int, int] | None:
        if item == 0:
            return self.amount
        if item == 1:
            return self.date
        return None


class Cost:
    def __init__(self, category_name: str, amount: float,
        date: tuple[int, int, int]) -> None:
        self.category_name: str = category_name
        self.amount: float = amount
        self.date: tuple[int, int, int] = date

    def __getitem__(self, item: int) -> str | float | tuple[int, int, int]:
        if item == 0:
            return self.category_name
        if item == 1:
            return self.amount
        if item == 2:
            return self.date
        raise IndexError


financial_transactions_storage: list[Income | Cost] = []
EXPENSE_CATEGORIES: dict[str, str] = {}

INCORRECT_DATE_MSG: str = "Неправильная дата!"
NONPOSITIVE_VALUE_MSG: str = "Значение должно быть больше нуля!"
NOT_EXISTS_CATEGORY: str = "Имя категории должно быть одним словом без точек и запятых"
OP_SUCCESS_MSG: str = "Добавлено"

stats_template: str = """Ваша статистика по состоянию на {date}:
Суммарный капитал: {total_capital:.2f} рублей
В этом месяце {status} составил{status_suffix} {month_diff:.2f} рублей
Доходы: {month_income:.2f} рублей
Расходы: {month_cost:.2f} рублей

Детализация (категория: сумма):"""


class Dates:
    months_with_thirty_one_days: tuple[int, ...] = (1, 3, 5, 7, 8, 10, 12)
    months_with_thirty_days: tuple[int, ...] = (4, 6, 9, 11)
    february_month: int = 2
    max_day_in_month: int = 31
    max_day_in_short_month: int = 30
    months_in_year: int = 12
    february_leap_days: int = 29
    february_days: int = 28


def income_handler(amount_str: str | float, date_str: str) -> bool:
    extracted_amount = extract_amount(str(amount_str))
    extracted_date = extract_date(date_str)

    if extracted_amount is None:
        print(NONPOSITIVE_VALUE_MSG)
        return False
    if extracted_date is None:
        print(INCORRECT_DATE_MSG)
        return False

    financial_transactions_storage.append(
        Income(extracted_amount, extracted_date))
    print(OP_SUCCESS_MSG)
    return True


def cost_handler(category_name: str, amount_str: str | float,
    date_str: str) -> bool:
    extracted_amount = extract_amount(str(amount_str))
    extracted_date = extract_date(date_str)

    if len(category_name) == 0 or any(char in category_name for char in ".,"):
        print(NOT_EXISTS_CATEGORY)
        return False
    if extracted_amount is None:
        print(NONPOSITIVE_VALUE_MSG)
        return False
    if extracted_date is None:
        print(INCORRECT_DATE_MSG)
        return False

    if category_name not in EXPENSE_CATEGORIES:
        EXPENSE_CATEGORIES[category_name] = category_name

    financial_transactions_storage.append(
        Cost(category_name, extracted_amount, extracted_date))
    print(OP_SUCCESS_MSG)
    return True


def cost_categories_handler() -> dict[str, str]:
    for index, category in enumerate(sorted(EXPENSE_CATEGORIES.keys()), 1):
        print(f"{index}. {category}")
    return EXPENSE_CATEGORIES


def stats_handler(date_str: str) -> None:
    date_val = extract_date(date_str)
    if date_val is None:
        print(INCORRECT_DATE_MSG)
        return

    income_list: list[Income] = [t for t in financial_transactions_storage if
                                 isinstance(t, Income)]
    cost_list: list[Cost] = [t for t in financial_transactions_storage if
                             isinstance(t, Cost)]

    total_capital = count_total_capital(date_val, income_list, cost_list)

    month_income = [i.amount for i in income_list if
                    is_same_month(i.date, date_val)]
    month_cost = [c.amount for c in cost_list if
                  is_same_month(c.date, date_val)]

    total_month_income = sum(month_income)
    total_month_cost = sum(month_cost)
    month_diff = total_month_income - total_month_cost

    status_text = "прибыль" if month_diff >= 0 else "убыток"
    status_suffix_text = "а" if month_diff >= 0 else ""

    print(stats_template.format(
        date=date_str,
        total_capital=total_capital,
        status=status_text,
        status_suffix=status_suffix_text,
        month_diff=abs(month_diff),
        month_income=total_month_income,
        month_cost=total_month_cost
    ))

    current_month_costs = [c for c in cost_list if
                           is_same_month(c.date, date_val)]
    categories_sum = get_categories_map(current_month_costs)

    for index, category in enumerate(sorted(categories_sum.keys()), 1):
        print(f"{index}. {category}: {categories_sum[category]:.0f}")


def get_categories_map(costs: list[Cost]) -> dict[str, float]:
    res: dict[str, float] = {}
    for c in costs:
        res[c.category_name] = res.get(c.category_name, 0.0) + c.amount
    return res


def count_total_capital(threshold: tuple[int, int, int],
    income_list: list[Income],
    cost_list: list[Cost]) -> float:
    total_income = sum(i.amount for i in income_list if
                       is_date_before_or_equal(i.date, threshold))
    total_cost = sum(c.amount for c in cost_list if
                     is_date_before_or_equal(c.date, threshold))
    return total_income - total_cost


def extract_date(maybe_dt: str) -> tuple[int, int, int] | None:
    parts = maybe_dt.split("-")
    if len(parts) != 3 or not all(p.isdigit() for p in parts):
        return None

    day, month, year = map(int, parts)
    if is_valid_date(day, month, year):
        return day, month, year

    return None


def extract_amount(amount: str) -> float | None:
    normalized = amount.replace(",", ".")
    if normalized.count(".") > 1:
        return None

    if not normalized.replace(".", "", 1).isdigit():
        return None

    value = float(normalized)
    return value if value > 0 else None


def is_valid_date(day: int, month: int, year: int) -> bool:
    if day < 1 or day > 31 or month < 1 or month > 12 or year < 0:
        return False

    if month in Dates.months_with_thirty_days and day > 30:
        return False

    if month == 2:
        leap = (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)
        return day <= (29 if leap else 28)

    return True


def is_date_before_or_equal(current_date: tuple[int, int, int],
    threshold_date: tuple[int, int, int]) -> bool:
    return (current_date[2], current_date[1], current_date[0]) <= \
        (threshold_date[2], threshold_date[1], threshold_date[0])


def is_same_month(date_one: tuple[int, int, int],
    date_two: tuple[int, int, int]) -> bool:
    return date_one[1] == date_two[1] and date_one[2] == date_two[2]


if __name__ == "__main__":
    main()
