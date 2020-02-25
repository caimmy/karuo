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

    @staticmethod
    def date_list(start_date: str, end_date: str, include_enddate=False) -> list:
        """
        通过起始日期和结束日期两个参数，获取一个从起始日期到结束日期的日期列表，按日填充
        :param start_date: 起始日期
        :param end_date: 结束日期
        :param include_enddate: 返回的列表中是否包含结束日期，默认不包含
        :return:
        """
        ret_date_list = []
        _start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
        _end_datetime = datetime.strptime(end_date, "%Y-%m-%d")
        if _start_datetime < _end_datetime:
            _cur_timestamp = _start_datetime.timestamp()
            _flag_timestamp = _end_datetime.timestamp()
            while _cur_timestamp < _flag_timestamp:
                _cur_datetime = datetime.fromtimestamp(_cur_timestamp)
                ret_date_list.append(_cur_datetime.strftime("%Y-%m-%d"))
                _cur_timestamp = (_cur_datetime + timedelta(days=1)).timestamp()
            if include_enddate: ret_date_list.append(end_date)
        else:
            raise ValueError("end_date must greater than start_date")
        return ret_date_list