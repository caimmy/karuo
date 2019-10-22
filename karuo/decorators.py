# _*_ coding: utf-8 _*_
"""
-------------------------------------------------
@File Name： decorators
@Description:
@Author: caimmy
@date： 2019/10/22 17:26
-------------------------------------------------
Change Activity:

-------------------------------------------------
"""

import functools

def Singleton(cls):
    _instance = {}

    @functools.wraps
    def getInstance(*args, **kwargs):
        nonlocal _instance
        if not str(cls) in _instance:
            _instance.setdefault(str(cls), cls(*args, **kwargs))
        return _instance.get(str(cls))
    return getInstance