#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright (c) 2018 alibaba-inc. All Rights Reserved
# 

"""
File: xiaoqu.py
Author: wang.gaofei(wang.gaofei@alibaba-inc.com)
Date: 2021/6/19
"""
import json


class XiaoQu():
    xiaoqu_id = 0
    area = ""
    name = ""
    turnover = ""  # 成交量
    price = 0  # 均价
    houses = 0  # 在售数量
    other = {}

if __name__ == '__main__':
    # xiaoqu = XiaoQu()
    # xiaoqu.area = "dongcheng"
    # xiaoqu.name = "name"
    # xiaoqu.price = 1
    # xiaoqu.other = {"a":1}
    # print xiaoqu.__dict__
    a = """{"price": 1, "other": {"a": 1}, "name": "name", "area": "dongcheng"}"""
    xiaoqu = XiaoQu()
    json.loads(a)

    xiaoqu.__dict__ = json.loads(a)
    print xiaoqu
    print xiaoqu.other
    print xiaoqu.name
    print xiaoqu.area

