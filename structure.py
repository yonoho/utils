# -*- coding: utf-8 -*-
import json
import datetime
from copy import deepcopy
from numbers import Number


class Storage(dict):
    """
    A Storage object is like a dictionary except `obj.foo` can be used in addition to `obj['foo']`.
        >>> o = storage(a=1)
        >>> o.a
        1
        >>> o['a']
        1
        >>> o.a = 2
        >>> o['a']
        2
        >>> del o.a
        >>> o.a
        Traceback (most recent call last):
            ...
        AttributeError: 'a'
    """

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError as k:
            raise AttributeError(k)

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, key):
        try:
            del self[key]
        except KeyError as k:
            raise AttributeError(k)

    def __repr__(self):
        return '<Storage ' + dict.__repr__(self) + '>'


def recursive_json_loads(data):
    """
    将 json 字符串迭代处理为 Python 对象
        >>> a = '[{"foo": 1}]'
        >>> b = recursive_json_loads(a)
        >>> b[0].foo
        >>> 1
    """
    if isinstance(data, list):
        return [recursive_json_loads(i) for i in data]
    elif isinstance(data, tuple):
        return tuple([recursive_json_loads(i) for i in data])
    elif isinstance(data, dict):
        return Storage({recursive_json_loads(k): recursive_json_loads(data[k]) for k in data.keys()})
    else:
        try:
            obj = json.loads(data)
            if obj == data:
                return data
            return recursive_json_loads(obj)
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
        >>> data
        {'a': 1,
         'b': 2,
         'c': 3}
        >>> map_rulls
        {'a': 'x',
         'c': 1}
        >>> dict_project(data, map_rulls)
        {'x': 1,
         'c': 3}
    """
    if isinstance(data, dict):
        data = Storage({map_rulls[k] if isinstance(map_rulls[k], basestring) else k: data[k] for k in data if k in map_rulls})
    elif isinstance(data, (list, tuple)):
        return [dict_project(o, map_rulls) for o in data]
    else:
        raise ValueError('无法处理对象: %s' % str(data))
    return data
