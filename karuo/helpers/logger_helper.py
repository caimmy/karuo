# _*_ coding: utf-8 _*_
"""
-------------------------------------------------
@File Name： logger_helper
@Description:
@Author: caimmy
@date： 2019/10/22 12:30
-------------------------------------------------
Change Activity:

-------------------------------------------------
"""

import logging
import logging.handlers
import os

class LoggerTimedRotating(object):
    _instances = {}

    @staticmethod
    def getInstance(filename, when='d', interval=1, backupCount=30, logger='karuo', level=logging.DEBUG) -> logging.Logger:
        cls = __class__
        if logger not in cls._instances:
            _log_path = os.path.abspath(os.path.dirname(filename))
            if not os.path.isdir(_log_path):
                os.mkdir(_log_path)
            if os.path.isdir(_log_path):
                gen_logger = logging.getLogger(logger)
                gen_logger.setLevel(level)

                rf_handler = logging.handlers.TimedRotatingFileHandler(filename=filename, when=when, interval=interval,
                                                                       backupCount=backupCount)
                rf_handler.setFormatter(
                    logging.Formatter("%(asctime)s - %(levelname)s - %(filename)s[:%(lineno)d] - %(message)s"))

                # 在控制台打印日志
                handler = logging.StreamHandler()
                handler.setLevel(level)
                handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))

                gen_logger.addHandler(rf_handler)
                gen_logger.addHandler(handler)

                cls._instances.setdefault(logger, gen_logger)
            else:
                raise IOError("logger file not exists")
        return cls._instances.get(logger)
