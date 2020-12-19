# -*- encoding: utf-8 -*-
'''
@文件    :test_qywx.py
@说明    :
@时间    :2020/12/14 16:41:55
@作者    :caimmy@hotmail.com
@版本    :0.1
'''
import sys, os
_proj_root = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
print(_proj_root)
sys.path.append(_proj_root)

import unittest
from karuo.qywx.base import QywxClient

class TestQywxClient(unittest.TestCase):
    def testCreateSchedule(self):
        client = QywxClient("wx1ac9c673f281add6",
                        "oSRzybnxy4r7q0z8tbI1L1cqjMaJjWa3lCvU04Mi7vw")
        # result = client.CreateSchedule("long", 1607997600, 1608001200, ["caimmy", "long", "wangtao", "liangchaowei", "demouser"], "测试会议日程", "alsdkfjaslkdf asldfsadf拉丝机的弗拉sdf", "五楼会议室")
        
        # result = client.UpdateSchedule("caimmy", "8ace6b79414a03040d7b1569900b30a7", 1607997600, 1608001200, ["caimmy", "long", "wangtao", "liangchaowei"], "测试会议日程更新", "alsdkfjaslkdf asldfsadf拉丝机的弗拉sdf", "董事长办公室")
        result = client.DeleteSchedule("06430a6f3ddd5e31084a5c97d9aca129")
        print(result)

if "__main__" == __name__:
    suite = unittest.TestSuite()
    suite.addTest(TestQywxClient("testCreateSchedule"))
    runner = unittest.TextTestRunner()
    runner.run(suite)