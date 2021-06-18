#!/usr/bin/env python
# -*- coding: utf-8 -*-
########################################################################
# 
# Copyright (c) 2017 alibaba-inc. All Rights Reserved
# 
########################################################################

"""
异常定义模板，包含常用的异常类型定义。

File: exceptions.py
Author: mushi(mushi.hgx@alibaba-inc.com)
Date: 2017/12/25 21:08:30
"""


class ENotImplement(Exception):
    """
    调用了纯虚函数
    """


class EMissingParam(Exception):
    """
    缺少参数
    """


class EUnknownRequest(Exception):
    """
    未知请求
    """


class EFailedRequest(Exception):
    """
    请求失败
    """


class EInvalidOperation(Exception):
    """
    错误操作，通常指错误的请求或操作
    """


class EInvalidParam(Exception):
    """
    参数错误
    """


class EInvalidData(Exception):
    """
    数据不合法，解析数据失败
    """


class EExisted(Exception):
    """
    新建的资源已经存在
    """


class ENotExist(Exception):
    """
    请求的资源不存在
    """


class EUnknownException(Exception):
    """
    未知异常
    """


class ENeedNoOperation(Exception):
    """
    无需操作
    """


class EUserNotLogin(Exception):
    """
    获取不到用户信息
    """


class EClockPhasesTooLarge(Exception):
    """
    时钟误差过大
    """


class ESignNotMatch(Exception):
    """
    签名校验失败
    """


class ESqlSyntax(Exception):
    """
    数据库SQL错误
    """


class EUnsupported(Exception):
    """
    不支持类型
    """


class EExpired(Exception):
    """
    cache已过期
    """


class EInvalidConfig(Exception):
    """
    配置不合法
    """


class EMaxRetryReached(Exception):
    """
    达到最大重试次数
    """


class TimeoutError(Exception):
    """
    函数执行时间超过设定的超时时间
    """
