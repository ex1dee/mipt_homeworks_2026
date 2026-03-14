#!/usr/bin/env python
# ruff: noqa: T201, RUF001


class Messages:
  unknown_command = "Неизвестная команда!"
  nonpositive_value = "Значение должно быть больше нуля!"
  incorrect_category_name = (
    "Имя категории должно быть одним словом без точек и запятых"
  )
  incorrect_date = "Неправильная дата!"
  op_success = "Добавлено"
  stats_template = """Ваша статистика по состоянию на {date}:
Суммарный капитал: {total_capital:.2f} рублей
В этом месяце {status} составил{status_suffix} {month_diff:.2f} рублей
Доходы: {month_income:.2f} рублей
Расходы: {month_cost:.2f} рублей

Детализация (категория: сумма):"""


class Commands:
  income = "income"
  cost = "cost"
  stats = "stats"


class Dates:
  months_with_thirty_one_days = (1, 3, 5, 7, 8, 10, 12)
  months_with_thirty_days = (4, 6, 9, 11)
  february_month = 2
  max_day_in_month = 31
  max_day_in_short_month = 30
  months_in_year = 12
  february_leap_days = 29
  february_days = 28


class Income:
  amount: float
  date: tuple[int, int, int]

  def __init__(self, amount: float, date: tuple[int, int, int]) -> None:
    self.amount = amount
    self.date = date


class Cost:
  category_name: str
  amount: float
  date: tuple[int, int, int]

  def __init__(self, category_name: str, amount: float,
      date: tuple[int, int, int]) -> None:
    self.category_name = category_name
    self.amount = amount
    self.date = date


def main() -> None:
  income_list: list[Income] = []
  cost_list: list[Cost] = []

  while True:
    inp = input("Введите команду: ")
    parse_input(inp, income_list, cost_list)


def parse_input(inp: str, income_list: list[Income], cost_list: list[Cost]) -> None:
  command_parts = inp.split()
  if len(command_parts) == 0:
    return

  command = command_parts[0]
  args = command_parts[1:]

  match command:
    case Commands.income:
      handle_income(args, income_list)
    case Commands.cost:
      handle_cost(args, cost_list)
    case Commands.stats:
      handle_stats(args, income_list, cost_list)
    case _:
      print(Messages.unknown_command)


def handle_income(args: list[str], income_list: list[Income]) -> None:
  income_args_count = 2
  if len(args) != income_args_count:
    print(Messages.unknown_command)
    return

  amount_str, date_str = args
  extracted_date = extract_date(date_str)
  extracted_amount = extract_amount(amount_str)

  if extracted_amount is None:
    print(Messages.nonpositive_value)
    return

  if extracted_date is None:
    print(Messages.incorrect_date)
    return

  income_list.append(Income(extracted_amount, extracted_date))
  print(Messages.op_success)


def handle_cost(args: list[str], cost_list: list[Cost]) -> None:
  cost_args_count = 3
  if len(args) != cost_args_count:
    print(Messages.unknown_command)
    return

  category_name, amount_str, date_str = args
  extracted_date = extract_date(date_str)
  extracted_amount = extract_amount(amount_str)

  if len(category_name) == 0 or any(char in category_name for char in ".,"):
    print(Messages.incorrect_category_name)
    return

  if extracted_amount is None:
    print(Messages.nonpositive_value)
    return

  if extracted_date is None:
    print(Messages.incorrect_date)
    return

  cost_list.append(Cost(category_name, extracted_amount, extracted_date))
  print(Messages.op_success)


def handle_stats(args: list[str], income_list: list[Income],
    cost_list: list[Cost]) -> None:
  stats_args_count = 1
  if len(args) != stats_args_count:
    print(Messages.unknown_command)
    return

  date_str = args[0]
  date_val = extract_date(date_str)

  if date_val is None:
    print(Messages.incorrect_date)
    return

  total_capital = count_total_capital(date_val, income_list, cost_list)

  month_income = [income.amount for income in income_list if
                  is_same_month(income.date, date_val)]
  month_cost = [cost.amount for cost in cost_list if
                is_same_month(cost.date, date_val)]
  month_diff = sum(month_income) - sum(month_cost)

  if month_diff >= 0:
    status_text = "прибыль"
    status_suffix_text = "а"
  else:
    status_text = "убыток"
    status_suffix_text = ""

  print(Messages.stats_template.format(
      date=date_str,
      total_capital=total_capital,
      status=status_text,
      status_suffix=status_suffix_text,
      month_diff=abs(month_diff),
      month_income=sum(month_income),
      month_cost=sum(month_cost)
  ))

  categories_sum = get_categories_map(
      [cost for cost in cost_list if is_same_month(cost.date, date_val)])
  sorted_categories = sorted(categories_sum.keys())

  for index, category in enumerate(sorted_categories, 1):
    category_sum = categories_sum[category]
    print(f"{index}. {category}: {category_sum:.0f}")


def get_categories_map(costs: list[Cost]) -> dict[str, float]:
  categories_sum: dict[str, float] = {}

  for cost in costs:
    category = cost.category_name
    amount = cost.amount
    categories_sum[category] = categories_sum.get(category, 0.0) + amount

  return categories_sum


def count_total_capital(threshold: tuple[int, int, int],
    income_list: list[Income],
    cost_list: list[Cost]) -> float:
  total_income = [income.amount for income in income_list if
                  is_date_before_or_equal(income.date, threshold)]
  total_cost = [cost.amount for cost in cost_list if
                is_date_before_or_equal(cost.date, threshold)]

  return sum(total_income) - sum(total_cost)


def extract_date(maybe_dt: str) -> tuple[int, int, int] | None:
  date_parts = maybe_dt.split("-")
  date_components_count = 3
  if len(date_parts) != date_components_count:
    return None

  for part in date_parts:
    if not part.isdigit():
      return None

  day, month, year = map(int, date_parts)
  if not is_valid_date(day, month, year):
    return None

  return day, month, year


def extract_amount(amount: str) -> float | None:
  normalized = amount.replace(",", ".")

  if normalized.count(".") > 1:
    return None

  if not normalized.replace(".", "", 1).isdigit():
    return None

  value = float(normalized)
  return value if value > 0 else None


def is_valid_date(day: int, month: int, year: int) -> bool:
  if day < 1 or day > Dates.max_day_in_month or \
      month < 1 or month > Dates.months_in_year or year < 0:
    return False

  if month in Dates.months_with_thirty_days and day > Dates.max_day_in_short_month:
    return False

  if month == Dates.february_month:
    max_feb_day = Dates.february_leap_days if is_leap_year(year) \
      else Dates.february_days
    return day <= max_feb_day

  return True


def is_date_before_or_equal(current: tuple[int, int, int],
    threshold: tuple[int, int, int]) -> bool:
  return (current[2], current[1], current[0]) <= (threshold[2], threshold[1],
                                                  threshold[0])


def is_same_month(first_date: tuple[int, int, int],
    second_date: tuple[int, int, int]) -> bool:
  return first_date[1] == second_date[1] and first_date[2] == second_date[2]


def is_leap_year(year: int) -> bool:
  leap_divisor = 4
  century_divisor = 100
  quad_century_divisor = 400
  return (year % leap_divisor == 0 and year % century_divisor != 0) or \
    (year % quad_century_divisor == 0)


if __name__ == "__main__":
  main()
