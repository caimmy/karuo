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
import time, datetime
from karuo.helpers.logger_helper import LoggerTimedRotating
from karuo.helpers.date_helper import DatetimeHelper

class HelperTest(TestCase):
    def testTimedRotatingLogger(self):
        l1 = LoggerTimedRotating.getInstance(r"./raws/t.log", logger="abc")
        l1.debug("asdfasdf")

        l2 = LoggerTimedRotating.getInstance(r"./raws/t.log", logger="adf")
        l2.info("infor l2")

        l3 = LoggerTimedRotating.getInstance(r"./raws/t1.log", logger="abc1")
        l3.debug("debug l3")

    def testDateBeforeNDays(self):
        testDate = DatetimeHelper.date_before_n_days(3, datetime.datetime.strptime("2020-02-13 10:00:00", "%Y-%m-%d %H:%M:%S").timestamp())
        self.assertEqual("2020-02-10", testDate.strftime("%Y-%m-%d"))
        tStartDate = datetime.datetime.strptime("2020-02-13 10:00:00", "%Y-%m-%d %H:%M:%S")
        t1, t2 = DatetimeHelper.day_range_of_timestamp(tStartDate, tStartDate)
        self.assertEqual("2020-02-13 00:00:00", datetime.datetime.fromtimestamp(t1).strftime("%Y-%m-%d %H:%M:%S"))
        self.assertEqual("2020-02-14 00:00:00", datetime.datetime.fromtimestamp(t2).strftime("%Y-%m-%d %H:%M:%S"))

    def testDatelist(self):
        ret_date_list = DatetimeHelper.date_list("2019-01-01", "2019-02-01")
        self.assertEqual(len(ret_date_list), 31)
        ret_date_list = DatetimeHelper.date_list("2019-01-01", "2019-02-01", True)
        print(ret_date_list)
        self.assertEqual(len(ret_date_list), 32)