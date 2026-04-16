import json
from datetime import UTC, datetime
from functools import wraps
from typing import Any, ParamSpec, Protocol, TypeVar, cast
from urllib.request import urlopen

INVALID_CRITICAL_COUNT = "Breaker count must be positive integer!"
INVALID_RECOVERY_TIME = "Breaker recovery time must be positive integer!"
VALIDATIONS_FAILED = "Invalid decorator args."
TOO_MUCH = "Too much requests, just wait."

P = ParamSpec("P")
R_co = TypeVar("R_co", covariant=True)


class CallableWithMeta(Protocol[P, R_co]):
    __name__: str
    __module__: str

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R_co: ...


class BreakerError(Exception):
    def __init__(self, message: str, func_name: str, block_time: datetime) -> None:
        super().__init__(message)

        self.func_name = func_name
        self.block_time = block_time


class CircuitBreaker:
    def __init__(
        self,
        critical_count: int = 5,
        time_to_recover: int = 30,
        triggers_on: type[Exception] = Exception,
    ):
        self.__validate_init_data(critical_count, time_to_recover)

        self.critical_count = critical_count
        self.time_to_recover = time_to_recover
        self.triggers_on = triggers_on

        self.errors_counter = 0
        self.last_blocked_at: datetime | None = None

    def __call__(self, func: CallableWithMeta[P, R_co]) -> CallableWithMeta[P, R_co]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R_co:
            now = self.__get_datetime_now()

            if self.errors_counter >= self.critical_count and self.last_blocked_at:
                time_since_block = (now - self.last_blocked_at).total_seconds()

                if time_since_block < self.time_to_recover:
                    raise self.__get_breaker_error(func)

            try:
                result = func(*args, **kwargs)
            except self.triggers_on as error:
                self.errors_counter += 1

                if self.errors_counter >= self.critical_count:
                    self.last_blocked_at = now
                    raise self.__get_breaker_error(func) from error

                raise

            self.last_blocked_at = None
            self.errors_counter = 0

            return result

        return cast("CallableWithMeta[P, R_co]", cast("object", wrapper))

    def __get_breaker_error(self, func: CallableWithMeta[P, R_co]) -> BreakerError:
        func_name = f"{func.__module__}.{func.__name__}"
        block_time = self.last_blocked_at or self.__get_datetime_now()
        return BreakerError(TOO_MUCH, func_name, block_time)

    @staticmethod
    def __get_datetime_now() -> datetime:
        return datetime.now(UTC)

    @staticmethod
    def __validate_init_data(critical_count: int, time_to_recover: int) -> None:
        errors = []

        if not isinstance(critical_count, int) or critical_count <= 0:
            errors.append(ValueError(INVALID_CRITICAL_COUNT))
        if not isinstance(time_to_recover, int) or time_to_recover <= 0:
            errors.append(ValueError(INVALID_RECOVERY_TIME))

        if errors:
            raise ExceptionGroup(VALIDATIONS_FAILED, errors)


circuit_breaker = CircuitBreaker(5, 30, Exception)


# @circuit_breaker
def get_comments(post_id: int) -> Any:
    """
    Получает комментарии к посту

    Args:
        post_id (int): Идентификатор поста

    Returns:
        list[dict[int | str]]: Список комментариев
    """
    response = urlopen(f"https://jsonplaceholder.typicode.com/comments?postId={post_id}")
    return json.loads(response.read())


if __name__ == "__main__":
    comments = get_comments(1)
