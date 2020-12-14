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

import unittest
from unittest import TestCase
import time, datetime
from karuo.helpers.logger_helper import LoggerTimedRotating
from karuo.helpers.date_helper import DatetimeHelper
from karuo.qywx.WXBizMsgCrypt import WXBizMsgCrypt

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


    def testWxencrypt(self):
        sToken = "hJqcu3uJ9Tn2gXPmxx2w9kkCkCE2EPYo"
        sEncodingAESKey = "6qkdMrq68nTKduznJYO1A37W2oEgpkMUvkttRToqhUt"
        sCorpID = "ww1436e0e65a779aee"
        '''
            ------------使用示例一：验证回调URL---------------
            *企业开启回调模式时，企业号会向验证url发送一个get请求 
            假设点击验证时，企业收到类似请求：
            * GET /cgi-bin/wxpush?msg_signature=5c45ff5e21c57e6ad56bac8758b79b1d9ac89fd3&timestamp=1409659589&nonce=263014780&echostr=P9nAzCzyDtyTWESHep1vC5X9xho%2FqYX3Zpb4yKa9SKld1DsH3Iyt3tP3zNdtp%2B4RPcs8TgAE7OaBO%2BFZXvnaqQ%3D%3D 
            * HTTP/1.1 Host: qy.weixin.qq.com
            接收到该请求时，企业应	1.解析出Get请求的参数，包括消息体签名(msg_signature)，时间戳(timestamp)，随机数字串(nonce)以及企业微信推送过来的随机加密字符串(echostr),
            这一步注意作URL解码。
            2.验证消息体签名的正确性 
            3. 解密出echostr原文，将原文当作Get请求的response，返回给企业微信
            第2，3步可以用企业微信提供的库函数VerifyURL来实现。
        '''
        wxcpt=WXBizMsgCrypt(sToken,sEncodingAESKey,sCorpID)
        #sVerifyMsgSig=HttpUtils.ParseUrl("msg_signature")
        #ret = wxcpt.VerifyAESKey()
        #print ret
        sVerifyMsgSig="012bc692d0a58dd4b10f8dfe5c4ac00ae211ebeb"
        #sVerifyTimeStamp=HttpUtils.ParseUrl("timestamp")
        sVerifyTimeStamp="1476416373"
        #sVerifyNonce=HttpUitls.ParseUrl("nonce")
        sVerifyNonce="47744683"
        #sVerifyEchoStr=HttpUtils.ParseUrl("echostr")
        sVerifyEchoStr="fsi1xnbH4yQh0+PJxcOdhhK6TDXkjMyhEPA7xB2TGz6b+g7xyAbEkRxN/3cNXW9qdqjnoVzEtpbhnFyq6SVHyA=="
        ret,sEchoStr=wxcpt.VerifyURL(sVerifyMsgSig, sVerifyTimeStamp,sVerifyNonce,sVerifyEchoStr)
        if(ret!=0):
            print("ERR: VerifyURL ret: " + str(ret))


if "__main__" == __name__:
    suite = unittest.TestSuite()
    suite.addTest(HelperTest("testWxencrypt"))
    
    runner = unittest.TextTestRunner()
    runner.run(suite)