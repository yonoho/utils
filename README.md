# utils
Utility in web/common development

to run module doctest, use the `$ python -m utils.transform` command. btw, this command should be run outside the project directory.


# redis_lock

copyed from `git@github.com:ionelmc/python-redis-lock.git`

Modified origin's `acquire` and `__enter__` methods, make it possible to use `timeout` param in `with` statement.(While the origin usage of with statement shall no longer work.)

    from utils.redis_lock import Lock

    lock = Lock(StrictRedis(), 'name-of-the-lock', expire=5, auto_renewal=True)

    with lock.acquire(timeout=3):
        pass
