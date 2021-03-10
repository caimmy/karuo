# -*- encoding: utf-8 -*-
'''
@文件    :test_qywx.py
@说明    :
@时间    :2020/12/14 16:41:55
@作者    :caimmy@hotmail.com
@版本    :0.1
'''
import sys, os, codecs, base64
_proj_root = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
print(_proj_root)
sys.path.append(_proj_root)

import unittest
from karuo.qywx.base import QywxClient

class TestQywxClient(unittest.TestCase):
    def testSingleMethod(self):
        client = QywxClient("wx1ac9c673f281add6",
                        "lClGIPazrIcIFbeTkX13wBdRPbFm17tsslTQhMgvcd8")
        # result = client.CreateSchedule("long", 1607997600, 1608001200, ["caimmy", "long", "wangtao", "liangchaowei", "demouser"], "测试会议日程", "alsdkfjaslkdf asldfsadf拉丝机的弗拉sdf", "五楼会议室")
        
        # result = client.UpdateSchedule("caimmy", "8ace6b79414a03040d7b1569900b30a7", 1607997600, 1608001200, ["caimmy", "long", "wangtao", "liangchaowei"], "测试会议日程更新", "alsdkfjaslkdf asldfsadf拉丝机的弗拉sdf", "董事长办公室")
        #result = client.CreateDocSpace("caimmy", "api创建的空间", [])
        
        test_space_id = "s.wx1ac9c673f281add6.615340355PLh"

        # # 上传文件测试
        # with open('/data/duoneng_20210117.xls', 'rb') as f:
        #     _c = f.read()
        #     _content = base64.b64encode(_c)
        #     result = client.UploadDocFile("caimmy", test_space_id, "duoneng_20210117.xls", _content.decode('utf-8'))
        #     print(result)
        # print(client.UploadDocFile("long", test_space_id, "demo.txt", base64.b64encode("何当共剪西窗烛".encode("utf-8")).decode("utf-8")))

        result = client.DeleteFileAccess("caimmy", "s.wx1ac9c673f281add6.615340355PLh_f.615343547R0Uq", 
            [
                {
                    "type": 1,
                    "userid": "long"
                }
            ])
        print(result)
        print("----------------------")

        result = client.GetDocFilesList("long", test_space_id)
        print(result)

if "__main__" == __name__:
    suite = unittest.TestSuite()
    suite.addTest(TestQywxClient("testSingleMethod"))
    runner = unittest.TextTestRunner()
    runner.run(suite)