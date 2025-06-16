from typing import Callable, TypeVar


T = TypeVar("T")


def lazy_task(builder: Callable[[], T]):
    cache = None

    def wrapper() -> T:
        nonlocal cache
        if cache is not None:
            return cache

        cache = builder()
        return cache

    return wrapper
