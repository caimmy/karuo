# -*- encoding: utf-8 -*-
'''
@文件    :char_helper.py
@说明    :
@时间    :2020/09/17 10:07:46
@作者    :caimmy@hotmail.com
@版本    :0.1
'''

def ensureString(s: any) -> str:
    """
    确保s是一个字符串
    """
    if isinstance(s, str): return s
    if isinstance(s, bytes): return s.decode("UTF-8")
    return str(s)

def ensureBytes(b: any) -> bytes:
    """
    确保b是一个bytes类型的数据
    """
    if isinstance(b, bytes): return b
    if isinstance(b, str): return b.encode("utf-8")
    return bytes(str(b), "utf-8")
