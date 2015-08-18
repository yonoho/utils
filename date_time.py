# -*- coding: utf-8 -*-
import time
import datetime
import re
from numbers import Number

try:
    basestring
except NameError:
    basestring = str

__all__ = [
    'transtime',
]

DT_PATTERN = re.compile('^((?P<year>\d{4})-(?P<month>\d{1,2})-(?P<day>\d{1,2}))?(?P<sep> |T)?((?P<hour>\d{1,2}):(?P<minute>\d{1,2})(:(?P<second>\d{1,2}))?)?(\.(?P<microsecond>\d{1,6}))?$')


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

    >>> transtime('2010-01-01', 'date')
    datetime.date(2010, 1, 1)

    >>> transtime('09:00:01', 'time')
    datetime.time(9, 0, 1)

    >>> transtime('09:00', 'time')
    datetime.time(9, 0)

    >>> transtime('2010-01-01 09:00:00', 'datetime')
    datetime.datetime(2010, 1, 1, 9, 0)

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
        elif to_type == 'date':
            to_type = datetime.date
        elif to_type == 'time':
            to_type = datetime.time
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
    elif isinstance(from_obj, (str, basestring)):
        match = re.match(DT_PATTERN, from_obj)
        if not match:
            raise ValueError('Unknown from_obj format:%s' % from_obj)
        dt_dict = match.groupdict()
        sep = dt_dict.pop('sep')
        dt_dict.update({k: int(v) for k, v in dt_dict.items() if v})
        if sep:
            return datetime.datetime(**{k: v for k, v in dt_dict.items() if v})
        elif dt_dict['day']:
            return datetime.date(**{k: dt_dict[k] for k in ('year', 'month', 'day') if dt_dict[k]})
        elif dt_dict['hour']:
            return datetime.time(**{k: dt_dict[k] for k in ('hour', 'minute', 'second', 'microsecond') if dt_dict[k]})
        else:
            raise ValueError('Unable to parse the datetime string:%s' % from_obj)
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
