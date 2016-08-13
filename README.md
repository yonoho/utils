# utils
Utility in web/common development

to run module doctest, use the `$ python -m utils.transform` command. btw, this command should be run outside the project directory.


# redis_lock

copyed from `git@github.com:ionelmc/python-redis-lock.git`

Modified origin's `acquire` and `__enter__` methods, make it possible to use `timeout` param in `with` statement.(While the origin usage of with statement shall no longer work.)

    from utils.redis_lock import Lock

    lock = Lock(StrictRedis(), 'name-of-the-lock', expire=5)

    with lock.acquire(timeout=3):
        # this with statement will block up to 3 seconds before raise a NotAcquired error,
        # and the codes below will not have the chance to run.
        print('successfully acquired the lock witin 3 seconds.')
        print('And the lock will exprire in 5 seconds.')
