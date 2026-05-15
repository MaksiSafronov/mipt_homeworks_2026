import json
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from functools import wraps
from typing import Any, NoReturn, ParamSpec, TypeVar
from urllib.request import urlopen

INVALID_CRITICAL_COUNT = "Breaker count must be positive integer!"
INVALID_RECOVERY_TIME = "Breaker recovery time must be positive integer!"
VALIDATIONS_FAILED = "Invalid decorator args."
TOO_MUCH = "Too much requests, just wait."
BLOCK_TIME_NOT_SET = "Block time must be set when breaker is open."


P = ParamSpec("P")
R_co = TypeVar("R_co", covariant=True)


class BreakerError(Exception):
    def __init__(self, func_name: str, block_time: datetime, message: str = TOO_MUCH) -> None:
        super().__init__(message)
        self.func_name = func_name
        self.block_time = block_time


def _is_positive_int(number: int) -> bool:
    return isinstance(number, int) and not isinstance(number, bool) and number > 0


def _collect_validation_errors(critical_count: int, time_to_recover: int) -> list[ValueError]:
    validation_errors: list[ValueError] = []
    if not _is_positive_int(critical_count):
        validation_errors.append(ValueError(INVALID_CRITICAL_COUNT))
    if not _is_positive_int(time_to_recover):
        validation_errors.append(ValueError(INVALID_RECOVERY_TIME))
    return validation_errors


class CircuitBreaker:
    def __init__(
        self,
        critical_count: int = 5,
        time_to_recover: int = 30,
        triggers_on: type[Exception] = Exception,
    ) -> None:
        errors = _collect_validation_errors(critical_count, time_to_recover)
        if errors:
            raise ExceptionGroup(VALIDATIONS_FAILED, errors)

        self._critical_count = critical_count
        self._time_to_recover = time_to_recover
        self._triggers_on = triggers_on
        self._errors_count = 0
        self._blocked_at: datetime | None = None

    def __call__(self, func: Callable[P, R_co]) -> Callable[P, R_co]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R_co:
            now_utc = datetime.now(UTC)
            self._try_to_recover(now_utc)
            if self._is_blocked():
                self._raise_blocked_error(func)

            try:
                result = func(*args, **kwargs)
            except Exception as error:
                if self._should_open_breaker(error, now_utc):
                    self._raise_blocked_error(func, source=error)
                raise

            self._reset_state()
            return result

        return wrapper

    def _reset_state(self) -> None:
        self._errors_count = 0
        self._blocked_at = None

    def _is_blocked(self) -> bool:
        return self._blocked_at is not None

    def _try_to_recover(self, now_utc: datetime) -> None:
        if self._blocked_at is None:
            return
        unblock_time = self._blocked_at + timedelta(seconds=self._time_to_recover)
        if now_utc >= unblock_time:
            self._reset_state()

    def _raise_blocked_error(self, func: Callable[P, R_co], source: Exception | None = None) -> NoReturn:
        if self._blocked_at is None:
            raise RuntimeError(BLOCK_TIME_NOT_SET)

        module_name = getattr(func, "__module__", "__main__")
        function_name = getattr(func, "__name__", func.__class__.__name__)
        full_name = f"{module_name}.{function_name}"

        if source is None:
            raise BreakerError(full_name, self._blocked_at)

        raise BreakerError(full_name, self._blocked_at) from source

    def _should_open_breaker(self, error: Exception, now_utc: datetime) -> bool:
        if not isinstance(error, self._triggers_on):
            return False

        self._errors_count += 1
        if self._errors_count < self._critical_count:
            return False

        self._blocked_at = now_utc
        return True


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
