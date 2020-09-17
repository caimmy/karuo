# _*_ coding:utf-8 _*_

from time import time
import xml.sax

class OriginCallbackData(xml.sax.ContentHandler):
    """
    系统回调的原始数据，加密前
    """
    def __init__(self):
        super(OriginCallbackData, self).__init__()
        self._current_tag = None
        self.ToUserName = ""
        self.AgentID = ""
        self.Encrypt = ""


    def startElement(self, tag, attributes):
        self._current_tag = tag

    def characters(self, content):
        # if self.CurrentData == "ToUserName":
        if self._current_tag == "ToUserName":
            self.ToUserName += content
        elif self._current_tag == "AgentID":
            self.AgentID += content
        elif self._current_tag == "Encrypt":
            self.Encrypt += content

    def endElement(self, tag):
        self._current_tag = None


class BaseCallbackData(xml.sax.ContentHandler):
    """
    xml消息或事件回调
    """
    def __init__(self):
        super(BaseCallbackData, self).__init__()
        self._current_tag = None
    
    def startElement(self, tag, attributes):
        self._current_tag = tag

    def endElement(self, tag):
        self._current_tag = None
    
    def characters(self, content):
        if self._current_tag:
            if hasattr(self, self._current_tag):
                _val = getattr(self, self._current_tag)
                if isinstance(_val, str):
                    _val += content
                    setattr(self, self._current_tag, _val)

class NormalCallbackData(BaseCallbackData):
    def characters(self, content):
        if self._current_tag:
            setattr(self, self._current_tag, content)

class CallbackDataDict(BaseCallbackData):

    def __init__(self):
        super(CallbackDataDict, self).__init__()
        self._data = {}

    def characters(self, content):
        if self._current_tag:
            self._data[self._current_tag] = content

    def getData(self):
        return self._data 

    def __getattr__(self, key):
        if key in self._data:
            return self._data[key]
        else:
            return None

class CallbackMessage(BaseCallbackData):
    """
    回调的消息
    """
    def __init__(self):
        super(CallbackMessage, self).__init__()
        self._current_tag = None
        # TODO 
        # 定义消息数据字段
        self.ToUserName = ""
        self.FromUserName = ""
        self.CreateTime = ""
        self.MsgType = ""
        self.Content = ""
        self.MsgId = ""
        self.AgentID = ""
        self.PicUrl = ""
        self.MediaId = ""
        self.Format = ""
        self.ThumbMediaId = ""
        self.Location_X = ""
        self.Location_Y = ""
        self.Scale = ""
        self.Label = ""
        self.AppType = ""
        self.Title = ""
        self.Description = ""
        self.Url = ""
        self.Event = ""
        self.EventKey = ""
        self.Latitude = ""
        self.Longitude = ""
        self.Precision = ""
        self.ChangeType = ""
        self.Id = ""
        self.Name = ""
        self.ParentId = ""
        self.Order = ""
        self.TagId = ""
        self.AddUserItems = ""
        self.DelUserItems = ""
        self.AddPartyItems = ""
        self.DelPartyItems = ""
        self.ScanType = ""
        self.ScanResult = ""


class QywxXMLParser():
    @staticmethod
    def parseOriginEncryptMsg(xml_content:str)->OriginCallbackData:
        """
        解析原始推送消息，解密前
        """
        origin_xml_handler = OriginCallbackData()
        xml.sax.parseString(xml_content, origin_xml_handler)
        return origin_xml_handler

    @staticmethod
    def parseCallbackMessage(xml_content:str)->CallbackMessage:
        """
        解析消息或事件文本
        """
        callback_xml_handler = CallbackMessage()
        xml.sax.parseString(xml_content, callback_xml_handler)
        return callback_xml_handler

    @staticmethod
    def parseNormalCallbackData(xml_content:str) -> CallbackDataDict:
        callback_msg_handler = CallbackDataDict()
        xml.sax.parseString(xml_content, callback_msg_handler)
        return callback_msg_handler

class QywxResponseGeneral():
    """
    生成自动响应消息
    """
    @staticmethod
    def ResponseXmlForText(ToUserName:str, FromUserName:str, Content:str):
        """
        自动响应的文本消息
        """
        _TEXT_RESPONSE_TEMPLATE = """<xml><ToUserName><![CDATA[%(ToUserName)s]]></ToUserName><FromUserName><![CDATA[%(FromUserName)s]]></FromUserName><CreateTime>%(tm)d</CreateTime><MsgType><![CDATA[text]]></MsgType><Content><![CDATA[%(Content)s]]></Content></xml>"""
        _params = {
            "ToUserName": ToUserName,
            "FromUserName": FromUserName,
            "tm": int(time()),
            "Content": Content
        }
        return _TEXT_RESPONSE_TEMPLATE % _params


def test_origin_msg():
    h = b"""<xml> 
   <ToUserName><![CDATA[toUser]]></ToUserName>
   <AgentID><![CDATA[toAgentID]]></AgentID>
   <Encrypt><![CDATA[msg_encrypt]]></Encrypt>
</xml>"""
    data = QywxXMLParser.parseOriginEncryptMsg(h)
    print(data)

def test_callback_msg():
    h = b"""<xml>
   <ToUserName><![CDATA[toUser]]></ToUserName>
   <FromUserName><![CDATA[FromUser]]></FromUserName>
   <CreateTime>123456789</CreateTime>
   <MsgType><![CDATA[event]]></MsgType>
   <Event><![CDATA[LOCATION]]></Event>
   <Latitude>23.104</Latitude>
   <Longitude>113.320</Longitude>
   <Precision>65.000</Precision>
   <AgentID>1</AgentID>
   <AppType><![CDATA[wxwork]]></AppType>
</xml>"""
    data = QywxXMLParser.parseCallbackMessage(h)
    print(data)

if "__main__" == __name__:
    
    test_callback_msg()