# -*- coding: utf-8 -*-
import time
import datetime
import re
from numbers import Number

__all__ = [
    'check_format',
    'transtime',
]

RE_FORMAT = {
    re.compile('^\d{2}-\d{1,2}-\d{1,2}$'): '%Y-%m-%d',
    re.compile('^\d{4}-\d{1,2}-\d{1,2}$'): '%Y-%m-%d',
    re.compile('\d{1,2}:\d{1,2}:\d{1,2}$'): '%H:%M:%S',
    re.compile('\d{1,2}:\d{1,2}$'): '%H:%M',
    re.compile('^\d{4}-\d{1,2}-\d{1,2} \d{1,2}:\d{1,2}:\d{1,2}$'): '%Y-%m-%d %H:%M:%S',
    re.compile('^\d{4}-\d{1,2}-\d{1,2} \d{1,2}:\d{1,2}:\d{1,2}\.\d{6}$'): '%Y-%m-%d %H:%M:%S.%f',
    re.compile('^\d{4}-\d{1,2}-\d{1,2}T\d{1,2}:\d{1,2}:\d{1,2}\.\d{6}$'): '%Y-%m-%dT%H:%M:%S.%f',
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
    to_type 也可以是以上类型的字符串名字

    >>> import datetime
    >>> dt = datetime.datetime(2010, 1, 1, 10, 10, 10, 555)
    >>> transtime(dt, str)
    '2010-01-01 10:10:10.000555'

    >>> transtime(dt, str, '%Y-%m-%d %H:%M:%S')
    '2010-01-01 10:10:10'

    >>> transtime(transtime(dt, str), datetime.datetime)
    datetime.datetime(2010, 1, 1, 10, 10, 10, 555)

    >>> transtime(dt, float)
    1262311810.555

    >>> transtime(1262311810.555, 'datetime')
    datetime.datetime(2010, 1, 1, 10, 10, 10, 555000)

    >>> transtime(1262311810.555, str)
    '2010-01-01 10:10:10.555000'

    >>> transtime(90000, 'timedelta')
    datetime.timedelta(1, 3600)

    >>> transtime(datetime.timedelta(days=1, hours=1), float)
    90000.0
    """
    # 参数兼容
    if isinstance(to_type, str):
        if to_type == 'datetime':
            to_type = datetime.datetime
        elif to_type == 'timedelta':
            to_type = datetime.timedelta
        elif to_type == 'timestamp':
            to_type = float
        elif to_type == 'str':
            to_type = str
    # 转换逻辑
    if isinstance(from_obj, to_type):
        return from_obj
    elif isinstance(from_obj, datetime.datetime):
        if issubclass(to_type, Number):  # datetime -> timestamp
            return to_type(time.mktime(from_obj.timetuple()) + from_obj.microsecond/1000.0)
        elif to_type == str:  # datetime -> str
            return from_obj.strftime(dt_format) if dt_format else from_obj.isoformat(' ')
        else:
            raise TypeError('Unsupported to_type: %s' % str(to_type))
    elif isinstance(from_obj, str):
        dt_format = dt_format or check_format(from_obj)
        if not dt_format:
            raise ValueError('no datetime format provided.')
        return transtime(datetime.datetime.strptime(from_obj, dt_format), to_type, dt_format)
    elif isinstance(from_obj, datetime.timedelta):
        if issubclass(to_type, Number):  # timedelta -> seconds
            return to_type(from_obj.total_seconds())
        else:
            raise TypeError('Unsupported to_type: %s' % str(to_type))
    elif isinstance(from_obj, Number):
        if to_type == datetime.datetime:  # timestamp -> datetime
            return datetime.datetime.fromtimestamp(from_obj)
        elif to_type == str:  # timestamp -> str
            return transtime(transtime(from_obj, 'datetime', dt_format), to_type, dt_format)
        elif to_type == datetime.timedelta:  # timestamp -> timedelta
            return datetime.timedelta(seconds=from_obj)
    else:
        raise TypeError('Unsupported from_obj type: %s' % str(type(from_obj)))


if __name__ == '__main__':
    import doctest
    doctest.testmod(verbose=True)
