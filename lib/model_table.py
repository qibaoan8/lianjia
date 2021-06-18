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


class XiaoQuModel(BaseModel):
    """
    小区表
    """

    def __init__(self):
        super(XiaoQuModel, self).__init__()
        self.table = "xiaoqu"

