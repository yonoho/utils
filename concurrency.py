# -*- coding: utf-8 -*-
try:
    import gevent
    from flask import copy_current_request_context
except ImportError:
    gevent = None
    copyright = None


def i_have_a_dream(func, *args, **kwargs):
    """
    Flask 异步任务处理。本函数会立即返回，并使用 gevent 的新线程执行 func 函数（带上下文）。
    """
    return gevent.spawn(copy_current_request_context(func), *args, **kwargs)
