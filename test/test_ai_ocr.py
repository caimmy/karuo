# -*- encoding: utf-8 -*-
'''
@文件    :test_ai_ocr.py
@说明    :
@时间    :2021/05/28 15:54:37
@作者    :caimmy@hotmail.com
@版本    :0.1
'''


from unittest import TestCase
from pprint import pprint

import karuo.baiduai

karuo.baiduai.APP_KEY = "MXbcVYhEbqxtV9NCGO3YSTXc"
karuo.baiduai.APP_SECRET = "YcjX8psuhOsGz3ngEQLXwghGo2mvrF3F"

from karuo.baiduai.func_ocr import OcrAiTool

class OcrAiTest(TestCase):
    def setUp(self):
        self.tool = OcrAiTool()
    
    def testRecognizeText(self):
        # res = self.tool.RecognizeText(url="https://ss1.bdstatic.com/70cFvXSh_Q1YnxGkpoWK1HF6hhy/it/u=1071507966,561992845&fm=224&gp=0.jpg")
        res = self.tool.RecognizeText(image="/data/work/karuo/test/imgs/hetong_ocr1.jpg", detect_direction=True)
        pprint(res.toDict)