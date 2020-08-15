# _*_ coding: utf-8 _*_
"""
-------------------------------------------------
@File Name： test_normal
@Description:
@Author: caimmy
@date： 2020/7/30 11:26
-------------------------------------------------
Change Activity:

-------------------------------------------------
"""

from unittest import TestCase
import shortuuid
import datetime
import xml.etree.ElementTree as ET
class NormalTest(TestCase):
    def testShortuuid(self):
        datas = []
        stm = datetime.datetime.now().strftime("%d:%H:%S")
        for i in range(200000):
            datas.append(shortuuid.uuid(name="abc"))
        etm = datetime.datetime.now().strftime("%d:%H:%S")
        print(datas)
        print(len(datas))
        print(stm, etm)

    def testXmlparse(self):
        print("")
        _c = """
        <?xml version="1.0"?>

<doc>

  <branch name="codingpy.com" hash="1cdf045c">

    text,source

  </branch>

  <branch name="release01" hash="f200013e">

    <sub-branch name="subrelease01">

      xml,sgml

    </sub-branch>

  </branch>

  <branch name="invalid">

  </branch>

</doc>
        """
        tree = ET.parse()