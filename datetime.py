# -*- coding: utf-8 -*-
import datetime
import time
from numbers import Number

__all__ = [
    'transtime',
]


def transtime(from_type, to_type, format=None):
    """
    时间格式转换
    支持的 type 类型:
        - datetime.datetime
        - datetime.timedelta
        - Number(时间戳, 秒)
        - str
    """
    if isinstance(from_type, datetime.datetime):
        pass
    elif isinstance(from_type, str):
        pass
    elif isinstance(from_type, datetime.timedelta):
        pass
    elif isinstance(from_type, Number):
        pass
    raise NotImplementedError
    return
