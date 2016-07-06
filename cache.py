import json as json


def cache_json(func, key_prefix='', expire=0, expire_at='', redis_client=None):
    """key_prefix should be unique at module level within the redis db,
    func name & all arguments would also be part of the key.

    redis_client: it's thread safe.
    to avoid giving `redis_client` param every time, you could do this:
        from functools import partial
        from somewhere import my_redis_client

        cache_json = partial(cache_json, redis_client=my_redis_client)
    """
    def wrapped(_use_cache=True, *args, **kwargs):
        if _use_cache:
            return
        else:
            ret = func(*args, **kwargs)
            return ret
    return wrapped
