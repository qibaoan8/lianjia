#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright (c) 2018 alibaba-inc. All Rights Reserved
# 

"""
File: model_table.py
Author: wang.gaofei(wang.gaofei@alibaba-inc.com)
Date: 2021/6/19
"""

from lib.models import BaseModel
from popo.house import House
from popo.xiaoqu import XiaoQu


class XiaoQuModel(BaseModel):
    """
    小区表
    """

    def __init__(self):
        super(XiaoQuModel, self).__init__()
        self.table = "xiaoqu"
        self.update_key = ["area", "area_2", "xiaoqu_name", "build_year", "turnover", "price", "houses", "other"]

    def json_to_object(self, _input):
        """ 将json 转换成对象 """
        if isinstance(_input, list):
            ret = []
            for i in _input:
                xiaoqu = XiaoQu()
                xiaoqu.__dict__ = i
                ret.append(xiaoqu)
            return ret
        elif isinstance(_input, dict):
            xiaoqu = XiaoQu()
            xiaoqu.__dict__ = _input
            return xiaoqu
        else:
            xiaoqu = XiaoQu()
            return xiaoqu

    def object_to_json(self, _input):
        """ 将对象 转换成json """
        if isinstance(_input, list):
            ret = []
            for i in _input:
                if isinstance(i, XiaoQu):
                    _json = i.__dict__
                    ret.append(_json)
            return ret
        elif isinstance(_input, XiaoQu):
            ret = _input.__dict__
            return ret
        else:
            return {}


class HouseModel(BaseModel):
    """
    房源表
    """

    def __init__(self):
        super(HouseModel, self).__init__()
        self.table = "house"
        self.update_key = ["house_title", "is_good_house", "price_total", "price_unit", "other", "bedroom",
                           "living_room", "house_size", "house_orientation", "have_elevator", "listing_time"]

    def json_to_object(self, _input):
        """ 将json 转换成对象 """
        if isinstance(_input, list):
            ret = []
            for i in _input:
                house = House()
                house.__dict__ = i
                ret.append(house)
            return ret
        elif isinstance(_input, dict):
            house = House()
            house.__dict__ = _input
            return house
        else:
            house = House()
            return house

    def object_to_json(self, _input):
        """ 将对象 转换成json """
        if isinstance(_input, list):
            ret = []
            for i in _input:
                if isinstance(i, House):
                    _json = i.__dict__
                    ret.append(_json)
            return ret
        elif isinstance(_input, House):
            ret = _input.__dict__
            return ret
        else:
            return {}
