# -*- encoding: utf-8 -*-
'''
@文件    :func_ocr.py
@说明    :OCR文字识别
@时间    :2021/05/28 11:51:21
@作者    :caimmy@hotmail.com
@版本    :0.1
'''



import json
from base64 import b64encode
from .base import ApiRequestBase, ACCEPTION_CONFIDENCE, LIVENESS_CONTROL
from karuo.datadef import KaruoResult


class OcrAiTool(ApiRequestBase):
    """
    识别语言类型，默认为CHN_ENG
    可选值包括：
    - CHN_ENG：中英文混合
    - ENG：英文
    - JAP：日语
    - KOR：韩语
    - FRE：法语
    - SPA：西班牙语
    - POR：葡萄牙语
    - GER：德语
    - ITA：意大利语
    - RUS：俄语
    """
    def RecognizeText(self, image: str=None, url: str=None, language_type: str = 'CHN_ENG', detect_direction: bool=False, detect_language: bool=False, paragraph: bool=False, probability: bool=False, basic: bool=True, with_locaton:bool=False):
        '''
        :param basic bool 是否是基础版本 默认True基础版
        '''
        _result = KaruoResult()
        _params = {
            'language_type': language_type,
            'detect_direction': detect_direction,
            'detect_language': detect_language,
            'paragraph': paragraph,
            'probability': probability
        }
        if not (image or url):
            _result.setMessage("image url 参数不能同时缺失")
        else:
            if image:
                _params['image'] = self.base64FileContent(image)
            elif url:
                _params['url'] = url
        if basic:
            if with_locaton:
                api_address = "https://aip.baidubce.com/rest/2.0/ocr/v1/general"
            else:
                api_address = "https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic"
        else:
            if with_locaton:
                api_address = "https://aip.baidubce.com/rest/2.0/ocr/v1/accurate"
            else:
                api_address = "https://aip.baidubce.com/rest/2.0/ocr/v1/accurate_basic"

        res = self._sendApiRequest(api_address, params=_params)
        if res.ok:
            _result.setSuccess(res.json())
        else:
            _result.setMessage(res.text)
        return _result