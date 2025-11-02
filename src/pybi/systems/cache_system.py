from functools import wraps


def instance_cache(func):
    cache_name = f"_cache_{func.__name__}"

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if not hasattr(self, cache_name):
            setattr(self, cache_name, {})
        cache = getattr(self, cache_name)

        try:
            key = (args, frozenset(kwargs.items()))
        except TypeError:
            return func(self, *args, **kwargs)

        if key not in cache:
            cache[key] = func(self, *args, **kwargs)
        return cache[key]

    return wrapper
