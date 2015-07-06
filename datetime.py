# -*- coding: utf-8 -*-
import datetime
import re
from numbers import Number

__all__ = [
    'transtime',
]

RE_FORMAT = {
    re.compile('^%d{4}-%d{1,2}-%d{1,2} %d{1,2}:%d{1,2}:%d{1,2}$'): '%Y-%m-%d %H:%M:%S',
    re.compile('^%d{4}-%d{1,2}-%d{1,2} %d{1,2}:%d{1,2}:%d{1,2}\.%d{6}$'): '%Y-%m-%d %H:%M:%S.%f',
    re.compile('^%d{4}-%d{1,2}-%d{1,2}T%d{1,2}:%d{1,2}:%d{1,2}\.%d{6}$'): '%Y-%m-%dT%H:%M:%S.%f',
}


def check_format(dt_str):
    """
    简单尝试判断 format
    """
    for pattern in RE_FORMAT:
        if re.match(pattern, dt_str):
            return RE_FORMAT[pattern]


def transtime(from_obj, to_type, dt_format=None):
    """
    时间格式转换
    支持的 obj/type 类型:
        - datetime.datetime
        - datetime.timedelta
        - Number(时间戳/时间段, 单位秒)
        - str
    """
    if isinstance(from_obj, datetime.datetime):
        pass
    elif isinstance(from_obj, str):
        dt_format = dt_format or check_format()
        if not dt_format:
            raise ValueError('no datetime format provided.')
        pass
    elif isinstance(from_obj, datetime.timedelta):
        pass
    elif isinstance(from_obj, Number):
        pass
    else:
        raise ValueError('Unsupported data type: %s' % str(type(from_obj)))
    raise NotImplementedError
    return
