# _*_ coding: utf-8 _*_
"""
-------------------------------------------------
@File Name： date_helper
@Description:
@Author: caimmy
@date： 2020/2/13 17:28
-------------------------------------------------
Change Activity:

-------------------------------------------------
"""

import time
from datetime import datetime, timedelta

class DatetimeHelper:
    @staticmethod
    def date_before_n_days(days: int, at = 0) -> datetime :
        """
        计算从指定时间戳往前的N天
        :param days: 偏移天数
        :param at: 其实偏移时间戳
        :return: datetime
        """
        _start_timestamp = datetime.now().timestamp() if 0 == at else at
        return datetime.fromtimestamp(_start_timestamp) - timedelta(days=days)

    @staticmethod
    def day_range_of_timestamp(start_date: datetime, end_date: datetime) -> (int, int):
        """
        计算日期范围的起止时间戳，（标准，从开始日期0点 到 结束日期0点）
        :param start_date:
        :param end_date:
        :return:
        """
        if isinstance(start_date, datetime) and isinstance(end_date, datetime):
            if not start_date > end_date:
                _s = datetime.strptime(start_date.strftime("%Y-%m-%d"), "%Y-%m-%d")
                _e = datetime.strptime(DatetimeHelper.date_before_n_days(-1, end_date.timestamp()).strftime("%Y-%m-%d"), "%Y-%m-%d")
                return _s.timestamp(), _e.timestamp()
            else:
                raise ValueError("end_date must greater than start_date")
        else:
            raise ValueError("params must be instance of datetime")

