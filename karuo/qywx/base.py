# _*_ coding: utf-8 _*_
"""
-------------------------------------------------
@File Name： base
@Description:
@Author: caimmy
@date： 2020/7/29 13:45
-------------------------------------------------
Change Activity:

-------------------------------------------------
"""
import time
import os
import pickle
import json
import tempfile
import requests
import urllib
from .WXBizMsgCrypt import WXBizMsgCrypt

def _refreshAccessToken(corpid: str, corpsecret: str):
    """
    通过企业微信服务器访问口令
    :return: dict | None
    """
    _url = f"https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={corpid}&corpsecret={corpsecret}"
    _req = requests.get(_url)
    if _req.ok:
        response_data = _req.json()
        if isinstance(response_data, dict) and 0 == response_data.get("errcode"):
            _access_token = response_data.get("access_token")
            _expires_in = response_data.get("expires_in")
            # 设置过期时间，比正常时间提前5分钟
            _exp_timestamp = int(time.time()) + (_expires_in - 300 if _expires_in > 300 else _expires_in)
            return {
                "exptm": _exp_timestamp,
                "access_token": _access_token
            }
    return None

def GetAccessToken(corpid: str, corpsecret: str):
    """
    获取访问口令，首先从缓存中获取
    :param corpid:
    :param corpsecret:
    :return: token, expiretm
    """
    ret_token = None
    ret_expiretm = 0
    _tmppath = tempfile.gettempdir()
    if not os.path.isdir(_tmppath):
        raise Exception("template path is invalid")
    _cache_token_file = os.path.join(_tmppath, f"{corpid}_{corpsecret}.bin")
    if os.path.isfile(_cache_token_file):
        with open(_cache_token_file, "rb") as f:
            _catched_data = pickle.load(f)
            if isinstance(_catched_data, dict) and "exptm" in _catched_data and _catched_data.get("exptm") > int(time.time()):
                ret_token = _catched_data.get("access_token")
                ret_expiretm = _catched_data.get("exptm")
    if not ret_token:
        # 没有从缓存文件中成功加载token，重新刷新token
        _refresh_data = _refreshAccessToken(corpid, corpsecret)
        if isinstance(_refresh_data, dict):
            ret_token = _refresh_data.get("access_token")
            ret_expiretm = _refresh_data.get("exptm")
            # 将刷新后的token写入缓存文件
            with open(_cache_token_file, "wb") as wf:
                pickle.dump(_refresh_data, wf)
    return ret_token, ret_expiretm

class _QywxBase():
    def __init__(self, corpid: str, corpsecret: str):
        self._corpid = corpid
        self._corpsecret = corpsecret
        # 初始化访问口令及访问口令过期时间
        self._access_token, self._token_exptm = GetAccessToken(self._corpid, self._corpsecret)

    def _getAccessToken(self):
        if int(time.time()) > self._token_exptm or not self._access_token:
            # 如果口令过期或者没有口令，则通过服务器刷新
            self._access_token, self._token_exptm = GetAccessToken(self._corpid, self._corpsecret)
        return self._access_token

    def postRequest(self, url: str, params: dict):
        """
        :param url:
        :param params:
        :return:
        """
        _url = f"{url}?access_token={self._getAccessToken()}"
        try:
            _response = requests.post(_url, bytes(json.dumps(params, ensure_ascii=False), "utf-8"))
            if _response.ok:
                ret_data = _response.json()
                return self._checkReponse(ret_data)
        except Exception as e:
            return False, str(e)

    def getRequest(self, url: str, params: dict):
        _url = f"{url}?access_token={self._getAccessToken()}"
        try:
            _response = requests.get(_url, params=params)
            if _response.ok:
                ret_data = _response.json()
                return self._checkReponse(ret_data)
        except Exception as e:
            return False, str(e)


    def _checkReponse(self, response):
        """
        检查API调用结果
        :param response:
        :return:
        """
        ret_check = True if "errcode" in response and 0 == response.get("errcode") else False
        return ret_check, response

class QywxClient(_QywxBase):

    def CallbackEchoStr(self, token:str, aeskey:str, msg_signature:str, timestamp:str, nonce:str, echostr:str) -> str:
        """
        设置回调时解密响应口令
        @return str
        """
        wxcpt = WXBizMsgCrypt(token, aeskey, self._corpid)
        ret, sEchoStr = wxcpt.VerifyURL(msg_signature, timestamp, nonce, echostr)
        return sEchoStr if 0 == ret else None

    def OauthRedirectUrl(self, url:str, state:str)->str:
        """
        构造oauth认证跳转地址
        """
        ret_url = ""
        if url and state:
            ret_url = f"https://open.weixin.qq.com/connect/oauth2/authorize?appid={self._corpid}&redirect_uri={urllib.parse.quote(url)}&response_type=code&scope=snsapi_base&state={state}#wechat_redirect"
        return ret_url

    def OauthGetUserInfor(self, code:str):
        """
        从oauth认证传递的code置换用户编号
        """
        _params = {
            "code": code
        }
        return self.getRequest("https://qyapi.weixin.qq.com/cgi-bin/user/getuserinfo", _params)


    def UserList(self, department_id: int, fetch_child: int = 0, detail: bool = False):
        """
        获取部门成员列表
        :param department_id:
        :param fetch_child: 1: 递归全部， 0: 当前层级
        :param detail: 是否获取完整的用户信息，默认否
        :return:
        """
        _params = {
            "department_id": department_id,
            "fetch_child": fetch_child
        }
        url = "https://qyapi.weixin.qq.com/cgi-bin/user/list" if detail else "https://qyapi.weixin.qq.com/cgi-bin/user/simplelist"
        ret, response = self.getRequest(url, _params)
        if ret:
            return response.get("userlist")
        return None

    def UserDetail(self, userid: str):
        """
        获取用户的详细信息
        :param userid:
        :return:
        """
        _params = {
            "userid": userid
        }
        ret, response = self.getRequest("https://qyapi.weixin.qq.com/cgi-bin/user/get", _params)
        if ret:
            return response
        return None

    def UserCreate(self, userid: str, name: str, mobile: str, gender: int, position: str="", telephone: str="", department: int=1, is_leader: int = 0):
        """
        创建企业成员
        :param userid:
        :param name:
        :param mobile:
        :param position:
        :param telephone:
        :param department:
        :return:
        """
        _params = {
            "userid": userid,
            "name": name,
            "mobile": mobile,
            "gender": gender,
            "telephone": telephone,
            "position": position,
            "department": department,
            "is_leader_in_dept": 1 if is_leader is 1 else 0
        }
        ret, _ = self.postRequest("https://qyapi.weixin.qq.com/cgi-bin/user/create", _params)
        return ret

    def UserUpdate(self, userid: str, **kwargs):
        """
        更新企业成员信息
        :param userid:
        :param name:
        :param mobile:
        :param telephone:
        :param position:
        :param department:
        :return:
        """
        arg_list = ["name", "mobile", "gender", "position", "telephone", "department", "is_leader"]
        _params = {
            "userid": userid,
        }
        for _prop in arg_list:
            if _prop in kwargs:
                _val = kwargs.get(_prop)
                _params[_prop] = _val

        ret, response = self.postRequest("https://qyapi.weixin.qq.com/cgi-bin/user/update", _params)
        return ret, response.get("errmsg")

    def UserDelete(self, userid):
        """
        删除成员
        :param userid:
        :return:
        """
        params = {
            "userid": userid
        }
        ret, _ = self.getRequest("https://qyapi.weixin.qq.com/cgi-bin/user/delete", params)
        return ret

    def DepartmentList(self, pid: int = 1):
        """
        获取部门列表
        :param pid:
        :return:
        """
        _params = {
            "id": pid
        }
        ret, response = self.getRequest("https://qyapi.weixin.qq.com/cgi-bin/department/list", _params)
        if ret:
            return response.get("department")
        return None

    def DepartmentCreate(self, name, parentid:int=1, order: int=0):
        """
        创建部门
        :param name:
        :param parentid:
        :param order:
        :return:
        """
        _params = {
            "name": name,
            "parentid": parentid,
            # "order": order
        }
        ret, response = self.postRequest("https://qyapi.weixin.qq.com/cgi-bin/department/create", _params)
        if ret:
            return response.get("id")
        return None

    def DepartmentUpdate(self, id, **kwargs):
        """
        更新部门信息
        :param id:
        :param kwargs:
        :return:
        """
        _prop_list = ["name", "name_en", "parentid"]
        _params = {
            "id": id,
        }
        for _prop in _prop_list:
            if _prop in kwargs:
                _params[_prop] = kwargs.get(_prop)
        ret, _ = self.postRequest("https://qyapi.weixin.qq.com/cgi-bin/department/update", _params)
        return ret

    def DepartmentDelete(self, id):
        """
        删除部门
        :param id:
        :return:
        """
        _params = {
            "id": id
        }
        ret, _ = self.getRequest("https://qyapi.weixin.qq.com/cgi-bin/department/delete", _params)
        return ret

if "__main__" == __name__:
    # _refreshAccessToken("wx1ac9c673f281add6", "GTTNCSIDw96JP0HqewrRwQ4Jw-7SpWfDAFJb4IoHNCg")
    # GetAccessToken("wx1ac9c673f281add6", "GTTNCSIDw96JP0HqewrRwQ4Jw-7SpWfDAFJb4IoHNCg")
    client = QywxClient("wx1ac9c673f281add6", "ghmdKl8bQZYS2cyXTTfk9rH4fnzDSBRqMwo0PFzManE")
    # client.UserDelete("mardini")
    # client.createDepartment("侧1")
    # print(client.UserList(2, 1, True))
    #print(client.DepartmentUpdate(4, name="2号上级"))
    print(client.DepartmentDelete(5))