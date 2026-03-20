#!/usr/bin/env python
# ruff: noqa: RUF001

def main() -> None:
    while True:
        line = input("Введите команду: ")
        if not line:
            break

        input_parts = line.split()
        if not input_parts:
            continue

        match input_parts:
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

    def __getitem__(self, item: int | str) -> float | tuple[
        int, int, int] | None:
        if item in {0, "amount"}:
            return self.amount
        if item in {1, "date"}:
            return self.date
        return None


class Cost:
    def __init__(self, category_name: str, amount: float,
        date: tuple[int, int, int]) -> None:
        self.category_name: str = category_name
        self.amount: float = amount
        self.date: tuple[int, int, int] = date

    def __getitem__(self, item: int | str) -> str | float | tuple[
        int, int, int] | None:
        if item in {0, "category_name"}:
            return self.category_name
        if item in {1, "amount"}:
            return self.amount
        if item in {2, "date"}:
            return self.date
        return None


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


def income_handler(amount_input: str | float, date_input: str) -> str:
    extracted_amount = extract_amount(str(amount_input))
    extracted_date = extract_date(date_input)

    if extracted_amount is None:
        print(NONPOSITIVE_VALUE_MSG)
        return NONPOSITIVE_VALUE_MSG
    if extracted_date is None:
        print(INCORRECT_DATE_MSG)
        return INCORRECT_DATE_MSG

    financial_transactions_storage.append(
        Income(extracted_amount, extracted_date))

    print(OP_SUCCESS_MSG)
    return OP_SUCCESS_MSG


def cost_handler(category_name: str, amount_input: str | float,
    date_input: str) -> str:
    extracted_amount = extract_amount(str(amount_input))
    extracted_date = extract_date(date_input)

    if len(category_name) == 0 or any(char in category_name for char in ".,"):
        print(NOT_EXISTS_CATEGORY)
        return NOT_EXISTS_CATEGORY

    if extracted_amount is None:
        print(NONPOSITIVE_VALUE_MSG)
        return NONPOSITIVE_VALUE_MSG

    if extracted_date is None:
        print(INCORRECT_DATE_MSG)
        return INCORRECT_DATE_MSG

    if category_name not in EXPENSE_CATEGORIES:
        EXPENSE_CATEGORIES[category_name] = category_name

    financial_transactions_storage.append(
        Cost(category_name, extracted_amount, extracted_date))

    print(OP_SUCCESS_MSG)
    return OP_SUCCESS_MSG


def cost_categories_handler() -> dict[str, str] | str:
    sorted_categories = sorted(EXPENSE_CATEGORIES.keys())
    for index, category in enumerate(sorted_categories, 1):
        print(f"{index}. {category}")
    return EXPENSE_CATEGORIES


def stats_handler(date_input: str) -> None:
    date_value = extract_date(date_input)
    if date_value is None:
        print(INCORRECT_DATE_MSG)
        return

    income_list: list[Income] = [transaction for transaction in
                                 financial_transactions_storage if
                                 isinstance(transaction, Income)]
    cost_list: list[Cost] = [transaction for transaction in
                             financial_transactions_storage if
                             isinstance(transaction, Cost)]

    total_capital = count_total_capital(date_value, income_list, cost_list)

    monthly_income_amounts = [income.amount for income in income_list if
                              is_same_month(income.date, date_value)]
    monthly_cost_amounts = [cost.amount for cost in cost_list if
                            is_same_month(cost.date, date_value)]

    total_monthly_income = sum(monthly_income_amounts)
    total_monthly_cost = sum(monthly_cost_amounts)
    monthly_difference = total_monthly_income - total_monthly_cost

    status_text = "прибыль" if monthly_difference >= 0 else "убыток"
    status_suffix_text = "а" if monthly_difference >= 0 else ""

    print(stats_template.format(
        date=date_input,
        total_capital=total_capital,
        status=status_text,
        status_suffix=status_suffix_text,
        month_diff=abs(monthly_difference),
        month_income=total_monthly_income,
        month_cost=total_monthly_cost
    ))

    current_month_costs = [cost for cost in cost_list if
                           is_same_month(cost.date, date_value)]
    categories_sum_map = get_categories_map(current_month_costs)

    for index, category in enumerate(sorted(categories_sum_map.keys()), 1):
        print(f"{index}. {category}: {categories_sum_map[category]:.0f}")


def get_categories_map(costs: list[Cost]) -> dict[str, float]:
    result_map: dict[str, float] = {}
    for cost in costs:
        result_map[cost.category_name] = result_map.get(cost.category_name,
                                                        0.0) + cost.amount
    return result_map


def count_total_capital(threshold_date: tuple[int, int, int],
    income_list: list[Income],
    cost_list: list[Cost]) -> float:
    total_income = sum(income.amount for income in income_list if
                       is_date_before_or_equal(income.date, threshold_date))
    total_cost = sum(cost.amount for cost in cost_list if
                     is_date_before_or_equal(cost.date, threshold_date))
    return total_income - total_cost


def extract_date(date_string: str) -> tuple[int, int, int] | None:
    expected_date_parts_count = 3
    date_parts = date_string.split("-")

    if len(date_parts) != expected_date_parts_count or not all(
        part.isdigit() for part in date_parts):
        return None

    day, month, year = map(int, date_parts)
    if is_valid_date(day, month, year):
        return day, month, year

    return None


def extract_amount(amount_string: str) -> float | None:
    normalized_amount = amount_string.replace(",", ".")
    if normalized_amount.count(".") > 1:
        return None

    if not normalized_amount.replace(".", "", 1).isdigit():
        return None

    value = float(normalized_amount)
    return value if value > 0 else None


def is_valid_date(day: int, month: int, year: int) -> bool:
    if day < 1 or day > Dates.max_day_in_month or \
        month < 1 or month > Dates.months_in_year or year < 0:
        return False

    if month in Dates.months_with_thirty_days and day > Dates.max_day_in_short_month:
        return False

    if month == Dates.february_month:
        is_leap = (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)
        return day <= (
            Dates.february_leap_days if is_leap else Dates.february_days)

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
