# -*- coding: utf-8 -*-
import inspect
import time
from functools import wraps
from flask import g
from flask import json
from flask import request
from flask import current_app
from numbers import Number
try:
    basestring
except NameError:
    basestring = str


CODE_MSG = {
    0: u'success',
    10: u'参数不合法',
    11: u'缺少必传参数',
    12: u'参数类型错误',
    13: u'参数值不合法',
    50: u'内部错误',
}


def resp(errcode, errmsg='', data={}):
    assert isinstance(errcode, int), 'invalid errcode type, int needed.'
    assert isinstance(errmsg, basestring), 'invalid errmsg type, string needed.'
    if not errmsg:
        errmsg = CODE_MSG.get(errcode, '')
    if errcode != 0:
        current_app.logger.warn('resp errcode: %d, errmsg: %s\nrequest: %s' %
                                (errcode, errmsg, getattr(g, 'cur_request', None)))
    return json.jsonify(errcode=errcode, errmsg=errmsg, data=data)


def _check_type(var1, var2):
    for ctype in (Number, basestring, (list, tuple), dict, bool):
        if isinstance(var1, ctype) and not isinstance(var2, ctype):
            return False
    return True


def parse_args(f):
    """为 view function 提供参数服务
    必须紧贴 view function
    """
    @wraps(f)
    def wrapped(**kwargs):
        # 参数获取
        kwargs.update(request.values.to_dict())
        if isinstance(request.json, dict):
            kwargs.update(request.json)
        g.cur_request = json.dumps({
            'request_args': kwargs,
            'start_time': time.time(),
        })
        # 参数检查
        spec = inspect.getargspec(f)
        defaults = {}
        if spec.defaults:
            for i in range(len(spec.defaults)):
                idx = -(i + 1)
                defaults[spec.args[idx]] = spec.defaults[idx]
        # 缺少参数
        for name in spec.args:
            if name not in kwargs and name not in defaults:
                return resp(11, 'required param %s is not given.' % name)
        # 参数类型错误
        for name, value in defaults.items():
            if value is not None and name in kwargs:
                if not _check_type(value, kwargs[name]):
                    return resp(12, 'param %s type error.' % name)
        # 参数过滤
        if spec.keywords is None:
            kwargs = {k: v for k, v in kwargs.items() if k in spec.args}
        return f(**kwargs)
    return wrapped
