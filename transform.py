# -*- coding: utf-8 -*-
import datetime
from copy import deepcopy
from numbers import Number

try:
    from pymongo import ObjectId
except ImportError:
    ObjectId = None

try:
    basestring
except NameError:
    basestring = str

__all__ = [
    'obj2dict',
    'dict_project',
    'group_by_key',
    'group_by_keys',
    'merge_dicts',
    'traversal_generator',
    'check_bin',
    'update_bin',
    'filter_bin',
]


def obj2dict(obj, datetime_format=None):
    """
    本函数用于使对象可 json 序列化，且返回的字典都是新的（deepcopy）
    """
    # iter collection
    if isinstance(obj, dict):
        return {obj2dict(k, datetime_format): obj2dict(v, datetime_format) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [obj2dict(m, datetime_format) for m in obj]
    # json seriable
    elif isinstance(obj, datetime.datetime):
        return obj.strftime(datetime_format) if datetime_format else obj.isoformat(' ')
    elif isinstance(obj, datetime.date):
        return obj.strftime(datetime_format) if datetime_format else obj.isoformat()
    elif isinstance(obj, datetime.time):
        return obj.strftime(datetime_format) if datetime_format else obj.isoformat()
    elif isinstance(obj, ObjectId):
        return str(obj)
    # object -> dict
    elif hasattr(obj, '__dict__') and not isinstance(obj, Number):
        obj_json = deepcopy(obj.__dict__)
        to_pop = []
        for k in obj_json:
            if isinstance(k, basestring) and (k.startswith('_') or k.isupper()):
                to_pop.append(k)
        for k in to_pop:
            obj_json.pop(k)
        return obj2dict(obj_json, datetime_format)
    else:
        return obj


def dict_project(data, map_rules={}):
    """
    字典投影，支持取 data 的子集和改名。只想投影而不想改名的，写个 1 就行，eg：
    >>> data = {
    ...     'a': 'value of a',
    ...     'b': 'value of b',
    ...     'c': 'value of c',
    ... }
    >>> map_rules = {
    ...     'a': 'x',
    ... }
    >>> dict_project(data, map_rules)
    {'x': 'value of a'}
    >>> map_rules = {
    ...     'c': 1
    ... }
    >>> dict_project(data, map_rules)
    {'c': 'value of c'}
    """
    if isinstance(data, dict):
        data = {map_rules[k] if isinstance(map_rules[k], basestring) else k: data[k] for k in data if k in map_rules}
    elif isinstance(data, (list, tuple)):
        return [dict_project(o, map_rules) for o in data]
    else:
        raise ValueError('无法处理对象: %s' % str(data))
    return data


def group_by_key(dict_list, key):
    """
    >>> data = [
    ...     {'a': 1, 'b': 2},
    ...     {'a': 1, 'b': 3}
    ... ]
    >>> group_by_key(data, 'a')
    {1: [{'a': 1, 'b': 2}, {'a': 1, 'b': 3}]}
    """
    grouped = {}
    for d in dict_list:
        group_key = d.get(key)
        grouped.setdefault(group_key, [])
        grouped[group_key].append(d)
    return grouped


def group_by_keys(dict_list, keys):
    """
    >>> data = [
    ...     {'a': 1, 'b': 2},
    ...     {'a': 1, 'b': 3}
    ... ]
    >>> group_by_keys(data, ['a', 'b'])
    {(1, 2): [{'a': 1, 'b': 2}], (1, 3): [{'a': 1, 'b': 3}]}
    """
    groups = {}
    for d in dict_list:
        value = tuple((d[k] for k in keys))
        groups.setdefault(value, [])
        groups[value].append(d)
    return groups


def merge_dicts(dicts):
    """将一组 dicts 取并集返回，键值冲突处理规则为：
    1. 优先返回最大的数值
    2. 若无数值类型，则返回倒数第一个值
    """
    total_k = reduce(lambda x, y: x | y.keys(), dicts, {})
    _d = {}
    for k in total_k:
        total_v = [d[k] for d in dicts if k in d]  # 必不为空
        # 选出最合适的一个
        numbers_v = [v for v in total_v if isinstance(v, Number)]
        if numbers_v:
            _d[k] = max(numbers_v)
        else:
            _d[k] = total_v[-1]
    return _d


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
    0
    >>> check_bin(2, 2)
    1
    """
    try:
        return int(bin(number)[2:][-index])
    except IndexError:
        return 0


def update_bin(number, index_pairs):
    """
    用于某些二进制标志位的场景
    将一个 int 类型变量的二进制数的第 index 位，置为 value 并返回新变量，index 从 1 开始, 如
    >>> update_bin(2, {2: 0})
    0
    >>> update_bin(2, {3: 1})
    6
    """
    for index, value in index_pairs.items():
        if value:
            number = number | int('1' + '0' * (index - 1), 2)
        else:
            number = number & int('0' + '1' * (index - 1), 2)
    return number


def filter_bin(length, index_pairs):
    """
    用于某些二进制标志位的场景
    index_pairs: {index: value,}
    返回 length 长度内第 index 位值为 value 的所有可能的 int 的 list, index 从 1 开始, e.g.
    >>> filter_bin(3, {1: 1})
    [1, 3, 5, 7]
    >>> filter_bin(3, {1: 1, 2: 0})
    [1, 5]
    >>> filter_bin(3, {1: 0, 2: 1})
    [2, 6]
    """
    ret = []
    for number in range(int('1' * length, 2) + 1):
        match = True
        for index in index_pairs:
            if len(bin(number)) - index >= 2:  # 位数够
                if int(bin(number)[-index]) ^ index_pairs[index]:
                    match = False
            else:  # 位数不够
                if index_pairs[index]:
                    match = False
        if match:
            ret.append(number)
    return ret


if __name__ == '__main__':
    import doctest
    doctest.testmod(verbose=True)
