# -*- coding: utf-8 -*-
import json
import datetime
from copy import deepcopy
from numbers import Number

from .structure import Storage

__all__ = [
    'recursively_json_loads',
    'model2dict',
    'dict_project',
    'group_by_attr',
    'traversal_generator',
    'check_bin',
    'update_bin',
]


def recursively_json_loads(data):
    """
    将 json 字符串迭代处理为 Python 对象
        >>> a = '[{"foo": 1}]'
        >>> b = recursively_json_loads(a)
        >>> b[0].foo
        >>> 1
    """
    if isinstance(data, list):
        return [recursively_json_loads(i) for i in data]
    elif isinstance(data, tuple):
        return tuple([recursively_json_loads(i) for i in data])
    elif isinstance(data, dict):
        return Storage({recursively_json_loads(k): recursively_json_loads(data[k]) for k in data.keys()})
    else:
        try:
            obj = json.loads(data)
            if obj == data:
                return data
            return recursively_json_loads(obj)
        except:
            return data


def model2dict(model, datetime_format=None):
    """
    本函数用于使对象可 json 序列化，且返回的字典都是新的（deepcopy）
    """
    if isinstance(model, dict):
        model = Storage(deepcopy(model))
        to_pop = []
        for k in model:
            # 过滤
            if isinstance(k, basestring) and (k.startswith('_') or k.isupper()):
                to_pop.append(k)
                continue
            # 转换
            elif isinstance(model[k], datetime.datetime):
                model[k] = model[k].strftime(datetime_format) if datetime_format else model[k].isoformat(' ')
            # 递归
            else:
                model[k] = model2dict(model[k], datetime_format)
        for k in to_pop:
            model.pop(k)
        return model
    elif hasattr(model, '__dict__') and not isinstance(model, Number):
        return model2dict(model.__dict__, datetime_format)
    elif isinstance(model, (list, tuple)):
        return [model2dict(m, datetime_format) for m in model]
    else:
        return model


def dict_project(data, map_rulls={}):
    """
    字典投影，支持取 data 的子集和改名。只想投影而不想改名的，写个 1 就行，eg：
        >>> data = {
                'a': 'value of a',
                'b': 'value of b',
                'c': 'value of c',
            }
        >>> map_rulls = {
                'a': 'x',
                'c': 1
            }
        >>> dict_project(data, map_rulls)
        {
            'x': 'value of a',
            'c': 'value of c'
        }
    """
    if isinstance(data, dict):
        data = Storage({map_rulls[k] if isinstance(map_rulls[k], basestring) else k: data[k] for k in data if k in map_rulls})
    elif isinstance(data, (list, tuple)):
        return [dict_project(o, map_rulls) for o in data]
    else:
        raise ValueError('无法处理对象: %s' % str(data))
    return data


def group_by_attr(obj_list, attr):
    """
    按属性分组，返回以属性值为键，以 obj list 为值的字典
    """
    groups = {}
    for obj in obj_list:
        attr_value = getattr(obj, attr, None)
        groups[attr_value] = groups.get(attr_value, []) + [obj]
    return groups


def traversal_generator(*iterables):
    """
    通过返回一个 generator, 可以从 n 个 iterables 中轮流取元素，保证取完
    """
    iterables = [i if hasattr(i, 'next') else iter(i) for i in iterables]
    done = False
    while not done:
        done = True
        for i in range(len(iterables)):
            try:
                yield next(iterables[i])
                done = False
            except StopIteration:
                pass
    return


def check_bin(number, index):
    """
    用于某些二进制标志位的场景
    返回一个 int 类型变量的某一二进制位的值，index 从 1 开始，即
    >>> check_bin(2, 1)
    >>> 0
    >>> check_bin(2, 2)
    >>> 1
    """
    try:
        return bin(number)[2:][-index]
    except IndexError:
        return 0


def update_bin(number, index, value):
    """
    用于某些二进制标志位的场景
    将一个 int 类型变量的二进制数的第 index 位，置为 value 并返回新变量，如
    >>> update_bin(2, 2, 0)
    >>> 0
    >>> update_bin(2, 3, 1)
    >>> 6
    """
    if value:
        return number | int('1' + '0'*(index-1), 2)
    else:
        return number & int('0' + '1'*(index-1), 2)
