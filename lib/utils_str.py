#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright (c) 2018 All Rights Reserved
# 

"""
File: utils_str.py
Author: songchuan.zhou
Date: 2018/7/31 10
"""


def str_hex_to_int(inputstr):
    """
    6969-238F-F 转化为 int 下划线形式
    :param inputstr:
    :return:
    """
    result = '_'.join([str(int(item, 16)) for item in inputstr.split('-')])
    return result


def is_number(s):
    """判断一个字符串是否是数字（比如1或一），是则返回True"""
    try:
        float(s)
        return True
    except ValueError:
        return False


def parse_url(url_string):
    """
    将url解析成一个url object，可选的连接参数会set给kwargs
    典型 url的格式： {scheme}://{username}:{password}@{hostname}:{port}{path}?{query}#{fragment}
    请注意， 所有可选参数的value类型均为str或int，使用时如对参数类型有要求，请务必根据情况转换
    :param url_string: 如 mysql://user:passwd@host:port/database?other=1&option=2
    :return:
    """
    from urlparse import urlparse, parse_qs
    uri = urlparse(url_string)

    setattr(uri, 'database', uri.path[1:])
    setattr(uri, 'server', "%s:%s" % (uri.hostname, uri.port))
    kwargs = dict([(k, int(v[0]) if is_number(v[0]) else v[0]) for k, v in parse_qs(uri.query).items()])
    setattr(uri, 'kwargs', kwargs)
    return uri

