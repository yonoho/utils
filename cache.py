import inspect
import json as json
from functools import wraps
from hashlib import md5


def cache_json(func, key_prefix='', expire=0, expire_at='', redis_client=None):
    """key_prefix is optional.
       if use, it should be unique at module level within the redis db,
       __module__ & func_name & all arguments would also be part of the key.

    redis_client: it's thread safe.
    to avoid giving `redis_client` param every time, you could do this:
        from functools import partial
        from somewhere import my_redis_client

        cache_json = partial(cache_json, redis_client=my_redis_client)
    """
    @wraps(func)
    def wrapped(_use_cache=True, *args, **kwargs):
        """set _use_cache to False if you do not want to use cache on this call.
        """
        if _use_cache:
            call_args = inspect.getcallargs(func, *args, **kwargs)
            func_code = inspect.getsource(func)
            args_hash = md5(json.dumps(call_args, sort_keys=True).encode()).hexdigest()
            key = key_prefix + func.__module__ + func.__name__ + args_hash
            cached = redis_client.get(key)
            if cached is None:
                ret = func(*args, **kwargs)
                redis_client[key] = json.dumps(ret)
            else:
                ret = json.loads(cached)
            return ret
        else:
            return func(*args, **kwargs)
    return wrapped


def release_cache(func):
    return
