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
import base64
import re
from enum import Enum
from urllib.parse import urlencode
from random import randint
from .WXBizMsgCrypt import WXBizMsgCrypt, SHA1
from .helper import QywxXMLParser, QywxResponseGeneral
from karuo.helpers.char_helper import ensureString

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
            _exp_timestamp = int(
                time.time()) + (_expires_in - 300 if _expires_in > 300 else _expires_in)
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
    def __init__(self, corpid: str, corpsecret: str, agentid: str = "", token: str = "", aeskey: str = ""):
        self._corpid = corpid
        self._corpsecret = corpsecret
        self._agentid = agentid
        self._token = token
        self._aeskey = aeskey
        # 初始化访问口令及访问口令过期时间
        self._access_token, self._token_exptm = GetAccessToken(
            self._corpid, self._corpsecret)

    def _getAccessToken(self):
        if int(time.time()) > self._token_exptm or not self._access_token:
            # 如果口令过期或者没有口令，则通过服务器刷新
            self._access_token, self._token_exptm = GetAccessToken(
                self._corpid, self._corpsecret)
        return self._access_token

    def postRequest(self, url: str, params: dict):
        """
        :param url:
        :param params:
        :return:
        """
        _url = f"{url}?access_token={self._getAccessToken()}"
        try:
            _response = requests.post(_url, bytes(
                json.dumps(params, ensure_ascii=False), "utf-8"))
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
        ret_check = True if "errcode" in response and 0 == response.get(
            "errcode") else False
        return ret_check, response

    def _loadSendmsgParams(self, agentid: str, msgtype: str, args: dict) -> dict:
        """
        针对发送消息请求，构造基本请求参数
        """
        touser = args.get("touser") if "touser" in args else []
        toparty = args.get("toparty") if "toparty" in args else []
        totag = args.get("totag") if "totag" in args else []
        safe = args.get("safe") if "safe" in args else 0
        _params = {
            "touser": "|".join(touser),
            "toparty": "|".join(toparty),
            "totag": "|".join(totag),
            "msgtype": msgtype,
            "agentid": agentid,
            "safe": safe,
            "enable_id_trans": 0,
            "enable_duplicate_check": 0,
            "duplicate_check_interval": 1800
        }

        return _params

class DocSpaceACL(Enum):
    '''
    文档空间访问权限枚举
    '''
    READONLY    = 1
    EDITABLE    = 2
    PREVIEW     = 4

class MicroDocumentType(Enum):
    '''
    微文档类型
    '''
    DIRECTORY   = 1     # 目录
    DOC         = 3     # 微文档
    EXCEL       = 4     # 表格
    COLLECT     = 5     # 收集表

class QywxClient(_QywxBase):
    """
    __init__ (self, corpid: str, corpsecret: str, agentid:str="", token:str="", aeskey:str="")
    """

    def CallbackEchoStr(self, token: str, aeskey: str, msg_signature: str, timestamp: str, nonce: str, echostr: str) -> str:
        """
        设置回调时解密响应口令
        在设置应用回调地址时使用
        @return str
        """
        wxcpt = WXBizMsgCrypt(token, aeskey, self._corpid)
        ret, sEchoStr = wxcpt.VerifyURL(
            msg_signature, timestamp, nonce, echostr)
        return sEchoStr if 0 == ret else None

    def CallbackEchoStrWithGetParams(self, token: str, aeskey: str, getparams: dict):
        """
        回调时从dict获取解密参数
        """
        return self.CallbackEchoStr(token, aeskey, ensureString(getparams.get("msg_signature")),
                                    ensureString(getparams.get("timestamp")), ensureString(getparams.get("nonce")), ensureString(getparams.get("echostr")))

    def ParseUploadMessage(self, params: dict, msgbody: str):
        """
        解析微信上行到应用服务器的消息
        @params: dict 验证参数 msg_signature, timestamp, nonce
        @msgbody: str 待解密消息体 echostr, 
        """
        ret_msg_struct = None
        sha1helper = SHA1()
        origin_encrypt_msg = QywxXMLParser.parseOriginEncryptMsg(msgbody)
        ret, check_sig = sha1helper.getSHA1(self._token, params.get(
            "timestamp"), params.get("nonce"), origin_encrypt_msg.Encrypt)
        if 0 == ret and check_sig == params.get("msg_signature"):
            # 提取加密数据字段
            str_callbackmsg = self.CallbackEchoStr(self._token, self._aeskey, params.get(
                "msg_signature"), params.get("timestamp"), params.get("nonce"), origin_encrypt_msg.Encrypt)
            if str_callbackmsg:
                ret_msg_struct = QywxXMLParser.parseCallbackMessage(
                    str_callbackmsg)
        return ret_msg_struct

    def ParseCallbackData(self, params: dict, msgbody: str):
        """
        解析微信服务器回调数据
        """
        ret_msg_struct = None
        sha1helper = SHA1()
        origin_encrypt_msg = QywxXMLParser.parseOriginEncryptMsg(msgbody)
        ret, check_sig = sha1helper.getSHA1(self._token, params.get(
            "timestamp"), params.get("nonce"), origin_encrypt_msg.Encrypt)
        if 0 == ret and check_sig == params.get("msg_signature"):
            # 提取加密数据字段
            str_callbackmsg = self.CallbackEchoStr(self._token, self._aeskey, params.get(
                "msg_signature"), params.get("timestamp"), params.get("nonce"), origin_encrypt_msg.Encrypt)
            if str_callbackmsg:
                ret_msg_struct = QywxXMLParser.parseNormalCallbackData(str_callbackmsg)
        return ret_msg_struct
    
    def ResponseTextMessage(self, msg:str, toUser:str, fromUser:str):
        """
        回复文本消息
        """
        xml_response = QywxResponseGeneral.ResponseXmlForText(toUser, fromUser, msg)
        return self.GenResponseMessage(xml_response, randint(10000, 99999))

    def GenResponseMessage(self, replyMsg: str, nonce: str) -> str:
        """
        生成回复消息
        """
        wxcpt = WXBizMsgCrypt(self._token, self._aeskey, self._corpid)
        _, ret_encrypt_xml = wxcpt.EncryptMsg(replyMsg, nonce)
        return ret_encrypt_xml

    def OauthRedirectUrl(self, url: str, state: str) -> str:
        """
        构造oauth认证跳转地址
        """
        ret_url = ""
        if url and state:
            ret_url = f"https://open.weixin.qq.com/connect/oauth2/authorize?appid={self._corpid}&redirect_uri={urllib.parse.quote(url)}&response_type=code&scope=snsapi_base&state={state}#wechat_redirect"
        return ret_url

    def SsoQrcodeRedirectUrl(self, agendid: str, url: str, state: str) -> str:
        """
        构造SSO登录地址
        """
        ret_url = ""
        if url and state:
            ret_url = f"https://open.work.weixin.qq.com/wwopen/sso/qrConnect?appid={self._corpid}&agentid={agendid}&redirect_uri={urllib.parse.quote(url)}&state={state}"
        return ret_url

    def OauthGetUserInfor(self, code: str):
        """
        从oauth认证传递的code置换用户编号
        """
        _params = {
            "code": code
        }
        return self.getRequest("https://qyapi.weixin.qq.com/cgi-bin/user/getuserinfo", _params)

    def CommunicationBook(self):
        """
        获取完整的通信录信息
        同时返回递归的全部部门和成员，分开显示
        """
        
        _d_res, _dep_list = self.DepartmentList()
        _u_res, _user_list = self.UserList(1, 1, True)
        if _d_res and _u_res:
            return True, {"dep": _dep_list, "user": _user_list}
        else:
            return False, None

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
        return self.getRequest(url, _params)
        

    def UserDetail(self, userid: str):
        """
        获取用户的详细信息
        :param userid:
        :return:
        """
        _params = {
            "userid": userid
        }
        return self.getRequest(
            "https://qyapi.weixin.qq.com/cgi-bin/user/get", _params)

    def UserCreate(self, userid: str, name: str, alias:str, mobile: str, email:str, gender: int, position: str = "", telephone: str = "", department: list = [], is_leader: list = [], invite=False):
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
            "alias": alias,
            "mobile": mobile,
            "email": email,
            "gender": gender,
            "telephone": telephone,
            "position": position,
            "to_invite": invite
        }
        if len(department) > 0:
            _params["department"] = department
        if len(is_leader) > 0:
            _params["is_leader_in_dept"] = is_leader
        return self.postRequest(
            "https://qyapi.weixin.qq.com/cgi-bin/user/create", _params)

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
        arg_list = ["name", "alias", "mobile", "gender", "position",
                    "telephone", "department", "is_leader"]
        _params = {
            "userid": userid,
        }
        for _prop in arg_list:
            if _prop in kwargs:
                _val = kwargs.get(_prop)
                _params[_prop] = _val

        return self.postRequest(
            "https://qyapi.weixin.qq.com/cgi-bin/user/update", _params)

    def UserDelete(self, userid):
        """
        删除成员
        :param userid:
        :return:
        """
        params = {
            "userid": userid
        }
        return self.getRequest(
            "https://qyapi.weixin.qq.com/cgi-bin/user/delete", params)

    def DepartmentList(self, pid: int = 1):
        """
        获取部门列表
        :param pid:
        :return:
        """
        _params = {
            "id": pid
        }
        return self.getRequest(
            "https://qyapi.weixin.qq.com/cgi-bin/department/list", _params)
        

    def DepartmentCreate(self, name, parentid: int = 1, order: int = 0):
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
        }
        if isinstance(order, int) and order > 0:
            _params["order"] = order

        return self.postRequest(
            "https://qyapi.weixin.qq.com/cgi-bin/department/create", _params)

    def DepartmentUpdate(self, id, **kwargs):
        """
        更新部门信息
        :param id:
        :param kwargs:
        :return:
        """
        _prop_list = ["name", "name_en", "parentid", "order"]
        _params = {
            "id": id,
        }
        for _prop in _prop_list:
            if _prop in kwargs:
                _params[_prop] = kwargs.get(_prop)
        return self.postRequest(
            "https://qyapi.weixin.qq.com/cgi-bin/department/update", _params)

    def DepartmentDelete(self, id):
        """
        删除部门
        :param id:
        :return:
        """
        _params = {
            "id": id
        }
        return self.getRequest(
            "https://qyapi.weixin.qq.com/cgi-bin/department/delete", _params)

    def MsgSendText(self, agentid: int, content: str, **kwargs):
        """
        发送文本消息
        """
        _params = self._loadSendmsgParams(agentid, "text", kwargs)
        _params["text"] = {
            "content": content
        }

        return self.postRequest("https://qyapi.weixin.qq.com/cgi-bin/message/send", params=_params)

    def MsgSendImage(self, agentid: int, img_content, **kwargs):
        """
        发送图片消息
        首先调用 [上传临时素材接口] 获取图片的media_id，
        然后再发送消息
        """
        media_id = self.UploadTempMedia("image", content=img_content)
        if media_id:
            _params = self._loadSendmsgParams(agentid, "image", kwargs)
            _params["image"] = {
                "media_id": media_id
            }
            return self.postRequest("https://qyapi.weixin.qq.com/cgi-bin/message/send", params=_params)
        else:
            return {
                "errcode": -1,
                "errmsg": "没有获取到有效的media_id"
            }

    def MsgSendTextCard(self, agentid: int, title: str, description: str, url: str, btntxt: str = "更多", **kwargs):
        """
        发送文本卡片消息
        """
        _params = self._loadSendmsgParams(agentid, "textcard", kwargs)
        _params["textcard"] = {
            "title": title,
            "description": description,
            "url": url,
            "btntxt": btntxt
        }
        return self.postRequest("https://qyapi.weixin.qq.com/cgi-bin/message/send", params=_params)

    def MsgSendPictureCard(self, agentid: int, title: str, description: str, url: str, picurl: str, **kwargs):
        """
        发送图文卡片消息
        """
        _params = self._loadSendmsgParams(agentid, "news", kwargs)
        _params["news"] = {
            "articles": [
                {
                    "title": title,
                    "description": description,
                    "url": url,
                    "picurl": picurl
                }
            ]
        }

        return self.postRequest("https://qyapi.weixin.qq.com/cgi-bin/message/send", params=_params)

    def MsgSendMarkdown(self, agentid: int, markdown: str, **kwargs):
        """
        发送markdown消息
        """
        _params = self._loadSendmsgParams(agentid, "markdown", kwargs)
        _params["markdown"] = {
            "content": markdown
        }

        return self.postRequest("https://qyapi.weixin.qq.com/cgi-bin/message/send", params=_params)

    ######  辅助功能相关
    
    def UploadTempMedia(self, filetype, filepath=None, content=None):
        """
        :param filepath 图片文件路径
        :param content 图片文件内容 io.BytesIO
        上传临时素材
        """
        _ret_media_id = None
        from requests_toolbelt import MultipartEncoder
        form_data = MultipartEncoder(
            fields={"filename": ("media", open(filepath, "rb") if filepath else content, "image/png")}
        )
        _upload_url = f"https://qyapi.weixin.qq.com/cgi-bin/media/upload?access_token={self._getAccessToken()}&type={filetype}"
        _upload_res = requests.post(_upload_url, data=form_data, headers={'Content-Type': form_data.content_type})
        try:
            _ret_data = _upload_res.json()
            if 0 == _ret_data.get("errcode"):
                _ret_media_id = _ret_data.get("media_id")
        except Exception as e:
            _ret_media_id = ""
        return _ret_media_id

    def DownloadTempMedia(self, media_id: str, store_path: str, ext_name: str=""):
        """
        下载微信临时文件
        :param media_id str 资源文件编号
        :param store_file str 暂存的本地文件fullpath
        """
        ret, msg = False, "gen"
        
        try:
            if os.path.isdir(store_path):
                _download_url = f"https://qyapi.weixin.qq.com/cgi-bin/media/get?access_token={self._getAccessToken()}&media_id={media_id}"
                response = requests.get(_download_url, stream=True)
                if response.ok:
                    if ext_name:
                        _ext_name = ext_name if ext_name.startswith(".") else ("." + ext_name)
                    else:
                        response_headers = dict(response.headers)
                        ext_suggests = re.findall("(\.\w+)", response_headers.get("Content-disposition"))
                        _ext_name = ext_suggests[0] if ext_suggests else ".data"
                    store_file = f"{media_id}{_ext_name}"
                    with open(store_file, 'ab') as wf:
                        for chunk in response.iter_content(chunk_size=1024000):
                            if chunk:
                                wf.write(chunk)
                        ret = True
            else:
                msg = "store_path invalid"
        except Exception as e:
            msg = str(e)
        finally:
            return ret, msg
            

    ######  工作日程相关
    def CreateSchedule(self, organizer:str, start_time:int, end_time:int, attendees:list, summary:str, description:str, location:str, remind_pre_sec:int=3600):
        """
        创建日程
        :param organizer str 组织者日程
        :param start_time int 日程开始时间戳
        :param end_time int 日程结束时间戳
        :param attendees list 日程参与者列表
        :param summary str 日程标题
        :param description str 日程描述
        :param location str 日程地址
        :param remind_pre_sec 提前多少秒通知
        """
        _params = {
            "schedule": {
                "organizer": organizer,
                "start_time": start_time,
                "end_time": end_time,
                "attendees": [
                    {"userid": uid, "readonly": 0} for uid in attendees
                ],
                "summary": summary,
                "description": description,
                "reminders": {
                    "is_remind": 1,
                    "remind_before_event_secs": remind_pre_sec,
                    "is_repeat": 0,
                    "repeat_type": 7
                },
                "location": location,
                # "cal_id": "wcjgewCwAAqeJcPI1d8Pwbjt7nttzAAA"
            }
        }

        return self.postRequest("https://qyapi.weixin.qq.com/cgi-bin/oa/schedule/add", params=_params)

    def CreateScheduleComplex(self, organizer:str, start_time:int, end_time:int, attendees:list, summary:str, description:str, location:str, 
        is_remaind=1, is_repeat=1, remind_before_event_secs=0, remind_repeat_type=7, remind_repeat_until=0):
        """
        创建日程
        :param organizer str 组织者日程
        :param start_time int 日程开始时间戳
        :param end_time int 日程结束时间戳
        :param attendees list 日程参与者列表
        :param summary str 日程标题
        :param description str 日程描述
        :param location str 日程地址
        :param remind_pre_sec 提前多少秒通知
        """
        _params = {
            "schedule": {
                "organizer": organizer,
                "start_time": start_time,
                "end_time": end_time,
                "attendees": [
                    {"userid": uid, "readonly": 0} for uid in attendees
                ],
                "summary": summary,
                "description": description,
                "reminders": {
                    "is_remind": is_remaind,
                    "remind_before_event_secs": remind_before_event_secs,
                    "is_repeat": is_repeat,
                    "repeat_type": remind_repeat_type,
                    "repeat_until": remind_repeat_until
                },
                "location": location,
                # "cal_id": "wcjgewCwAAqeJcPI1d8Pwbjt7nttzAAA"
            }
        }

        return self.postRequest("https://qyapi.weixin.qq.com/cgi-bin/oa/schedule/add", params=_params)

    def UpdateSchedule(self, organizer:str, schedule_id:str, start_time:int, end_time:int, attendees: list, summary: str, description:str, location:str, remind_pre_sec:int=3600):
        """
        更新日程
        """
        _params = {
            "schedule": {
                "organizer": organizer,
                "schedule_id": schedule_id,
                "start_time": start_time,
                "end_time": end_time,
                "attendees": [
                    {"userid": uid, "readonly": 0} for uid in attendees
                ],
                "summary": summary,
                "description": description,
                "reminders": {
                    "is_remind": 1,
                    "remind_before_event_secs": remind_pre_sec,
                    "is_repeat": 0,
                    "repeat_type": 7
                },
                "location": location,
                # "cal_id": "wcjgewCwAAqeJcPI1d8Pwbjt7nttzAAA"
            }
        }
        return self.postRequest("https://qyapi.weixin.qq.com/cgi-bin/oa/schedule/update", params=_params)

    def DeleteSchedule(self, schedule_id: str):
        """
        取消日程
        """
        _params = {
            "schedule_id": schedule_id
        }
        return self.postRequest("https://qyapi.weixin.qq.com/cgi-bin/oa/schedule/del", params=_params)


    ### 微盘空间管理相关
    # 创建微盘空间
    def DocSpaceCreate(self, user_id: str, spacename: str, user_list: list, dep_list: list, defaultAuth=4):
        """
        创建微盘空间
        :param defaultAuth int 默认权限 成员权限 1:可下载 2:可编辑 4:可预览（仅专业版企业可设置）
        """
        _user_info_list = [{
            "type": 1,
            "userid": uid,
            "auth": defaultAuth
        } for uid in user_list]
        _dep_info_list = [{
            "type": 2,
            "departmentid": did,
            "auth": defaultAuth
        } for did in dep_list]
        _params = {
            "userid": user_id,
            "space_name": spacename,
            "auth_info": _user_info_list + _dep_info_list
        }
        return self.postRequest("https://qyapi.weixin.qq.com/cgi-bin/wedrive/space_create", params=_params)

    ### 重命名微盘空间
    def DocSpaceRename(self, userid: str, spaceid: str, spacename: str):
        '''
        重命名空间
        :param userid str 操作者编号
        :param spaceid str 被重命名空间的编号
        :param spacename str 调整后的空间名称
        '''
        _params = {
            "userid": userid,
            "spaceid": spaceid,
            "space_name": spacename
        }
        return self.postRequest("https://qyapi.weixin.qq.com/cgi-bin/wedrive/space_rename", params=_params)

    # 解散微盘空间
    def DocSpaceDismiss(self, userid: str, spaceid: str):
        '''
        解散空间
        :param userid str 操作者编号
        :param spaceid str 需解散空间的编号
        '''
        _params = {
            "userid": userid,
            "spaceid": spaceid
        }
        return self.postRequest("https://qyapi.weixin.qq.com/cgi-bin/wedrive/space_dismiss", params=_params)
    
    # 获取微盘空间信息
    def DocSpaceGetInfor(self, userid: str, spaceid: str):
        '''
        获取空间信息
        :param userid str 操作者编号
        :param spaceid str 空间编号
        '''
        _params = {
            "userid": userid,
            "spaceid": spaceid
        }
        return self.postRequest("https://qyapi.weixin.qq.com/cgi-bin/wedrive/space_info", params=_params)

    def DocSpaceAddACL(self, userid: str, spaceid: str, user_list: list, dep_list: list, auth_type: DocSpaceACL):
        '''
        增加文档空间ACL访问权限
        '''
        _user_info_list = [{
            "type": 1,
            "userid": uid,
            "auth": auth_type.value
        } for uid in user_list]
        _dep_info_list = [{
            "type": 2,
            "departmentid": did,
            "auth": defaultAuth.value
        } for did in dep_list]
        _params = {
            "userid": userid,
            "spaceid": spaceid,
            "auth_info": _user_info_list + _dep_info_list
        }
        return self.postRequest("https://qyapi.weixin.qq.com/cgi-bin/wedrive/space_acl_add", params=_params)

    def DocSpaceDeleteACL(self, userid: str, spaceid: str, user_list:list, dep_list: list):
        '''
        删除文档空间ACL访问权限
        '''
        _user_info_list = [{
            "type": 1,
            "userid": uid,
        } for uid in user_list]
        _dep_info_list = [{
            "type": 2,
            "departmentid": did,
        } for did in dep_list]
        _params = {
            "userid": userid,
            "spaceid": spaceid,
            "auth_info": _user_info_list + _dep_info_list
        }
        return self.postRequest("https://qyapi.weixin.qq.com/cgi-bin/wedrive/space_acl_del", params=_params)

    def DocSpaceSetting(self, userid: str, spaceid: str, add_member_only_admin: bool=True, enable_share_url: bool=False, share_url_no_approve:bool=False, share_url_no_approve_default_auth:DocSpaceACL=DocSpaceACL.READONLY):
        '''
        设置共享空间权限
        :param userid str 操作者账号
        :param spaceid str 空间编号
        :param add_member_only_admin bool 是否仅管理员可改变设置
        :param enable_share_url bool 是否启用成员邀请链接
        :param share_url_no_approve bool 是否通过链接加入空间无需审批
        :param share_url_no_approve_default_auth int 邀请链接默认权限 
        '''
        _params = {
            "userid": userid,
            "spaceid": spaceid,
            "add_member_only_admin": add_member_only_admin,
            "enable_share_url": enable_share_url,
            "share_url_no_approve": share_url_no_approve,
            "share_url_no_approve_default_auth": share_url_no_approve_default_auth.value
        }
        return self.postRequest("https://qyapi.weixin.qq.com/cgi-bin/wedrive/space_setting", params=_params)

    ### 微文档管理
    def DocSpaceGetFilesList(self, userid: str, spaceid: str, fatherid: str='', sort_type: int=6, start: int=0, limit: int=100):
        '''
        获取文件列表
        '''
        _father_id = fatherid if fatherid else spaceid
        _params = {
            "userid": userid,
            "spaceid": spaceid,
            "fatherid": _father_id,
            "sort_type": sort_type,
            "start": start,
            "limit": limit
        }
        return self.postRequest("https://qyapi.weixin.qq.com/cgi-bin/wedrive/file_list", params=_params)

    def DocSpaceUploadFileContent(self, userid: str, spaceid: str, filename: str, file_base64_content: str, fatherid: str=''):
        '''
        按内容上传文件
        :param userid str 操作者编号
        :param spaceid str 文件存放的空间编号
        :param filename str 文件名
        :param file_base64_content str 文件内容的base64内容
        :param fatherid str 目录名称
        '''
        _father_id = fatherid if fatherid else spaceid
        _params = {
            "userid": userid,
            "spaceid": spaceid,
            "fatherid": _father_id,
            "file_name": filename,
            "file_base64_content": file_base64_content
        }
        return self.postRequest("https://qyapi.weixin.qq.com/cgi-bin/wedrive/file_upload", params=_params)

    def DocSpaceUploadFile(self, userid: str, spaceid: str, filepath: str, filename:str, fatherid: str=''):
        '''
        上传文件
        '''
        try:
            with open(filepath, 'rb') as f:
                _c = f.read()
                _content = base64.b64encode(_c)
                return self.DocSpaceUploadFileContent(userid, spaceid, filename, _content.decode("utf-8"), fatherid)
        except Exception as e:
            return False, {'errcode': -1, 'errmsg': str(e)}

    def DocSpaceDeleteFile(self, userid: str, fileid: list):
        '''
        删除文件
        :param userid str 操作者编号
        :param fileid list[str] 被删除文件编号列表
        '''
        _params = {
            "userid": userid,
            "fileid": fileid
        }
        return self.postRequest("https://qyapi.weixin.qq.com/cgi-bin/wedrive/file_delete", params=_params)

    def DocSpaceDeleteFileAccess(self, userid: str, fileid: str, auth_info: list):
        '''
        删除指定文件的指定人/部门
        :param userid str 操作者编号
        :param fileid str 目标文件编号
        :param auth_info obj[] 被移除的成员信息
        @auth_info :
        "auth_info": [{
            "type": 1,
            "userid": "USERID1"
        }, {
            "type": 2,
            "departmentid": DEPARTMENT_ID1    
        }]
        *** type	uint32	必填	成员类型 1:个人 2:部门
        *** userid	string	根据type必填	成员userid,字符串 (type为1时填写)
        *** departmentid	uint32	根据type必填	部门departmentid, 32位整型范围是[0, 2^32) (type为2时填写)
        '''
        _params = {
            "userid": userid,
            "fileid": fileid,
            "auth_info": auth_info
        }
        return self.postRequest("https://qyapi.weixin.qq.com/cgi-bin/wedrive/file_acl_del", params=_params)
    
    def DocSpaceCreateMicroDocument(self, userid: str, spaceid: str, filename: str, filetype: MicroDocumentType, fatherid=''):
        '''
        创建微文档
        '''
        _params = {
            "userid": userid,
            "spaceid": spaceid,
            "fatherid": fatherid if fatherid else spaceid,
            "file_type": filetype.value,
            "file_name": filename
        }
        return self.postRequest("https://qyapi.weixin.qq.com/cgi-bin/wedrive/file_create", params=_params)

    def DocSpaceFileShareUrl(self, userid: str, fileid: str):
        """
        获取文件的分享链接
        """
        _params = {
            "userid": userid,
            "fileid": fileid
        }
        return self.postRequest("https://qyapi.weixin.qq.com/cgi-bin/wedrive/file_share", params=_params)