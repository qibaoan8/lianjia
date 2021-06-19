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
import datetime
import json


class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, datetime.date):
            return obj.strftime("%Y-%m-%d")
        else:
            return json.JSONEncoder.default(self, obj)


class XiaoQu():

    def __init__(self):
        self.id = 0
        self.create_time = datetime.datetime.now()
        self.xiaoqu_id = 0
        self.area = ""
        self.area_2 = ""
        self.xiaoqu_name = ""
        self.build_year = 0
        self.turnover = ""  # 成交量
        self.price = 0  # 均价
        self.houses = 0  # 在售数量
        self.other = {}

    def __str__(self):
        return json.dumps(self.__dict__, ensure_ascii=False, cls=DateEncoder)


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
    print xiaoqu.xiaoqu_name
    print xiaoqu.area
    print xiaoqu
