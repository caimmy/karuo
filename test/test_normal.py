# _*_ coding: utf-8 _*_
"""
-------------------------------------------------
@File Name： test_normal
@Description:
@Author: caimmy
@date： 2020/7/30 11:26
-------------------------------------------------
Change Activity:

-------------------------------------------------
"""

from unittest import TestCase
import shortuuid
import datetime
class NormalTest(TestCase):
    def testShortuuid(self):
        datas = []
        stm = datetime.datetime.now().strftime("%d:%H:%S")
        for i in range(200000):
            datas.append(shortuuid.uuid(name="abc"))
        etm = datetime.datetime.now().strftime("%d:%H:%S")
        print(datas)
        print(len(datas))
        print(stm, etm)