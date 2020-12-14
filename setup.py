# _*_ coding: utf-8 _*_
"""
-------------------------------------------------
@File Name： setup
@Description:
@Author: caimmy
@date： 2019/10/22 12:35
-------------------------------------------------
Change Activity:

-------------------------------------------------
"""
from setuptools import setup, find_packages
from karuo import __version__

setup(
    name="karuo",
    version=__version__,
    keywords=["helpers", "tools", "widgets"],
    description="collection of some tools",
    long_description="collection of tools",
    license="MIT Licence",

    url="https://github.com/caimmy/karuo",
    author="caimmy",
    author_email="caimmy@hotmail.com",

    packages=find_packages(),
    include_package_data=True,
    platforms="any",
    install_requires=['requests', 'pycryptodome', 'requests_toolbelt']
)
