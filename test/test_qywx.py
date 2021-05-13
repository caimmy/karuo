# -*- encoding: utf-8 -*-
'''
@文件    :test_qywx.py
@说明    :
@时间    :2020/12/14 16:41:55
@作者    :caimmy@hotmail.com
@版本    :0.1
'''
import sys, os, codecs, base64
import time
_proj_root = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
print(_proj_root)
sys.path.append(_proj_root)

import unittest
from karuo.qywx.base import QywxClient, DocSpaceACL, MicroDocumentType

class TestQywxClient(unittest.TestCase):

    def setUp(self):
        self.client = QywxClient("wx1ac9c673f281add6",
                        "8L5MUh-xSrBC8LYwEjh7BJ0VbZXRcUkIZd29OPafV2E")

    def _tTmp(self):
        a = DocSpaceACL.PREVIEW.value

        print(a)

    def _tCreateDocSpace(self):
        result = self.client.DocSpaceCreate("robot_document", "项目1启动流程", ['caimmy', 'long', 'xujing'], [], defaultAuth=1)
        print(result)

    def _tDeleteDocSpaceACL(self):
        result = self.client.DocSpaceDeleteACL("robot_document", "s.wx1ac9c673f281add6.619073743FM2", ["huji", "jianhuiyong"], [])
        print(result)

    def _tDocSpaceAclAdd(self):
        result = self.client.DocSpaceAddACL("robot_document", "s.wx1ac9c673f281add6.619073743FM2", ['caimmy'], [], DocSpaceACL.EDITABLE)
        print(result)

    def _tDocSpaceSetting(self):
        result = self.client.DocSpaceSetting("robot_document", "s.wx1ac9c673f281add6.619073743FM2")
        print(result)

    def _tDocSpaceUpload(self):
        with open('/data/duoneng_20210117.xls', 'rb') as f:
            _c = f.read()
            _content = base64.b64encode(_c)
        result = self.client.DocSpaceUploadFileContent('long', "s.wx1ac9c673f281add6.619073743FM2", "duoneng_20210117.xls", _content.decode('utf-8'))
        print(result)

    def _tDocSpaceUploadRaw(self):
        result = self.client.DocSpaceUploadFile("long", "s.wx1ac9c673f281add6.619073743FM2", "/data/work/karuo/README.md", "README.md")
        print(result)

    def _tDocQueryDocSpace(self):
        result = self.client.DocSpaceGetFilesList("caimmy", "s.wx1ac9c673f281add6.619073743FM2")
        print(result)

    def _tDocCreateDocument(self):
        result = self.client.DocSpaceCreateMicroDocument('robot_document', "s.wx1ac9c673f281add6.619073743FM2", "collection", MicroDocumentType.EXCEL, fatherid="s.wx1ac9c673f281add6.619073743FM2_d.6190829161iin")
        print(result)

    def _tDocGetShareurl(self):
        result = self.client.DocSpaceFileShareUrl("robot_document", "s.wx1ac9c673f281add6.619073743FM2_f.619078542Pk47")
        print(result)

    def _tCalendarRobot(self):
        _now = int(time.time())
        _end_time = _now + 3600 * 24 * 7
        result = self.client.CreateScheduleComplex('duoneng_work_robot', _now, _end_time, ['long', 'longjiang', 'caimmy'], "工作任务", 
        "来看数据地方卢卡斯地方卢卡斯蝶恋蜂狂是按地方撒地方", "", 1, 1, 0, 7, _end_time)
        print(result)

    def testSingleMethod(self):
        self._tDocGetShareurl()
        # client = QywxClient("wx1ac9c673f281add6",
        #                 "lClGIPazrIcIFbeTkX13wBdRPbFm17tsslTQhMgvcd8")
        # result = client.CreateSchedule("long", 1607997600, 1608001200, ["caimmy", "long", "wangtao", "liangchaowei", "demouser"], "测试会议日程", "alsdkfjaslkdf asldfsadf拉丝机的弗拉sdf", "五楼会议室")
        
        # result = client.UpdateSchedule("caimmy", "8ace6b79414a03040d7b1569900b30a7", 1607997600, 1608001200, ["caimmy", "long", "wangtao", "liangchaowei"], "测试会议日程更新", "alsdkfjaslkdf asldfsadf拉丝机的弗拉sdf", "董事长办公室")
        #result = client.CreateDocSpace("caimmy", "api创建的空间", [])
        
        # test_space_id = "s.wx1ac9c673f281add6.615340355PLh"

        # # 上传文件测试
        # with open('/data/duoneng_20210117.xls', 'rb') as f:
        #     _c = f.read()
        #     _content = base64.b64encode(_c)
        #     result = client.UploadDocFile("caimmy", test_space_id, "duoneng_20210117.xls", _content.decode('utf-8'))
        #     print(result)
        # print(client.UploadDocFile("long", test_space_id, "demo.txt", base64.b64encode("何当共剪西窗烛".encode("utf-8")).decode("utf-8")))

        # result = client.DeleteFileAccess("caimmy", "s.wx1ac9c673f281add6.615340355PLh_f.615343547R0Uq", 
        #     [
        #         {
        #             "type": 1,
        #             "userid": "long"
        #         }
        #     ])
        # print(result)
        # print("----------------------")

        # result = client.GetDocFilesList("long", test_space_id)
        # print(result)

if "__main__" == __name__:
    suite = unittest.TestSuite()
    suite.addTest(TestQywxClient("_tCalendarRobot"))
    runner = unittest.TextTestRunner()
    runner.run(suite)