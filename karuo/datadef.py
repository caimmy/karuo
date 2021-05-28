# -*- encoding: utf-8 -*-
'''
@文件    :datadef.py
@说明    :
@时间    :2021/05/28 14:55:29
@作者    :caimmy@hotmail.com
@版本    :0.1
'''

from dataclasses import dataclass, field
class KaruoResult:
    '''
    返回值封装对象
    '''
    code: int = -1
    msg: str = "gen_error"
    data: dict = field(default_factory=dict)

    @property
    def toDict(self):
        return {
            "code": self.code,
            "msg": self.msg,
            "data": self.data
        }

    def setSuccess(self, data={}):
        self.code = 0
        self.msg = ""
        self.data = data

    @property
    def IsSuccess(self):
        return 0 == self.code


    def setMessage(self, msg: str):
        """
        设置错误消息
        :param msg str 错误消息
        """
        self.msg = msg