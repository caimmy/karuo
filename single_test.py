# -*- encoding: utf-8 -*-
'''
@文件    :single_test.py
@说明    :
@时间    :2021/05/28 15:58:25
@作者    :caimmy@hotmail.com
@版本    :0.1
'''



import unittest
from test.test_ai_ocr import OcrAiTest

if "__main__" == __name__:
    suite = unittest.TestSuite()
    suite.addTest(OcrAiTest("testRecognizeText"))
    runner = unittest.TextTestRunner()
    runner.run(suite)