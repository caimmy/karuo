# _*_ coding: utf-8 _*_
"""
-------------------------------------------------
@File Name： functions
@Description:
@Author: caimmy
@date： 2020/7/22 16:31
-------------------------------------------------
Change Activity:

-------------------------------------------------
"""
import json
from base64 import b64encode
from .base import ApiRequestBase, ACCEPTION_CONFIDENCE, LIVENESS_CONTROL

class FacerelAiTool(ApiRequestBase):
    def FaceMatch(self, facefirst: str, facesecend: str, live_control=True):
        """
        两张脸进行相似度比较
        :param facefirst: 图1的路径
        :param facesecend: 图2的路径
        :param live_control: 是否进行活体检测
        :return: bool, str  是否一致， 接口原因
        """
        check_match = False
        msg = "general"
        with open(facefirst, "rb") as img_first, open(facesecend, "rb") as img_second:
            params = [
                {
                    "image": b64encode(img_first.read()).decode("utf-8"),
                    "image_type": "BASE64",
                    "face_type": "LIVE",
                    "quality_control": "LOW",
                    "liveness_control": LIVENESS_CONTROL if live_control else "NONE"
                },
                {
                    "image": b64encode(img_second.read()).decode("utf-8"),
                    "image_type": "BASE64",
                    "face_type": "LIVE",
                    "quality_control": "LOW",
                    "liveness_control": LIVENESS_CONTROL if live_control else "NONE"
                }
            ]
            result = self._sendApiRequest("https://aip.baidubce.com/rest/2.0/face/v3/match", json.dumps(params))
            if result:
                if 0 == result.get("code"):
                    check_match = True if result.get("origin").get("score") > ACCEPTION_CONFIDENCE else False
                else:
                    msg = result.get("msg")
            return check_match, msg

    def FaceLibraryQuery(self, user_id: str, group_id: str = "@ALL"):
        """
        人脸库查询，查询人脸的信息
        :param user_id:
        :param group_id:
        :return: dict
        """
        ret_result = False

        _param = {
            "user_id": user_id,
            "group_id": group_id
        }
        ret_result = self._sendApiRequest("https://aip.baidubce.com/rest/2.0/face/v3/faceset/user/get", params=_param)

        return ret_result



    def FaceLibraryAdd(self, face: str, group_id: str, user_id: str, user_info: str, live_control=True):
        """
        人脸库管理 - 添加人脸
        :param face: 人脸图片文件路径
        :param group_id: 组编号
        :param user_id: 人员编号
        :param user_info: 人员信息
        :param live_control: 是否进行活体检测
        :return: bool
        """
        _image_type = "URL" if face.lower().startswith("http") else "BASE64"
        _img_content = face
        if _image_type == "BASE64":
            with open(face, "rb") as f:
                _img_content = b64encode(f.read()).decode("utf-8")
        _param = {
            "image": _img_content,
            "image_type": _image_type,
            "group_id": group_id,
            "user_id": user_id,
            "user_info": user_info,
            "quality_control": "NORMAL",
            "liveness_control": LIVENESS_CONTROL if live_control else "NONE"
        }

        result = self._sendApiRequest("https://aip.baidubce.com/rest/2.0/face/v3/faceset/user/add", params=_param)
        ret_oper = True if result and 0 == result.get("code") else False
        return ret_oper, result

    def FaceLibraryUpdate(self, face: str, group_id: str, user_id: str, user_info: str, live_control=True):
        """
        人脸库管理 - 更新人脸
        :param face:
        :param group_id:
        :param user_id:
        :param user_info:
        :param live_control:
        :return: bool, origin_result
        """
        _image_type = "URL" if face.lower().startswith("http") else "BASE64"
        _img_content = face
        if _image_type == "BASE64":
            with open(face, "rb") as f:
                _img_content = b64encode(f.read()).decode("utf-8")
        _param = {
            "image": _img_content,
            "image_type": _image_type,
            "group_id": group_id,
            "user_id": user_id,
            "user_info": user_info,
            "quality_control": "NORMAL",
            "liveness_control": LIVENESS_CONTROL if live_control else "NONE"
        }
        result = self._sendApiRequest("https://aip.baidubce.com/rest/2.0/face/v3/faceset/user/update", params=_param)
        ret_oper = True if result and 0 == result.get("code") else False
        return ret_oper, result

    def FaceLibraryDelete(self, user_id: str, group_id: str, face_token: str):
        """
        人脸库管理 - 删除
        :param user_id:
        :param group_id:
        :param face_token:
        :return:
        """
        _param = {
            "user_id": user_id,
            "group_id": group_id,
            "face_token": face_token
        }
        result = self._sendApiRequest("https://aip.baidubce.com/rest/2.0/face/v3/faceset/face/delete", params=_param)
        ret_oper = True if 0 == result.get("code") else False
        return ret_oper, result


    def FaceLibrarySearch(self, face, group_id_list: list, live_control: bool = True, user_id: str = "", max_user_num: int = 1):
        """
        人脸库 - 搜索
        :param face:
        :param group_id_list:
        :param live_control:
        :return:
        """
        _image_type = "URL" if face.lower().startswith("http") else "BASE64"
        _img_content = face
        if _image_type == "BASE64":
            with open(face, "rb") as f:
                _img_content = b64encode(f.read()).decode("utf-8")
        _param = {
            "image": _img_content,
            "image_type": _image_type,
            "group_id_list": ",".join(group_id_list) if 0 < len(group_id_list) else "",
            "quality_control": "NORMAL",
            "liveness_control": LIVENESS_CONTROL if live_control else "NONE",
            #"user_id": user_id,
            "max_user_num": max_user_num
        }
        result = self._sendApiRequest("https://aip.baidubce.com/rest/2.0/face/v3/search", params=_param)
        ret_oper = True if 0 == result.get("code") else False
        return ret_oper, result