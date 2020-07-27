# _*_ coding: utf-8 _*_
"""
-------------------------------------------------
@File Name： test_ai_face
@Description:
@Author: caimmy
@date： 2020/7/24 9:39
-------------------------------------------------
Change Activity:

-------------------------------------------------
"""
from unittest import TestCase


import karuo.baiduai

karuo.baiduai.APP_KEY = "MXbcVYhEbqxtV9NCGO3YSTXc"
karuo.baiduai.APP_SECRET = "YcjX8psuhOsGz3ngEQLXwghGo2mvrF3F"

from karuo.baiduai.func_faces import FacerelAiTool

class FaceAiTest(TestCase):
    def setUp(self):
        tool = FacerelAiTool()
        add_ret, result = tool.FaceLibraryAdd("./imgs/liudehua5.jpg", "demo", "liudehua", "123", False)

    def tearDown(self):
        pass

    def testFaceMatch(self):
        tool = FacerelAiTool()
        check, msg = tool.FaceMatch("./imgs/liudehua.jpg", "./imgs/liudehua5.jpg", False)
        self.assertTrue(check)

    def _testFacelibadd(self):
        tool = FacerelAiTool()
        add_ret, result = tool.FaceLibraryAdd("./imgs/liudehua5.jpg", "demo", "liudehua", "123", False)
        print(result)
        self.assertTrue(add_ret)

    def testFacelibQuery(self):
        tool = FacerelAiTool()
        result = tool.FaceLibraryQuery("liudehua", "demo")
        print(result)
        self.assertEqual(0, result.get("code"))

    def testFacelibUpdate(self):
        tool = FacerelAiTool()
        ret, result = tool.FaceLibraryUpdate("./imgs/liudehua.jpg", "demo", "liudehua", "123")
        self.assertEqual(0, result.get("code"))
        print(result)

    def testFacelibDelete(self):
        tool = FacerelAiTool()
        ret, result = tool.FaceLibraryUpdate("./imgs/liudehua.jpg", "demo", "liudehua", "")
        self.assertEqual(0, result.get("code"))
        print(result)
        print("--------------------updated------------------------")
        face_token = result.get("face_token")
        ret, result = tool.FaceLibraryDelete("liudehua", "demo", face_token)
        self.assertEqual(0, result.get("code"))
        print(result)
        print("--------------------deleted------------------------")

    def testFacelibSearch(self):
        tool = FacerelAiTool()
        ret, result = tool.FaceLibrarySearch("./imgs/liudehua.jpg", ["demo"])
        self.assertEqual(0, result.get("code"))
        print(result)