# _*_ coding: utf-8 _*_
"""
-------------------------------------------------
@File Name： base
@Description:
@Author: caimmy
@date： 2020/7/22 11:39
-------------------------------------------------
Change Activity:

-------------------------------------------------
"""
import os
import json
import time
import pickle
import tempfile
from urllib.parse import urlencode
import requests

from karuo.baiduai import APP_KEY, APP_SECRET

_, token_cache_file = tempfile.mkstemp(prefix="token_", suffix=".bin")


# 置换访问口令的URL地址
API_URL_ACCESS_TOKEN = "https://aip.baidubce.com/oauth/2.0/token"
# 置信度
ACCEPTION_CONFIDENCE = 80
# 活体检测级别
LIVENESS_CONTROL = "NORMAL" # "HIGH


def request_access_token():
    """
    置换调用业务需要的口令
    使用设备本地文件系统作为缓存
    :return:
    """
    actoken = False
    if os.path.isfile(token_cache_file):
        with open(token_cache_file, "rb") as f:
            try:
                access_token_info = pickle.load(f)
            except EOFError:
                access_token_info = None
            if isinstance(access_token_info, dict) and "expire_tm" in access_token_info and int(time.time()) < access_token_info.get("expire_tm"):
                actoken = access_token_info
    if actoken is False:
        url_tail = urlencode({
            "grant_type": "client_credentials",
            "client_id": APP_KEY,
            "client_secret": APP_SECRET
        })
        req = requests.get(f"{API_URL_ACCESS_TOKEN}?{url_tail}")
        if req.ok:
            response = req.json()
            catch_infor = {
                "expire_tm": int(time.time()) + response.get("expires_in") - 300,       # 提前5分钟过期
                "val": response
            }
            with open(token_cache_file, "wb") as f:
                pickle.dump(catch_infor, f)
            actoken = catch_infor
    return actoken


class ApiRequestBase():
    """
    发起api调用的公共基类
    """
    def __init__(self):
        self._access_token = None

    def _getAccessToken(self):
        if not self._access_token or int(time.time()) > self._access_token.get("expire_tm"):
            self._access_token = request_access_token()
        if not self._access_token:
            raise Exception("access token failure")
        return self._access_token.get("val").get("access_token")

    def _sendApiRequest(self, url, params):
        """
        执行实际的api调用请求
        :param url:
        :param params:
        :return: dict
        """
        _url = f"{url}?access_token={self._getAccessToken()}"
        response = requests.post(_url, data=params, headers={'content-type': 'application/x-www-form-urlencoded'})
        return self.parseApiRequestResult(response)

    def parseApiRequestResult(self, response: requests.Response):
        """
        对请求结果进行解析
        可以被重写
        :param response:
        :return: bool 是否接受人脸的一致性评价, result: dict
        """
        result = False
        _resp = response.json() if response.ok else False
        if _resp:
            try:
                _error_code = _resp.get("error_code")
                _error_msg = _resp.get("error_msg")
                _result = _resp.get("result")
                _score = _result.get("score") if result else 0
                result = {
                    "code": _error_code,
                    "msg": _error_msg,
                    "score": _score,
                    "face_token": _result.get("face_token") if _result else 0,
                    "origin": _result
                }
            except Exception:
                result = False
        return result
