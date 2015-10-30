# -*- coding: utf-8 -*-

__all__ = [
    'Storage',
]


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

    dict 子类，支持属性式访问其 key (`obj.key`)，KeyError => AttributeError
    """

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError as k:
            raise AttributeError(k.message)

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, key):
        try:
            del self[key]
        except KeyError as k:
            raise AttributeError(k.message)

    def __repr__(self):
        return '<Storage ' + dict.__repr__(self) + '>'
