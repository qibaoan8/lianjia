#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright (c) 2018 alibaba-inc. All Rights Reserved
# 

"""
File: house.py
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


class House():

    def __init__(self):
            # id
            self.id = 0
            # time
            self.create_time = datetime.datetime.now()
            # id
            self.xiaoqu_id = ""
            # 爬取批次
            self.update_batch = 0
            # id
            self.house_id = ""
            # 标题
            self.house_title = ""
            # 好房
            self.is_good_house = False
            # 总价
            self.price_total = 0
            # 单价
            self.price_unit = 0
            # 房屋户型
            self.bed_room = 1
            self.living_room = 1
            # 建筑面积
            self.house_size = 0.0
            # 房屋朝向
            self.house_orientation = ""
            # 配备电梯
            self.have_elevator = False
            # 挂牌时间
            self.listing_time = None
            # 其他
            self.other = {}

            # <li><span class="label">房屋户型</span>1室1厅1厨1卫</li>
            # <li><span class="label">所在楼层</span>高楼层 (共15层)</li>
            # <li><span class="label">建筑面积</span>67.8㎡</li>
            # <li><span class="label">户型结构</span>平层</li>
            # <li><span class="label">套内面积</span>暂无数据</li>
            # <li><span class="label">建筑类型</span>板楼</li>
            # <li><span class="label">房屋朝向</span>东 西</li>
            # <li><span class="label">建筑结构</span>钢混结构</li>
            # <li><span class="label">装修情况</span>精装</li>
            # <li><span class="label">梯户比例</span>两梯六户</li>
            # <li><span class="label">供暖方式</span>集中供暖</li>
            # <li><span class="label">配备电梯</span>有</li>

            # <li class=""><span class="label ">挂牌时间</span><span>2020-11-18</span></li>
            # <li class=""><span class="label ">交易权属</span><span>商品房</span></li>
            # <li class=""><span class="label ">上次交易</span><span>2017-08-10</span></li>
            # <li class=""><span class="label ">房屋用途</span><span>普通住宅</span></li>
            # <li class=""><span class="label ">房屋年限</span><span>满两年</span></li>
            # <li class=""><span class="label ">产权所属</span><span>非共有</span></li>
            # <li><span class="label">抵押信息</span><span title="无抵押">无抵押</span></li>
            # <li class=""><span class="label ">房本备件</span><span>已上传房本照片</span></li>


    def __str__(self):
        return json.dumps(self.__dict__, ensure_ascii=False, cls=DateEncoder)

