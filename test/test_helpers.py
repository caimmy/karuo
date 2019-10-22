# _*_ coding: utf-8 _*_
"""
-------------------------------------------------
@File Name： test_helpers
@Description:
@Author: caimmy
@date： 2019/10/22 17:47
-------------------------------------------------
Change Activity:

-------------------------------------------------
"""

from unittest import TestCase
from karuo.helpers.logger_helper import LoggerTimedRotating

class HelperTest(TestCase):
    def testTimedRotatingLogger(self):
        l1 = LoggerTimedRotating.getInstance(r"./raws/t.log", logger="abc")
        l1.debug("asdfasdf")

        l2 = LoggerTimedRotating.getInstance(r"./raws/t.log", logger="adf")
        l2.info("infor l2")

        l3 = LoggerTimedRotating.getInstance(r"./raws/t1.log", logger="abc1")
        l3.debug("debug l3")