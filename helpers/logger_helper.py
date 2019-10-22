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

def getTimedRotatingLogger(filename, when="d", interval=1, backupCount=30):
    # logging    初始化工作
    gen_logger = logging.getLogger("zjlogger")
    gen_logger.setLevel(logging.DEBUG)

    # 添加TimedRotatingFileHandler
    # 定义一个1秒换一次log文件的handler
    # 保留3个旧log文件
    rf_handler = logging.handlers.TimedRotatingFileHandler(filename="logs/app.log", when='d', interval=1,
                                                           backupCount=30)
    rf_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(filename)s[:%(lineno)d] - %(message)s"))

    # 在控制台打印日志
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))

    gen_logger.addHandler(rf_handler)
    gen_logger.addHandler(handler)


    return gen_logger